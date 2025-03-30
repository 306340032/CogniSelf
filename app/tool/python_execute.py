import multiprocessing
import sys
from io import StringIO
from typing import Dict
from app.logger import logger

from app.tool.base import BaseTool

class PythonExecute(BaseTool):    #执行python代码
    """一个用于安全执行Python代码机超时处理的工具。"""

    name: str = "执行python代码"
    description: str = "执行Python代码字符串。注意：只有打印输出可见，函数返回值不会被捕获。使用打印语句查看结果"
    parameters: dict = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "执行python代码.",
            },
        },
        "required": ["code"],
    }

    def _run_code(self, code: str, result_dict: dict, safe_globals: dict) -> None:
        original_stdout = sys.stdout
        try:
            output_buffer = StringIO()
            sys.stdout = output_buffer
            exec(code, safe_globals, safe_globals)
            result_dict["observation"] = output_buffer.getvalue()
            result_dict["success"] = True
        except Exception as e:
            result_dict["observation"] = str(e)
            result_dict["success"] = False
        finally:
            sys.stdout = original_stdout

    async def execute(
            self,
            code: str,
            timeout: int=5,
    ) -> Dict:
        """
        执行携带有Python代码及超时设置。

        参数：
        code（str）：要执行的python代码；
        timeout（int）：执行超时（秒）；

        返回：
        Dict(dict)：包含带有执行输出或错误消息和“成功”状态的“输出”
        """

        with multiprocessing.Manager() as manager:
            result = manager.dict({"observation":"","success":False})
            if isinstance(__builtins__, dict):
                safe_globals ={"__builtins__": __builtins__}
            else:
                safe_globals ={"__builtins__": __builtins__.__dict__.copy()}
            proc = multiprocessing.Process(
                target=self._run_code, args=(code,result,safe_globals)
            )
            proc.start()
            proc.join(timeout)

            #超时处理
            if proc.is_alive():
                proc.terminate()
                proc.join(1)
                return {
                    "observation": f"Execution timeout after {timeout} seconds",
                    "success": False,
                }
            return dict(result)