#tool_collection.py是工具集，主要用于存放一些工具类，比如数据库连接池、日志记录器、缓存、消息队列等。
from typing import Dict, Any, List

from app.exceptions import ToolError
from app.logger import logger
from app.tool import BaseTool
from app.tool.base import ToolResult, ToolFailure

class ToolCollection:#工具集类
    """工具集类"""
    logger.info(f"智能体(工具调用)-工具集功能-开始加载")
    class Config:
        arbitrary_types_allowed = True

    def __init__(self,*tools: BaseTool):
        logger.info(f"智能体(工具调用)-工具集功能-正在初始化...")
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    def __iter__(self):#迭代器
        logger.info(f"智能体(工具调用)-工具集功能-正在遍历所有工具")
        return iter(self.tools)

    def to_params(self) -> List[Dict[str, Any]]:
        return [tool.to_param() for tool in self.tools]

    async def execute(self, *, name:str, tool_input: Dict[str, Any]=None) -> ToolResult: # 执行
        logger.info(f"智能体(工具调用)-工具集功能-执行方法")
        tool = self.tool_map.get(name)
        if not tool:
            return ToolFailure(error=f"Tool {name} is invalid")
        try:
            result = await tool(**tool_input)
            return result
        except ToolError as e:
            return ToolFailure(error=e.message)

    async def execute_all(self) -> List[ToolResult]:
        """Execute all tools in the collection sequentially."""
        results = []
        for tool in self.tools:
            try:
                result = await tool()
                results.append(result)
            except ToolError as e:
                results.append(ToolFailure(error=e.message))
        return results

    def get_tool(self, name: str) -> BaseTool:
        return self.tool_map.get(name)

    def add_tool(self, tool: BaseTool):
        self.tools += (tool,)
        self.tool_map[tool.name] = tool
        return self

    def add_tools(self, *tools: BaseTool):
        for tool in tools:
            self.add_tool(tool)
        return self

