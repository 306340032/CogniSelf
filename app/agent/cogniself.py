#CogniSelf模块
from pydantic import Field

from app.config import config
from app.agent.browser import BrowserAgent
from app.prompt.manus import NEXT_STEP_PROMPT, SYSTEM_PROMPT
from app.logger import logger
from app.tool import ToolCollection
from app.tool.browser_use_tool import BrowserUseTool
from app.tool.python_execute import PythonExecute
from app.prompt.browser import NEXT_STEP_PROMPT as BROWSER_NEXT_STEP_PROMPT


class CogniSelf(BrowserAgent):#CognSelf类继承自BrowserAgent类
    name: str = "CogniSelf"
    version: str = "0.1.0"
    description: str = "一个多功能代理，可以使用多种工具解决各种任务."

    system_prompt: str = SYSTEM_PROMPT.format(directory=config.workspace_root)
    next_step_prompt: str = NEXT_STEP_PROMPT

    max_observe: int = 10000
    max_steps: int = 20

    #将通用工具添加到工具集合中
    logger.info(f"智能体-CogniSelf工具集正在添加工具：")
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute()
        )
    )
    logger.info(f"智能体-CogniSelf工具集添加工具结束")

    async def think(self) -> bool:
        logger.info(f"智能体-CogniSelf正在执行思考：")
        original_prompt = self.next_step_prompt

        recent_messages = self.memory.messages[-3:] if self.memory.messages else []
        browser_in_use = any(
            "browser_use" in msg.content.lower()
            for msg in recent_messages
            if hasattr(msg,"content") and isinstance(msg.content, str)
        )

        if browser_in_use:
            self.next_step_prompt = BROWSER_NEXT_STEP_PROMPT

        result = await super().think()
        self.next_step_prompt = original_prompt
        return result



