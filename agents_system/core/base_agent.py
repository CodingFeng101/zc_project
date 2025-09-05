import sys
import os
from abc import ABC, abstractmethod
from typing import Any, Dict
from fastapi import APIRouter

from agents_system.utils.logger import get_logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



class BaseAgent(ABC):
    """所有智能体的基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"agent.{name}")
        self.router = APIRouter(prefix=f"/{name}")
        self._setup_routes()
        self.logger.info(f"Initialized agent: {name}")
    
    def _setup_routes(self):
        """设置默认路由"""
        self.router.get("/info", response_model=Dict[str, Any])(self.info)
    
    async def info(self) -> Dict[str, Any]:
        """获取智能体信息"""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "description": self.__doc__
        }
    
    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """
        处理输入数据的核心方法，需要在子类中实现
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        pass