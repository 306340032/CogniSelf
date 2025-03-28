import threading
import tomllib
from pathlib import Path   #导入Path类,用于获取项目根目录。
from urllib.request import proxy_bypass


def get_project_root() -> Path:#获取项目根目录
    """获取项目根目录"""
    return Path(__file__).resolve().parent.parent#返回当前文件所在目录的上两级目录,__file__为当前文件路径，resolve()方法用于获取绝对路径，parent.parent为上两级目录。

PROJECT_ROOT = get_project_root()  #获取项目根目录
WORKSPACE_ROOT = PROJECT_ROOT/"workspace"#获取工作区目录

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
                    #self._load_initial_config() #加载初始配置。
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



if __name__ == '__main__':
    print("-----------")
    Config._get_app()



