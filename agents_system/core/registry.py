import sys
import os
from typing import Dict, Type, Any, Optional
from fastapi import APIRouter

from agents_system.utils.logger import get_logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = get_logger(__name__)


class AgentRegistry:
    """智能体注册表"""
    
    def __init__(self):
        self._agents: Dict[str, Type] = {}
        self._agent_instances: Dict[str, Any] = {}
        self._router = APIRouter(prefix="/agents")
        logger.info("Initialized AgentRegistry")
    
    def register(self, name: str, agent_class: Type):
        """
        注册一个新的智能体
        
        Args:
            name: 智能体名称
            agent_class: 智能体类
        """
        if name in self._agents:
            logger.warning(f"Agent {name} is already registered, overwriting...")
        
        self._agents[name] = agent_class
        logger.info(f"Registered agent: {name}")
    
    def unregister(self, name: str):
        """
        取消注册一个智能体
        
        Args:
            name: 智能体名称
        """
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered agent: {name}")
        
        if name in self._agent_instances:
            del self._agent_instances[name]
    
    def get_agent_class(self, name: str) -> Optional[Type]:
        """
        获取智能体类
        
        Args:
            name: 智能体名称
            
        Returns:
            智能体类或None
        """
        return self._agents.get(name)
    
    def get_agent_instance(self, name: str, *args, **kwargs) -> Any:
        """
        获取智能体实例（单例模式）
        
        Args:
            name: 智能体名称
            *args: 实例化参数
            **kwargs: 实例化关键字参数
            
        Returns:
            智能体实例
        """
        if name not in self._agent_instances:
            agent_class = self._agents.get(name)
            if agent_class is None:
                logger.error(f"Agent {name} not found in registry")
                raise ValueError(f"Agent {name} not found in registry")
            
            self._agent_instances[name] = agent_class(*args, **kwargs)
            logger.info(f"Created instance for agent: {name}")
        
        return self._agent_instances[name]
    
    def list_agents(self) -> Dict[str, str]:
        """
        列出所有已注册的智能体
        
        Returns:
            智能体名称和类名的映射
        """
        return {name: cls.__name__ for name, cls in self._agents.items()}
    
    @property
    def router(self) -> APIRouter:
        """获取API路由"""
        return self._router


# 全局注册表实例
registry = AgentRegistry()