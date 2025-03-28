import threading
import tomllib
from pathlib import Path   #导入Path类,用于获取项目根目录。
from typing import Dict, Optional, List
from urllib.request import proxy_bypass

from pydantic import BaseModel, Field


def get_project_root() -> Path:#获取项目根目录
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent#返回当前文件所在目录的上两级目录,__file__为当前文件路径，resolve()方法用于获取绝对路径，parent.parent为上两级目录。

PROJECT_ROOT = get_project_root()  #获取项目根目录
WORKSPACE_ROOT = PROJECT_ROOT/"workspace"#获取工作区目录

class LLMSettings(BaseModel):
    print("LLMSettings方法调用")
    model: str = Field(..., description="模型名称")
    base_url: str = Field(..., description="模型API地址")
    api_key: str = Field(..., description="模型API密钥")
    max_tokens: int = Field(4096, description="模型最大推理长度")
    max_input_tokens: Optional[int] = Field(None, description="模型最大输入长度")
    temperature: float = Field(1.0, description="模型生成的文本的随机性")
    api_type: str = Field(..., description="Azure,Openai, or Ollama")
    api_version: str = Field(..., description="模型API版本")
    print("LLMSettings方法调用结束")

class ProxySettings(BaseModel):
    server: str = Field(None,description="代理服务器地址")
    username: Optional[str] = Field(None, description="代理用户名")
    password: Optional[str] = Field(None, description="代理服务器密码")

class SearchSettings(BaseModel):
    engine: str = Field(default="Baidu",description="要使用的LMM搜索引擎")
    fallback_engines: List[str] = Field(default=lambda: ["Google", "Bing"],description="备用搜索引擎列表")
    retry_delay: int = Field(default=60,description="搜索失败后重试间隔，单位为秒")
    max_retries: int = Field(default=3,description="搜索失败后最大重试次数")

class BrowserSettings(BaseModel):
    headless: bool = Field(False, description="是否在隐藏模式下运行浏览器")
    disable_security: bool = Field(True, description="是否禁用浏览器安全功能")
    extra_chromium_args: list[str] = Field(default_factory=list, description="额外的浏览器参数")
    chrome_instance_path: Optional[str] = Field(None, description="指定浏览器实例路径")
    wss_url: Optional[str] = Field(None, description="指定WebSocket地址")
    cdp_url: Optional[str] = Field(None, description="通过CDP连接到浏览器")
    proxy: Optional[ProxySettings] = Field(None, description="代理配置")
    max_content_length: int = Field(2000, description="最大内容长度")

class SandboxSettings(BaseModel):#xss沙箱配置
    use_sandbox: bool = Field(False, description="是否使用沙箱")
    image: str = Field("python:3.12-slim",description="沙箱镜像")
    work_dir: str = Field("/workspace",description="沙箱工作目录")
    memory_limit: str = Field("512m",description="沙箱内存限制")
    cpu_limit: float = Field(1.0,description="沙箱CPU限制")
    timeout: int = Field(300,description="沙箱超时时间")
    network_enabled: bool = Field(False,description="是否允许网络访问")

class AppConfig(BaseModel):
    llm: Dict[str, LLMSettings]
    sandbox: Optional[SandboxSettings] = Field(
        None, description="Sandbox configuration"
    )
    browser_config: Optional[BrowserSettings] = Field(
        None, description="Browser configuration"
    )
    search_config: Optional[SearchSettings] = Field(
        None, description="Search configuration"
    )

    class Config:
        arbitrary_types_allowed = True

