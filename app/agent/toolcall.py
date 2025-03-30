#工具调用模块
from app.agent.react import ReActAgent
from app.logger import logger

class ToolCallAgent(ReActAgent):#工具调用代理
    """用于处理具有增强抽象的工具/函数调用的基本代理类"""
    name: str = "工具调用"
    description: str = "可以执行工具调用的代理"

    SYSTEM_PROMPT = "你是一个可以调用工具的智能体。"
    NEXT_STEP_PROMPT = "如果你想停止调用工具，请用'terminate'工具/函数调用"
    async def think(self) -> bool:
        logger.info(f"智能体(工具调用)-执行动作：思考...")
