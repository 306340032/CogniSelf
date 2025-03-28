#基础智能体类
from abc import ABC, abstractmethod
from typing import Optional #Optional用于定义可选参数
from app.llm import LLM  # LLM是语言模型的抽象基类
from pydantic import BaseModel, Field  # pydantic库的BaseModel类用于定义智能体的属性和方法，并提供数据校验和序列化功能。
class BaseAgent(BaseModel, ABC):
    """智能体的抽象基类，用于管理智能体的状态和执行。为状态转换、内存管理提供基础功能，以及基于步骤的执行循环。子类必须实现step方法。"""
    print("BaseAgent智能体基础正在运行")
    #核心属性
    name: str = Field(..., description="Agent的唯一名称")
    description: Optional[str] = Field(None, description="Agent的描述信息")

    #提示信息
    system_prompt: Optional[str] = Field(None, description="系统级别提示信息")
    next_step_prompt: Optional[str] = Field(None, description="下一步提示信息")
    #依赖性
    llm: LLM = Field(default_factory=LLM, description="智能体的语言模型实例")
    class Config:
        arbitrary_types_allowed = True  # 允许任意类型，包括自定义类型。
        extra = "allow"  # 允许额外的属性。
    print("BaseAgent智能体基础正在运行结束")