class Config:                     #Config代表配置类
    _instance = None             #私有变量，用于单例模式的实现，_instance为None，第一次调用Config()时，_instance为Config类的实例，后续调用Config()时，直接返回_instance。
    _lock = threading.Lock()     #私有变量，用于线程锁，用于保证线程安全，Lock()方法返回一个Lock对象，可以调用acquire()和release()方法来实现线程同步。
    _initialized = False         #私有变量，用于初始化标志，用于判断是否已经初始化过，避免重复初始化。

    def __new__(cls):                #__new__方法用于创建实例，返回实例对象。
        if cls._instance is None:    #如果_instance为None，说明还没有创建实例，需要加锁进行同步。
            with cls._lock:          #加锁
                if cls._instance is None:     #再次判断是否为None，避免多线程同时创建实例。
                    cls._instance = super().__new__(cls)  #调用父类的__new__方法创建实例。
        return cls._instance        #返回实例对象。

    def __init__(self):             #__init__方法用于初始化实例，在第一次调用Config()时，会调用__init__方法进行初始化。
        if not self._initialized:   #如果_initialized为False，说明还没有初始化过，需要进行初始化。
            with self._lock:         #加锁
                if not self._initialized:    #再次判断是否已经初始化过，避免重复初始化。
                    self._config = {}         #私有变量，用于保存配置信息。
                    self._load_initial_config() #加载初始配置。
                    self._initialized = True   #设置初始化标志为True。

    @staticmethod #静态方法，用于加载初始配置。@staticmethod装饰器用于修饰静态方法，不需要实例化对象即可调用。staticmethod用于定义不需要实例化的类方法。
    def _get_config_path() -> Path:  #静态方法，用于获取配置文件路径。
        root = PROJECT_ROOT      #获取项目根目录下的config目录。
        config_path = root / "config" / "config.toml"   #config.toml为配置文件名。
        if config_path.exists():  #.exists()方法用于判断文件是否存在。
            return config_path    #返回配置文件路径。
        example_path = root / "config" / "config.example.toml"  #example是示例。
        if example_path.exists():  #.exists()方法用于判断文件是否存在。
            return example_path   #返回示例配置文件路径。
        raise FileNotFoundError("配置文件不存在！")  #抛出异常，配置文件不存在。

    def _load_config(self) -> dict:  #加载配置。
        config_path = self._get_config_path()  #获取配置文件路径。
        with config_path.open("rb") as f:  #使用open()方法打开配置文件。rb表示以二进制读模式打开。 f为文件对象。
            return tomllib.load(f)  #使用tomllib.load()方法加载配置文件。tomllib是Python的TOML解析库,load()方法用于解析TOML格式的配置文件。

    def _load_initial_config(self):
        raw_config = self._load_config()
        base_llm = raw_config.get("llm", {})
        llm_overrides = {
            k: v for k, v in raw_config.get("llm", {}).items() if isinstance(v, dict)
        }

        default_settings = {
            "model": base_llm.get("model"),
            "base_url": base_llm.get("base_url"),
            "api_key": base_llm.get("api_key"),
            "max_tokens": base_llm.get("max_tokens", 4096),
            "max_input_tokens": base_llm.get("max_input_tokens"),
            "temperature": base_llm.get("temperature", 1.0),
            "api_type": base_llm.get("api_type", ""),
            "api_version": base_llm.get("api_version", ""),
        }

        # handle browser config.
        browser_config = raw_config.get("browser", {})
        browser_settings = None

        if browser_config:
            # handle proxy settings.
            proxy_config = browser_config.get("proxy", {})
            proxy_settings = None

            if proxy_config and proxy_config.get("server"):
                proxy_settings = ProxySettings(
                    **{
                        k: v
                        for k, v in proxy_config.items()
                        if k in ["server", "username", "password"] and v
                    }
                )

            # filter valid browser config parameters.
            valid_browser_params = {
                k: v
                for k, v in browser_config.items()
                if k in BrowserSettings.__annotations__ and v is not None
            }

            # if there is proxy settings, add it to the parameters.
            if proxy_settings:
                valid_browser_params["proxy"] = proxy_settings

            # only create BrowserSettings when there are valid parameters.
            if valid_browser_params:
                browser_settings = BrowserSettings(**valid_browser_params)

        search_config = raw_config.get("search", {})
        search_settings = None
        if search_config:
            search_settings = SearchSettings(**search_config)
        sandbox_config = raw_config.get("sandbox", {})
        if sandbox_config:
            sandbox_settings = SandboxSettings(**sandbox_config)
        else:
            sandbox_settings = SandboxSettings()

        config_dict = {
            "llm": {
                "default": default_settings,
                **{
                    name: {**default_settings, **override_config}
                    for name, override_config in llm_overrides.items()
                },
            },
            "sandbox": sandbox_settings,
            "browser_config": browser_settings,
            "search_config": search_settings,
        }

        self._config = AppConfig(**config_dict)

    @property#属性装饰器，用于定义只读属性。
    def llm(self) -> Dict[str,LLMSettings]:
        return self._config.llm  #返回配置信息中的llm部分。

config = Config()  #实例化Config类，config为Config类的实例。



