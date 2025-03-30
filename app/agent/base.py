#基础智能体类
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import Optional, List  # Optional用于定义可选参数
from app.llm import LLM  # LLM是语言模型的抽象基类
from pydantic import BaseModel, Field, model_validator  # pydantic库的BaseModel类用于定义智能体的属性和方法，并提供数据校验和序列化功能。
from app.schema import AgentState, ROLE_TYPE, Memory, Message  # 导入AgentState、ROLE_TYPE、Memory类
from app.logger import logger

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
    memory: Memory = Field(default_factory=Memory, description="智能体的内存实例")
    state: AgentState = Field(default=AgentState.IDLE, description="智能体的当前状态")
    max_steps: int = Field(default=10, description="最大执行步骤数")
    current_step: int = Field(default=0, description="当前执行步骤数")

    class Config:
        arbitrary_types_allowed = True  # 允许任意类型，包括自定义类型。
        extra = "allow"  # 允许额外的属性。
    @asynccontextmanager
    async def state_context(self, new_state: AgentState) -> None:
        """状态上下文管理器，用于管理Agent的状态。"""
        if not isinstance(new_state, AgentState):
            raise ValueError(f"当前状态为{new_state}")
        previous_state = self.state
        self.state = new_state
        try:
            yield
        except Exception as e:
            self.state = AgentState.ERROR
            raise e
        finally:
            self.state = previous_state
    def update_memory(self,role: ROLE_TYPE,content: str,base64_image: Optional[str] = None,**kwargs,) -> None:
        #logger.info(f"(app-agent-base[update_memory])-角色类型：{role} 内容：{content} 图片Base64编码：{base64_image} 其他参数：{kwargs}")
        message_map = {
            "user": Message.user_message,
            "system": Message.system_message,
            "assistant": Message.assistant_message,
            "tool": lambda content, **kw: Message.tool_message(content, **kw),
        }
        if role not in message_map:
            raise ValueError(f"不支持的角色类型: {role}")

        kwargs = {"base64_image":base64_image,**(kwargs if role == "tool" else {})} ##**操作符用于将字典扩展为关键字参数
        self.memory.add_message(message_map[role](content, **kwargs))
    async def run(self, request: Optional[str]=None) -> str:
        """异步执行代理的主循环
        参数:
            request:可选的要处理的初始化用户请求
        返回值:
            总结执行结果的字符串
        增加：
            如果Agent启动未处于IDLE状态
        """
        logger.info(f"正在启动【CogniSelf】智能体...")
        if self.state!= AgentState.IDLE:
            logger.warning(f"Agent启动失败，当前状态为{self.state}")
            raise RuntimeError(f"无法启动Agent，当前状态为{self.state}")
        if request:
            self.update_memory("user",request)   # 向Agent的内存中添加初始请求信息

        results: List[str] = []
        async with self.state_context(AgentState.RUNNING):#异步上下文管理器，用于管理Agent的状态
            while self.current_step < self.max_steps and self.state != AgentState.FINISHED:
                self.current_step += 1
                logger.info(f"智能体-当前步骤：{self.current_step}/{self.max_steps}")
                step_result = await self.step()  # 执行智能体的step方法
                logger.info(f"智能体-执行结果：{step_result}")
                # 卡住状态检查
                #if self.is_stuck():
                #    self.handle_stuck_state()
                #results.append(f"步骤{self.current_step}执行结果：{step_result}")  # 记录执行结果

    @abstractmethod
    async def step(self) -> str:
        """执行智能体的单步操作。子类必须实现此方法。"""
        logger.info(f"执行智能体的单步操作...")

    def handle_stuck_state(self):
        """处理卡住状态。"""
        logger.info(f"智能体卡住，进入错误状态...")
        stuck_prompt = "\监视到重复响应。考虑新的部署及避免重复已尝试无效路径"
        logger.warning(f"智能体检测到卡住状态。添加提示：{stuck_prompt}")

    def is_stuck(self) -> bool:
        """检查智能体是否卡住。"""
        if len(self.memory.messages) < 2:
            return False