#浏览器模块
from app.agent.toolcall import ToolCallAgent


class BrowserAgent(ToolCallAgent):
    print("BrowserAgent(浏览器代理)正在运行")