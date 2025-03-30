from app.logger import logger
from app.tool import BaseTool

_TERMINATE_DESCRIPTION = """Terminate the interaction when the request is met OR if the assistant cannot proceed further with the task.
When you have finished all the tasks, call this tool to end the work."""

class Terminate(BaseTool):#终止
    name: str = "terminate"
    description: str = _TERMINATE_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "The finish status of the interaction.",
                "enum": ["success", "failure"],
            }
        },
        "required": ["status"],
    }
    async def execute(self, status: str) -> str:
        """完成当前执行"""
        return f"交互完成。状态转变为:{status}"