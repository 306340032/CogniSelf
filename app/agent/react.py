#智能体框架ReActAgent
from abc import ABC, abstractmethod
from app.logger import logger
from app.agent.base import BaseAgent

class ReActAgent(BaseAgent, ABC):#继承自BaseAgent及ABC，ABC是抽象基类，BaseAgent是智能体的基类
    @abstractmethod
    async def think(self) -> bool:#定义think方法，返回bool值
        logger.info(f"智能体-执行动作：思考中...")
        logger.info(f"智能体-执行结果：思考结束，正在决定下一步动作...")

    async def step(self) -> str:
        logger.info(f"智能体-执行动作：准备思考")
        should_act = await self.think()
        if not should_act:
            return "思考结束，无需执行动作"
        return await self.act()#调用act方法，返回执行结果
