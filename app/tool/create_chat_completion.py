from typing import Any

from app.logger import logger
from app.tool import BaseTool


class CreateChatCompletion(BaseTool):
    name: str = "创建_聊天_完成"
    description: str = ("使用指定的输出格式创建结构化完成。")
    type_mapping: dict = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        dict: "object",
        list: "array",
    }
    async def execute(self, required: list | None = None, **kwargs) -> Any:  #执行
        return None
