import asyncio
from typing import Generic, TypeVar, Optional

from app.config import config
from app.tool.base import BaseTool, ToolResult
_BROWSER_DESCRIPTION = """12132132"""
Context = TypeVar("Context")

class BrowserUseTool(BaseTool, Generic[Context]):#浏览器使用工具
    name: str = "browser_use"
    description: str = _BROWSER_DESCRIPTION
    parameters: dict = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": [
                    "go_to_url",
                    "click_element",
                    "input_text",
                    "scroll_down",
                    "scroll_up",
                    "scroll_to_text",
                    "send_keys",
                    "get_dropdown_options",
                    "select_dropdown_option",
                    "go_back",
                    "web_search",
                    "wait",
                    "extract_content",
                    "switch_tab",
                    "open_tab",
                    "close_tab",
                ],
                "description": "The browser action to perform",
            },
            "url": {
                "type": "string",
                "description": "URL for 'go_to_url' or 'open_tab' actions",
            },
            "index": {
                "type": "integer",
                "description": "Element index for 'click_element', 'input_text', 'get_dropdown_options', or 'select_dropdown_option' actions",
            },
            "text": {
                "type": "string",
                "description": "Text for 'input_text', 'scroll_to_text', or 'select_dropdown_option' actions",
            },
            "scroll_amount": {
                "type": "integer",
                "description": "Pixels to scroll (positive for down, negative for up) for 'scroll_down' or 'scroll_up' actions",
            },
            "tab_id": {
                "type": "integer",
                "description": "Tab ID for 'switch_tab' action",
            },
            "query": {
                "type": "string",
                "description": "Search query for 'web_search' action",
            },
            "goal": {
                "type": "string",
                "description": "Extraction goal for 'extract_content' action",
            },
            "keys": {
                "type": "string",
                "description": "Keys to send for 'send_keys' action",
            },
            "seconds": {
                "type": "integer",
                "description": "Seconds to wait for 'wait' action",
            },
        },
        "required": ["action"],
        "dependencies": {
            "go_to_url": ["url"],
            "click_element": ["index"],
            "input_text": ["index", "text"],
            "switch_tab": ["tab_id"],
            "open_tab": ["url"],
            "scroll_down": ["scroll_amount"],
            "scroll_up": ["scroll_amount"],
            "scroll_to_text": ["text"],
            "send_keys": ["keys"],
            "get_dropdown_options": ["index"],
            "select_dropdown_option": ["index", "text"],
            "go_back": [],
            "web_search": ["query"],
            "wait": ["seconds"],
            "extract_content": ["goal"],
        },
    }

    async def execute(
            self,
            action: str,
            url: Optional[str] = None,
            index: Optional[int] = None,
            text: Optional[str] = None,
            scroll_amount: Optional[int] = None,
            tab_id: Optional[int] = None,
            query: Optional[str] = None,
            goal: Optional[str] = None,
            keys: Optional[str] = None,
            seconds: Optional[int] = None,
            **kwargs,
    ) -> ToolResult:
        """
        执行指定的浏览器操作。
        参数:
            action[str]:要执行的浏览器操作
            url[int]：导航或新选项卡的url
            index[int]：点击或输入操作的元素索引
            text[str]：用于输入操作或搜索查询的文本
            scroll_amount[int]：用于滚动操作的像素
            tab_id[int]：switch_tab操作的选项卡id
            query[str]：谷歌搜索的搜索查询
            goal[str]：内容提取的提取目标
            keys[str]：用于发送键盘操作的按键
            seconds[int]：等待秒数
            **kwargs：附加参数
        返回值：ToolResult带有操作输出或错误
        """
        async with self.lock:
            try:
                context = await self._ensure_browser_initialized()
                #从配置中获取最大内容长度
                max_content_length = getattr(config.browser_config,"max_content_length", 2000)

                #导航操作
                if action == "go_to_url":
                    if not url:
                        return ToolResult(error="URL是go_to_url的必要参数")
                    page = await context.get_current_page()
                    await page.goto(url)
                    await page.wait_for_load_state()
                    return ToolResult(output=f"导航到{url}")

                elif action == "go_back":
                    await context.go_back()
                    return ToolResult(output="导航返回")

                elif action == "refresh":
                    await context.refresh_page()
                    return ToolResult(output="刷新当前页面")

                elif action == "web_search":
                    if not query:
                        return ToolResult(error="'web_search'操作需要查询")
                    search_results = await self.web_search_tool.execute(query)

                    if search_results:
                        #导航到第一个搜索结果
                        first_result = search_results[0]
                        if isinstance(first_result, dict) and "url" in first_result:
                            url_to_navigate = first_result["url"]
                        elif isinstance(first_result, str):
                            url_to_navigate = first_result
                        else:
                            return ToolResult(error=f"搜索结果格式无效：｛first_result｝")

                        page = await context.get_current_page()
                        await page.goto(url_to_navigate)
                        await page.wait_for_load_state()

                        return ToolResult(output=f"搜索字词 '{query}' 并 导航到第一个结果: {url_to_navigate}\n所有的结果:" + "\n".join([str(r) for r in search_results]))
                    else:
                        return ToolResult(error=f"未找到{query}的搜索结果")

                else:
                    return ToolResult(error=f"未知参数：{action}")
            except Exception as e:
                return ToolResult(error=f"浏览器参数’{action}'错误：{str(e)}")








