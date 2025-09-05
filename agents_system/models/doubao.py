import json
import httpx
import sys
import os
from typing import Optional, Dict, Any, AsyncGenerator

from agents_system.config.settings import settings
from agents_system.utils.logger import get_logger

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = get_logger(__name__)


class DoubaoModel:
    """豆包大模型调用接口"""
    
    def __init__(self):
        self.api_key = settings.DOUBAO_API_KEY
        self.model_name = settings.DOUBAO_MODEL_NAME
        self.client = httpx.AsyncClient()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        logger.info(f"Initialized DoubaoModel with model: {self.model_name}")
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 其他参数
            
        Returns:
            生成的文本
        """
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        try:
            logger.info(f"Calling Doubao model with prompt: {prompt[:50]}...")
            response = await self.client.post(url, headers=self.headers, json=payload, timeout=60.0)
            response.raise_for_status()
            
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            logger.info("Successfully generated text with Doubao model")
            
            return generated_text
        except Exception as e:
            logger.error(f"Error calling Doubao model: {str(e)}")
            raise
    
    async def generate_text_stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        流式生成文本
        
        Args:
            prompt: 输入提示
            **kwargs: 其他参数
            
        Yields:
            生成的文本片段
        """
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        try:
            logger.info(f"Calling Doubao model stream with prompt: {prompt[:50]}...")
            async with self.client.stream("POST", url, headers=self.headers, json=payload, timeout=30.0) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk.startswith("data:"):
                        data = chunk[5:].strip()
                        if data != "[DONE]":
                            try:
                                result = json.loads(data)
                                if "choices" in result and len(result["choices"]) > 0:
                                    content = result["choices"][0]["delta"]["content"]
                                    if content:
                                        yield content
                            except Exception as e:
                                logger.warning(f"Error parsing stream data: {e}")
                                continue
            logger.info("Successfully streamed text with Doubao model")
        except Exception as e:
            logger.error(f"Error calling Doubao model stream: {str(e)}")
            raise
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


# 全局模型实例
doubao_model: Optional[DoubaoModel] = None


def get_doubao_model() -> DoubaoModel:
    """获取豆包模型实例"""
    global doubao_model
    if doubao_model is None:
        doubao_model = DoubaoModel()
    return doubao_model


async def call_doubao(prompt: str, **kwargs) -> str:
    """
    调用豆包模型生成文本（便捷函数）
    
    Args:
        prompt: 输入提示
        **kwargs: 其他参数
        
    Returns:
        生成的文本
    """
    model = get_doubao_model()
    return await model.generate_text(prompt, **kwargs)


async def call_doubao_stream(prompt: str, **kwargs) -> AsyncGenerator[str, None]:
    """
    流式调用豆包模型生成文本（便捷函数）
    
    Args:
        prompt: 输入提示
        **kwargs: 其他参数
        
    Yields:
        生成的文本片段
    """
    model = get_doubao_model()
    async for chunk in model.generate_text_stream(prompt, **kwargs):
        yield chunk