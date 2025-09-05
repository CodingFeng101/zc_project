#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, List, Dict
from pydantic import BaseModel
from fastapi import APIRouter
from jinja2 import Template
from agents_system.core.base_agent import BaseAgent
from agents_system.models.doubao import DoubaoModel, logger


class FillRequest(BaseModel):
    """
    选号需求填写请求模型
    
    :param conversations: 聊天历史记录
    :param form: 当前表单状态
    """
    conversations: List[Dict[str, str]]
    form: str = ""


class FillResponse(BaseModel):
    """
    选号需求填写响应模型
    
    :param response: 智能体回复内容
    :param success: 处理是否成功
    :param message: 处理结果消息
    """
    response: str
    success: bool
    message: str


class FillAgent(BaseAgent):
    """选号需求填写智能体"""
    
    def __init__(self):
        super().__init__(name="FillAgent")
        self.name = "选号需求填写智能体"
        self.description = "负责向品牌方询问博主的选号需求，识别产品类型并填写表单"
        self.doubao_client = DoubaoModel()
        # self._setup_routes()
    
    def _setup_routes(self) -> None:
        """设置路由"""
        router = APIRouter(prefix=f"/{self.__class__.__name__.lower().replace('agent', '')}")
        router.post("/fill", response_model=FillResponse)(self.fill_route)
        self.router = router
    
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        处理选号需求填写
        
        :param data: 包含聊天历史、用户输入和表单状态的数据
        :return: 处理结果
        """
        try:
            conversations = data.get("conversations", [])
            current_form = data.get("form", "")
            user_input = next((m.get('content') for m in reversed(conversations) if m.get('role') == "user"), "")
            
            # 构建提示词
            prompt = self._build_prompt(conversations, user_input, current_form)
            
            # 调用大模型生成回复
            response = await self.doubao_client.generate_text(prompt)
            
            logger.info(f"选号需求填写完成，用户输入: {user_input[:50]}...")
            
            return {
                "response": response.strip(),
                "success": True,
                "message": "选号需求填写成功"
            }
            
        except Exception as e:
            logger.error(f"选号需求填写失败: {str(e)}")
            return {
                "response": "抱歉，系统暂时无法处理您的请求，请稍后再试。",
                "success": False,
                "message": f"选号需求填写失败: {str(e)}"
            }
    
    def _build_prompt(self, conversations: List, user_input: str, current_form: str) -> str | None:
        """
        构建选号需求填写提示词
        
        :param conversations: 聊天历史记录
        :param user_input: 当前用户输入
        :param current_form: 当前表单状态
        :return: 构建的提示词
        """
        try:
            # 读取 prompt 模板文件
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_file = os.path.join(current_dir, "fill.txt")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = Template(f.read())
            
            # 替换模板中的占位符
            prompt = prompt_template.render(
                conversations=conversations,
                user_input=user_input,
                form=current_form
            )
            
            return prompt
            
        except Exception as e:
            logger.error(f"读取 fill.txt 文件失败: {str(e)}")
    
    async def fill_route(self, request: FillRequest) -> FillResponse:
        """
        选号需求填写接口
        
        :param request: 选号需求填写请求
        :return: 选号需求填写响应
        """
        try:
            result = await self.process({
                "conversations": request.conversations,
                "form": request.form
            })
            
            return FillResponse(
                response=result["response"],
                success=result["success"],
                message=result["message"]
            )
            
        except Exception as e:
            logger.error(f"选号需求填写接口调用失败: {str(e)}")
            return FillResponse(
                response="抱歉，系统暂时无法处理您的请求，请稍后再试。",
                success=False,
                message=f"选号需求填写失败: {str(e)}"
            )