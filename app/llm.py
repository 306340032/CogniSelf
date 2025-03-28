import tiktoken
from typing import Dict, Optional
from openai import OpenAI, AsyncOpenAI
from app.config import config,LLMSettings
class TokenCounter:
    print("TokenCounter类被调用")
    BASE_MESSAGE_TOKENS = 4
    FORMAT_TOKENS = 2
    LOW_DETAIL_IMAGE_TOKENS = 85
    HIGH_DETAIL_IMAGE_TOKENS = 170

    MAX_TOKENS = 2048
    HIGH_DETAIL_TARGET_SHORT_SIDE = 768
    TILE_SIZE = 512

    def __init__(self, tokenizer):
        print("TokenCounter实例被创建")
        self.tokenizer = tokenizer
        print(f"TokenCounter实例被创建:{tokenizer}")

    def count_text(self, text: str) -> int:
        #计算文本的token数量
        return 0 if not text else len(self.tokenizer.encode(text))
class LLM:
    print("LLM类被调用")
    _instances: Dict[str, "LLM"] = {}#私有实例
    def __new__(cls, config_name: str = "default", llm_config: Optional[LLMSettings]=None):#用于创建实例的特殊方法，在__init__之前调用
        print("LLM实例__new__方法被调用")
        if config_name not in cls._instances:
            instance = super().__new__(cls)
            instance.__init__(config_name, llm_config)
            cls._instances[config_name] = instance
        return cls._instances[config_name]

    def __init__(self, config_name: str = "default", llm_config: Optional[LLMSettings]=None):
        print("LLM实例__init__方法被调用")
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
        print("LLM实例__init__方法被调用结束")
    pass
