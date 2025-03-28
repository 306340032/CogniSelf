#CogniSelf模块
from app.agent.browser import BrowserAgent


class CogniSelf(BrowserAgent):#CognSelf类继承自BrowserAgent类
    name: str = "CogniSelf"
    version: str = "0.1.0"
    description: str = "一个多功能代理，可以使用多种工具解决各种任务."
    print("CogniSelf类正在运行...，父类：BrowserAgent")


