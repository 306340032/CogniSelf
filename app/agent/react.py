#智能体框架ReActAgent
from abc import ABC, abstractmethod

from app.agent.base import BaseAgent

class ReActAgent(BaseAgent, ABC):#继承自BaseAgent及ABC，ABC是抽象基类，BaseAgent是智能体的基类
    print("ReActAgent智能体框架正在运行，父类：BaseAgent")