class WebSearchEngine:#WEB搜索引擎基类
    def perform_search(self, query: str, num_results: int = 10, *args, **kwargs) -> list[dict]:
        """
        进行搜索，返回搜索结果列表
        参数：
            query: 搜索关键字
            num_results: 搜索结果数量
        返回值：
            搜索结果列表，每个元素为一个字典，包含以下字段：
        """
        raise NotImplementedError

