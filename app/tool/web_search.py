from app.tool.base import BaseTool
from app.tool.search import WebSearchEngine, BaiduSearchEngine


class WebSearch(BaseTool):# 继承BaseTool类，定义网络搜索类WebSearch。
    name = "网络搜索"
    description = """执行网络搜索并返回相关链接的列表。尝试使用主要搜索引擎API获取最新结果。意思是如果发生错误，则回退到备用搜索引擎。"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "(必填)提交给搜索引擎的搜索查询"},
            "num_results": {"type": "integer", "description": "（可选）要返回的搜索结果数。默认值为10","default":10}
        },
        "required": ["query"],
    }
    _search_engine:dict[str, WebSearchEngine] ={
        "baidu": BaiduSearchEngine()
    }# 定义搜索引擎列表

    async def execute(self, query: str, num_results: int = 10) -> list[dict]:#execute方法，执行网络搜索并返回相关链接的列表。
        """
        执行Web搜索并返回URL列表。
        根据配置按顺序尝试引擎，如果引擎出现故障并出现错误，则回退。
        如果所有引擎都失败，它将等待并重试配置的次数。
        参数：
            query: (必填)提交给搜索引擎的搜索查询
            num_results: (可选)要返回的搜索结果数。默认值为10
        返回：
            一个URL列表，包含搜索结果。
        """
        # Get retry settings from config意思是从配置文件中获取重试设置。
        retry_delay = 60 # 重试延迟，单位为秒
        max_retries = 3 # 最大重试次数

