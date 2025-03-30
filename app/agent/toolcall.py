#工具调用模块
from typing import List, Optional, Union

from pydantic import Field

from app.agent.react import ReActAgent
from app.logger import logger
from app.schema import TOOL_CHOICE_TYPE, ToolChoice, ToolCall, Message
from app.tool import ToolCollection, CreateChatCompletion, Terminate


class ToolCallAgent(ReActAgent):#工具调用代理
    """用于处理具有增强抽象的工具/函数调用的基本代理类"""
    name: str = "工具调用"
    description: str = "可以执行工具调用的代理"

    system_prompt: str = "你是一个可以调用工具的智能体。"
    next_step_prompt: str = "如果你想停止调用工具，请用'terminate'工具/函数"
    #可用工具
    available_tools: ToolCollection = ToolCollection(CreateChatCompletion(), Terminate())
    tool_choices: TOOL_CHOICE_TYPE = ToolChoice.AUTO
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    tool_calls: List[ToolCall] = Field(default_factory=list)
    _current_base64_image: Optional[str] = None

    max_steps: int = 30
    max_observe: Optional[Union[int, bool]] = None

    async def think(self) -> bool:
        logger.info(f"智能体(工具调用)-执行动作：思考...")
        if self.next_step_prompt:
            user_msg = Message.user_message(self.next_step_prompt)
            self.messages += [user_msg]
        try:
            response = await self.llm.ask_tool(
                messages=self.messages,
                system_msgs=(
                    [Message.system_message(self.system_prompt)]
                    if self.system_prompt
                    else None
                ),
                tools=self.available_tools.to_params(),
                tool_choice=self.tool_choices,
            )
        except ValueError:
            raise
        except Exception as e:
            logger.info(f"智能体(工具调用)-发生错误：{e}")#####未完待续



