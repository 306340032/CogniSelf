import sys
from datetime import datetime

from loguru import logger as _logger
from app.config import PROJECT_ROOT
#打印   级别  =  信息
_print_level = "INFO"

def define_log_level(print_level="INFO",logfile_level="DEBUG",name: str = None):#定义日志级别
    """调整控制台和文件输出的日志级别。"""
    global _print_level
    _print_level = print_level

    current_data = datetime.now()#获取当前时间
    formatted_data = current_data.strftime("%Y-%m-%d %H:%M:%S")#格式化时间
    log_name = (
        f"{name}_{formatted_data}" if name else formatted_data
    )#日志文件名,如果name为空则使用当前时间作为日志文件名
    _logger.remove()#_logger.remove()清除之前的日志配置
    _logger.add(sys.stderr, level=print_level)#控制台输出日志级别,sys.stderr表示控制台输出,level表示日志级别
    #_logger.add(PROJECT_ROOT / f"logs/{log_name}.log", level=logfile_level)#将日志输出到文件,level表示日志级别,PROJECT_ROOT / f"logs/{log_name}.log"表示日志文件路径
    return _logger

logger = define_log_level()#调用define_log_level()函数,并将返回值赋给logger变量

if __name__ == '__main__':
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
