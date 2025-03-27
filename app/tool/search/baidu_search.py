from baidusearch.baidusearch import search
# baidusearch库中封装了百度搜索的API，可以直接调用;其中search()函数可以搜索指定关键字的相关网页
from app.tool.search.base import WebSearchEngine
# 导入WebSearchEngine类，用于搜索引擎的基类

class BaiduSearchEngine(WebSearchEngine):
    def perform_search(self, query: str, num_results: int = 10, *args, **kwargs):
        """百度搜索引擎"""
        return search(query, num_results=num_results)
