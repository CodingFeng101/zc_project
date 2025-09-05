import logging
import os
import sys
import inspect
from typing import Optional

from agents_system.config.settings import settings

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class AgentLogger:
    """统一的日志模块，包含模块名、行号、时间戳等属性"""
    
    def __init__(self, name: str, log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, settings.LOG_LEVEL))
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建日志格式，包含时间戳、模块名等信息
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(location_info)s - %(message)s'
            )
            
            # 控制台处理器
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 文件处理器
            if log_file or settings.LOG_FILE:
                log_path = log_file or settings.LOG_FILE
                if log_path:
                    # 确保日志目录存在
                    log_dir = os.path.dirname(log_path)
                    if log_dir and not os.path.exists(log_dir):
                        os.makedirs(log_dir)
                    
                    file_handler = logging.FileHandler(log_path, encoding='utf-8')
                    file_handler.setFormatter(formatter)
                    self.logger.addHandler(file_handler)
    
    def _log_with_caller_info(self, level: int, message: str):
        """记录带有调用者信息的日志"""
        try:
            # 获取调用栈信息
            stack = inspect.stack()
            # 跳过当前函数和日志方法调用帧，获取实际调用者信息
            if len(stack) > 2:
                caller_frame = stack[2]
                filename = os.path.basename(caller_frame.filename)
                lineno = caller_frame.lineno
                func_name = caller_frame.function
                
                # 格式化位置信息
                location_info = f"{filename}:{func_name}:{lineno}"
                formatted_message = message
            else:
                # 如果无法获取调用栈信息，使用默认格式
                location_info = "unknown:unknown:0"
                formatted_message = message
            
            # 创建并处理日志记录，使用完整的参数列表消除编辑器警告
            record = self.logger.makeRecord(
                self.logger.name,     # name
                level,                # level
                filename,             # fn (filename)
                lineno,               # lno (line number)
                message,              # msg
                (),                   # args (empty tuple for no args)
                None,                 # exc_info
                func_name,            # func
                None,                 # extra
                None                  # sinfo
            )
            # 添加自定义的位置信息字段
            record.location_info = location_info
            self.logger.handle(record)
        except Exception as e:
            # 如果获取调用栈信息失败，回退到基本日志记录
            self.logger.log(level, message)
    
    def debug(self, message: str):
        self._log_with_caller_info(logging.DEBUG, message)
    
    def info(self, message: str):
        self._log_with_caller_info(logging.INFO, message)
    
    def warning(self, message: str):
        self._log_with_caller_info(logging.WARNING, message)
    
    def error(self, message: str):
        self._log_with_caller_info(logging.ERROR, message)
    
    def critical(self, message: str):
        self._log_with_caller_info(logging.CRITICAL, message)


def get_logger(name: str) -> AgentLogger:
    """获取日志记录器的工厂方法"""
    return AgentLogger(name)