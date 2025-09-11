#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from typing import Any, List, Dict
from pydantic import BaseModel
from fastapi import APIRouter
from jinja2 import Template
from agents_system.core.base_agent import BaseAgent
from agents_system.models.doubao import DoubaoModel, logger


class SaveRequest(BaseModel):
    """
    表单信息识别与更新请求模型
    
    :param conversations: 聊天历史记录
    :param form: 当前表单状态
    """
    conversations: List[Dict[str, str]]
    form: Dict[str, Any] = {}


class SaveResponse(BaseModel):
    """
    表单信息识别与更新响应模型
    
    :param updated_form: 更新后的表单内容，如果无更新则为null
    :param success: 处理是否成功
    :param message: 处理结果消息
    """
    updated_form: Dict[str, Any] = {}
    success: bool
    message: str


class SaveAgent(BaseAgent):
    """表单信息识别与更新智能体"""
    
    def __init__(self):
        super().__init__(name="SaveAgent")
        self.name = "表单信息识别与更新智能体"
        self.description = "专门负责识别聊天记录中表单信息并更新表单的系统"
        self.doubao_client = DoubaoModel()
        # self._setup_routes()
    
    def _setup_routes(self) -> None:
        """设置路由"""
        router = APIRouter(prefix=f"/{self.__class__.__name__.lower().replace('agent', '')}")
        router.post("/save", response_model=SaveResponse)(self.save_route)
        self.router = router
    
    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        处理表单信息识别与更新
        
        :param data: 包含聊天历史和当前表单状态的数据
        :return: 处理结果
        """
        try:
            conversations = data.get("conversations", "")
            current_form = data.get("form", "")
            
            # 构建提示词
            prompt = self._build_prompt(conversations, json.dumps(current_form))
            
            # 调用大模型进行表单更新
            response = await self.doubao_client.generate_text(prompt)
            
            # 处理响应
            updated_form = self._process_response(response)
            
            return {
                "updated_form": updated_form if updated_form != {} else current_form,
                "success": True,
                "message": "表单信息识别与更新成功"
            }
            
        except Exception as e:
            logger.error(f"表单信息识别与更新失败: {str(e)}")
            return {
                "updated_form": None,
                "success": False,
                "message": f"表单信息识别与更新失败: {str(e)}"
            }
    
    def _build_prompt(self, conversations: str, current_form: str) -> str | None:
        """
        构建表单信息识别与更新提示词
        
        :param conversations: 聊天历史记录
        :param current_form: 当前表单状态
        :return: 构建的提示词
        """
        try:
            # 读取 prompt 模板文件
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            prompt_file = os.path.join(current_dir, "save.txt")
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_template = Template(f.read())
            
            # 替换模板中的占位符
            prompt = prompt_template.render(
                conversations=conversations,
                form=current_form
            )
            
            return prompt
            
        except Exception as e:
            logger.error(f"读取 save.txt 文件失败: {str(e)}")

    def _process_response(self, response: str) -> Dict[str, Any]:
        """
        处理模型响应
        
        :param response: 模型响应
        :return: 处理后的表单内容或null
        """
        # 清理响应
        cleaned_response = response.strip()
        
        # 如果响应为空或者明确是null，返回null
        if not cleaned_response or cleaned_response.lower() == "null":
            return {}

        response = json.loads(cleaned_response)
        
        return response
    
    async def save_route(self, request: SaveRequest) -> SaveResponse:
        """
        表单信息识别与更新接口
        
        :param request: 表单信息识别与更新请求
        :return: 表单信息识别与更新响应
        """
        try:
            result = await self.process({
                "conversations": request.conversations,
                "form": request.form
            })
            return SaveResponse(
                updated_form=result["updated_form"],
                success=result["success"],
                message=result["message"]
            )
            
        except Exception as e:
            logger.error(f"表单信息识别与更新接口调用失败: {str(e)}")
            return SaveResponse(
                updated_form=None,
                success=False,
                message=f"表单信息识别与更新失败: {str(e)}"
            )
