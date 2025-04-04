import math

import tiktoken
from typing import Dict, Optional, List, Union
from openai import OpenAI, AsyncOpenAI, OpenAIError
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

from app.logger import logger
from app.config import config,LLMSettings
from app.schema import Message, ToolChoice, TOOL_CHOICE_TYPE, TOOL_CHOICE_VALUES

REASONING_MODELS=["R1"]#推理模型
MULTIMODAL_MODELS=["Align-DS-V"]#多模态模型
class TokenCounter:
    BASE_MESSAGE_TOKENS = 4
    FORMAT_TOKENS = 2
    LOW_DETAIL_IMAGE_TOKENS = 85
    HIGH_DETAIL_TILE_TOKENS = 170

    MAX_SIZE = 2048
    HIGH_DETAIL_TARGET_SHORT_SIDE = 768
    TILE_SIZE = 512

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

    def count_text(self, text: str) -> int:
        #计算文本的token数量
        return 0 if not text else len(self.tokenizer.encode(text))

    def count_image(self,image_item: dict) -> int:
        #计算图像的token数量
        detail = image_item.get("detail", "medium")#图像细节级别,detail为"high"或"low",medium为默认值,detail译为"高"或"低"，medium译为"中"
        if detail == "low":
            return self.LOW_DETAIL_IMAGE_TOKENS   #低细节图像的token数量
        if detail == "high" or detail == "medium":
            if "dimensions"in image_item:
                width, height = image_item["dimensions"]
                return self._calculate_high_detail_tokens(width,height)#计算高细节图像的token数量
        if detail == "high":
            return self._calculate_high_detail_tokens(1024,1024)
        elif detail == "medium":
            return 1024
        else:
            return 1024
    def _calculate_high_detail_tokens(self, width: int, height: int) -> int:
        """Calculate tokens for high detail images based on dimensions"""
        # Step 1: Scale to fit in MAX_SIZE x MAX_SIZE square
        if width > self.MAX_SIZE or height > self.MAX_SIZE:
            scale = self.MAX_SIZE / max(width, height)
            width = int(width * scale)
            height = int(height * scale)

        # Step 2: Scale so shortest side is HIGH_DETAIL_TARGET_SHORT_SIDE
        scale = self.HIGH_DETAIL_TARGET_SHORT_SIDE / min(width, height)
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)

        # Step 3: Count number of 512px tiles
        tiles_x = math.ceil(scaled_width / self.TILE_SIZE)
        tiles_y = math.ceil(scaled_height / self.TILE_SIZE)
        total_tiles = tiles_x * tiles_y

        # Step 4: Calculate final token count
        return (
                total_tiles * self.HIGH_DETAIL_TILE_TOKENS
        ) + self.LOW_DETAIL_IMAGE_TOKENS

    def count_content(self, content: Union[str, List[Union[str, dict]]]) -> int:
        if not content:
            return 0
        if isinstance(content, str):
            return self.count_text(content)

        token_count = 0
        for item in content:
            if isinstance(item, str):
                token_count += self.count_text(item)
            elif isinstance(item, dict):
                if "text" in item:
                    token_count += self.count_text(item["text"])
                elif "image_url" in item:
                    token_count += self.count_image(item)
        return token_count
    def count_tool_call(self,tool_calls: List[dict]) -> int:
        token_count = 0
        for tool_call in tool_calls:
            if "function" in tool_call:
                function = tool_call["function"]
                token_count += self.count_text(function.get("name",""))
                token_count += self.count_text(function.get("arguments",""))
        return token_count


    def count_messages_tokens(self, messages: List[dict]) -> int:
        #计算消息的token数量
        total_tokens = self.FORMAT_TOKENS #格式化token
        for message in messages:
            tokens = self.BASE_MESSAGE_TOKENS #基础消息token

            tokens += self.count_text(message.get("role", "")) #消息内容token

            if "content" in message:
                tokens += self.count_conten(message["content"])
class LLM:
    _instances: Dict[str, "LLM"] = {}#私有实例
    def __new__(cls, config_name: str = "default", llm_config: Optional[LLMSettings]=None):#用于创建实例的特殊方法，在__init__之前调用
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance
        return cls._instances[config_name]

    def __init__(self, config_name: str = "default", llm_config: Optional[LLMSettings]=None):
        if not hasattr(self, "client"):#判断是否已经初始化过,hasattr()方法用于判断对象是否包含对应的属性
            llm_config = llm_config or config.llm
            llm_config = llm_config.get(config_name, llm_config["default"])
            self.model = llm_config.model
            self.max_tokens = llm_config.max_tokens
            self.temperature = llm_config.temperature
            self.api_type = llm_config.api_type
            self.api_key = llm_config.api_key
            self.api_version = llm_config.api_version
            self.base_url = llm_config.base_url

            self.total_input_tokens = 0
            self.total_output_tokens = 0
            self.max_input_tokens = (llm_config.max_input_tokens if hasattr(llm_config, "max_input_tokens") else None)
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model)
            except KeyError:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
            self.tokens_counter = TokenCounter(self.tokenizer)

    def check_token_limit(self,input_tokens:int) -> bool:
        if self.max_input_tokens is not None:
            return (self.total_input_tokens + input_tokens) <= self.max_input_tokens
        return True

    @staticmethod
    def format_messages(messages: List[Union[dict, Message]],supports_images: bool = False) -> List[dict]:
        formatted_messages =[]

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(
            (OpenAIError, Exception, ValueError)
        ),  # Don't retry TokenLimitExceeded
    )
    async def ask_tool(
        self,
        messages: List[Union[dict, Message]],
        system_msgs: Optional[List[Union[dict, Message]]] = None,
        timeout: int = 300,
        tools: Optional[List[dict]] = None,
        tool_choice: TOOL_CHOICE_TYPE = ToolChoice.AUTO,  # type: ignore
        temperature: Optional[float] = None,
        **kwargs,
    ) -> ChatCompletionMessage | None:
        """
        使用函数 / 工具向大语言模型（LLM）提问并返回响应。
        参数：
        messages：对话消息列表
        system_msgs：可选的系统消息，将添加在开头
        timeout：请求超时时间（以秒为单位）
        tools：要使用的工具列表
        tool_choice：工具选择策略
        temperature：响应的采样温度
        **kwargs：其他完成请求的参数
        返回值：
        ChatCompletionMessage：模型的响应
        可能引发的异常：
        TokenLimitExceeded：如果超过了令牌限制
        ValueError：如果工具、工具选择或消息无效
        OpenAIError：如果在重试后 API 调用仍失败
        Exception：对于意外错误
        """
        try:
            #验证工具选择
            logger.info(f"智能体(工具调用)-执行操作：验证工具选择")
            if tool_choice not in TOOL_CHOICE_VALUES:
                raise ValueError(f"无效的工具选择: {tool_choice}")

            logger.info(f"智能体(工具调用)-执行操作：检查该模型是否支持图像")
            #检查该模型是否支持图像
            supports_images = self.model in MULTIMODAL_MODELS

            #格式化消息
            logger.info(f"智能体(工具调用)-执行操作：格式化消息")
            if  system_msgs:
                logger.info(f"智能体(工具调用)-执行操作：添加系统消息")
                system_msgs = self.format_messages(system_msgs, supports_images)
                messages = system_msgs + self.format_messages(messages, supports_images)
            else:
                logger.info(f"智能体(工具调用)-执行操作：没有系统消息")

            input_tokens = self.count_messages_tokens(messages)



        except Exception as e:
            logger.exception(f"智能体(工具调用)-执行操作：验证工具选择失败，原因：{e}")
            raise e





