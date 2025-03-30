from abc import ABC, abstractmethod
from typing import Optional, Any, Dict

# abc库提供抽象基类ABC，abstractmethod装饰器用来定义抽象方法。ABC类是抽象基类，不能实例化，只能作为基类被继承。abstractmethod装饰器用来定义抽象方法，被abstractmethod修饰的方法不能在类的实例化时调用，只能在子类中实现。
from pydantic import BaseModel, Field


# pydantic库提供数据验证功能，BaseModel类是数据模型的基类，用来定义数据模型。

class BaseTool(ABC, BaseModel):# 继承ABC和BaseModel类, 定义抽象基类BaseTool,Base意思是基类，Tool意思是工具。
    name: str # 定义一个字符串类型的属性name
    description: str # 定义一个字符串类型的属性description
    parameters: Optional[dict] = None # 定义一个字典类型的属性parameters，用来保存运行参数

    class Config:
        arbitrary_types_allowed = True # 允许任意类型,types意思是类型，allowed意思是允许，arbitrary意思是任意。

    async def __call__(self, **kwargs) -> Any: #Any是任意类型
        """定义抽象方法__call__，用来执行工具的功能。"""
        return await self.execute(**kwargs)

    @abstractmethod
    async def execute(self, **kwargs) -> Any:  #Any是任意类型
        """定义抽象方法execute，用来执行工具的功能。"""

    def to_param(self) -> Dict:  #Dict是字典类型 to_params意思是转换为参数
        """将工具的属性转换为字典类型，用于保存运行参数。"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

class ToolResult(BaseModel):  # 定义工具运行结果的模型类
    output: Any = Field(default=None) # 定义一个任意类型的属性output，默认值为None,Field方法用来定义属性的类型和默认值。
    error: Optional[str] = Field(default=None) # 定义一个可选字符串类型的属性error，默认值为None。Field方法用来定义属性的类型和默认值。
    base64_image: Optional[str] = Field(default=None) # 定义一个可选字符串类型的属性base64_image，默认值为None。Field方法用来定义属性的类型和默认值。
    system: Optional[str] = Field(default=None) # 定义一个可选字符串类型的属性system，默认值为None。Field方法用来定义属性的类型和默认值。

    class Config:
        arbitrary_types_allowed = True # 允许任意类型

    def __bool__(self): # 定义__bool__方法，用于判断工具运行结果是否成功。
        return any(getattr(self, field) for field in self.__fields__)
        # getattr(self, field)返回self的field属性的值。any()函数用于判断是否有成功的运行结果。getattr()函数用于获取属性值。

    def __add__(self, other): # 定义__add__方法，用于合并工具运行结果。
        def combine_field(field: Optional[str], other_field: Optional[str], concatenate: bool = True):
            if field and other_field:
                if concatenate:
                    return field + other_field
                raise ValueError("Cannot combine tool results.")
            return field or other_field

        return ToolResult(
            output=combine_field(self.output, other.output),
            error=combine_field(self.error, other.error),
            base64_image=combine_field(self.base64_image, other.base64_image, False),
            system=combine_field(self.system, other.system),
                )
        # combine_field函数用于合并工具运行结果的属性。
    def __str__(self): # 定义__str__方法，用于打印工具运行结果。
        return f"Error:{self.error}" if self.error else self.output
        # f-string格式化字符串，{self.error}表示输出error属性的值，{self.output}表示输出output属性的值。

    def replace(self, **kwargs): # 定义replace方法，用于替换工具运行结果的属性。
        return type(self)(**{**self.dict(), **kwargs})

class CLIResult(ToolResult):
    """A ToolResult that can be rendered as a CLI output."""

class ToolFailure(ToolResult):
    """表示失败的工具结果"""