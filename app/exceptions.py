#例外
class ToolError(Exception):
    """当工具遇到错误是引发"""
    def __init__(self, message):
        self.message = message