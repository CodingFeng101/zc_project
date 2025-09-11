#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, List, Dict
from pydantic import BaseModel
from fastapi import APIRouter
from jinja2 import Template

from agents_system.core.base_agent import BaseAgent
from agents_system.models.doubao import DoubaoModel, logger


class DispatchRequest(BaseModel):
    """
    对话统筹与路由判断请求模型
    
    :param conversations: 聊天历史记录
    """
    conversations: List[Dict[str, str]]


class DispatchResponse(BaseModel):
    """
    对话统筹与路由判断响应模型

    :param route_code: 路由判断结果，1或2
    :param success: 处理是否成功
    :param message: 处理结果消息
    """
    route_code: str
    success: bool
    message: str


class DispatchAgent(BaseAgent):
    """对话统筹与路由判断智能体"""

    def __init__(self):
        super().__init__(name="DispatchAgent")
        self.name = "对话统筹与路由判断智能体"
        self.description = "负责依据对话上下文和当前博主消息，精准输出单个三位码用于路由"
        self.doubao_client = DoubaoModel()
        # self._setup_routes()

    def _setup_routes(self) -> None:
        """设置路由"""
        router = APIRouter(prefix=f"/{self.__class__.__name__.lower().replace('agent', '')}")
        router.post("/dispatch", response_model=DispatchResponse)(self.dispatch_route)
        self.router = router

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        处理对话统筹与路由判断

        :param data: 包含聊天历史和当前输入的数据
        :return: 路由判断结果
        """
        try:
            conversations = data.get("conversations", [])
            user_input = next((m.get('content') for m in reversed(conversations) if m.get('role') == "user"), "")

            # 构建提示词
            prompt = self._build_prompt(conversations, user_input)

            # 调用大模型进行路由判断
            response = await self.doubao_client.generate_text(prompt)

            # 提取路由码
            route_code = self._extract_route_code(response)

            logger.info(f"路由判断完成, 路由码: {route_code}")

            return {
                "route_code": route_code,
                "success": True,
                "message": "路由判断成功"
            }

        except Exception as e:
            logger.error(f"路由判断失败: {str(e)}")
            return {
                "route_code": "2",  # 默认路由到咨询阶段
                "success": False,
                "message": f"路由判断失败: {str(e)}"
            }

    def _build_prompt(self, conversations: List, user_input: str) -> str | None:
        """
        构建路由判断提示词

        :param conversations: 聊天历史记录
        :return: 构建的提示词
        """
        try:
            # 读取 prompt 模板文件
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_file = os.path.join(current_dir, "dispatch.txt")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = Template(f.read())
            # 替换模板中的占位符

            prompt = prompt_template.render(
                conversations=conversations,
                user_input=user_input
            )
            print("prompt:", prompt)
            
            return prompt
            
        except Exception as e:
            logger.error(f"读取 dispatch.txt 文件失败: {str(e)}")

    def _extract_route_code(self, response: str) -> str:
        """
        从模型响应中提取路由码

        :param response: 模型响应
        :return: 路由码（1或2）
        """
        # 清理响应，只保留数字
        cleaned_response = response.strip()

        # 提取第一个数字字符
        for char in cleaned_response:
            if char in ['1', '2', '3']:
                return char

        # 如果没有找到有效路由码，默认返回2
        return "3"

    async def dispatch_route(self, request: DispatchRequest) -> DispatchResponse:
        """
        路由判断接口

        :param request: 路由判断请求
        :return: 路由判断响应
        """
        try:
            result = await self.process({"conversations": request.conversations})
            
            return DispatchResponse(
                route_code=result["route_code"],
                success=result["success"],
                message=result["message"]
            )
            
        except Exception as e:
            logger.error(f"路由判断接口调用失败: {str(e)}")
            return DispatchResponse(
                route_code="2",
                success=False,
                message=f"路由判断失败: {str(e)}"
            )
