#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Any, Dict, List
from pydantic import BaseModel
from fastapi import APIRouter
from jinja2 import Template

from tqdm.asyncio import tqdm

from agents_system.agents.jianlian_agent.rebate_identification_prompt import REBATE_IDENTIFICATION
from agents_system.core.base_agent import BaseAgent
from agents_system.models.doubao import DoubaoModel, logger


class RebateIdentificationRequest(BaseModel):
    """
    返点识别请求模型

    :param conversations: 包含多个字典的列表，每个字典包含'小红书昵称'和'聊天记录'字段
    """
    conversations: List[Dict[str, str]]


class RebateIdentificationResponse(BaseModel):
    """
    返点识别响应模型

    :param processed_conversations: 处理后的对话列表，包含'小红书昵称'、'聊天记录'、'原因'、'标签'字段
    :param success: 处理是否成功
    :param message: 处理结果消息
    """
    processed_conversations: List[Dict[str, str]]
    success: bool
    message: str


class RebateIdentificationAgent(BaseAgent):
    """返点识别智能体（异步并发版本）"""

    def __init__(self):
        super().__init__(name="RebateIdentificationAgent")
        self.name = "返点识别智能体"
        self.description = "负责分析聊天记录中未能达成返点协议的原因，并将识别结果添加到原数据结构中（支持异步并发）"
        self.doubao_client = DoubaoModel()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """设置路由"""
        router = APIRouter(prefix=f"/{self.__class__.__name__.lower().replace('agent', '')}")
        router.post("/identify-rebate", response_model=RebateIdentificationResponse)(self.identify_rebate_route)
        self.router = router

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        处理返点识别分析（异步并发版本）

        :param data: 包含对话列表的数据
        :return: 处理结果
        """
        try:
            conversations = data.get("conversations", [])

            if not conversations:
                return {
                    "processed_conversations": [],
                    "success": False,
                    "message": "输入的对话列表为空"
                }

            # 准备异步任务列表
            tasks = []
            for conversation in conversations:
                chat_content = conversation.get("聊天记录", "")
                tasks.append(self._analyze_single_conversation(chat_content))

            total_tasks = len(tasks)
            logger.info(f"开始异步并发分析 {total_tasks} 条聊天记录的返点识别")

            # 使用 asyncio.gather 进行异步并发处理
            processed_results = await tqdm.gather(
                *tasks,
                desc="异步分析返点原因"
            )

            # 处理异常结果
            for i, result in enumerate(processed_results):
                if isinstance(result, Exception):
                    logger.error(f"分析任务 {i} 时出错: {str(result)}")
                    processed_results[i] = {"原因": f"分析失败: {str(result)[:100]}", "标签": "分析异常"}

            # 构建结果列表，保持原数据结构并添加原因、标签字段
            processed_conversations = []
            for i, conversation in enumerate(conversations):
                processed_conversation = conversation.copy()
                result = processed_results[i]
                if isinstance(result, dict):
                    processed_conversation["原因"] = result.get("原因", "分析失败")
                    processed_conversation["标签"] = result.get("标签", "无标签适合")
                else:
                    processed_conversation["原因"] = result or "分析失败"
                    processed_conversation["标签"] = "无标签适合"
                processed_conversations.append(processed_conversation)

            logger.info(f"异步并发返点识别分析完成，成功分析了 {len(processed_conversations)} 条聊天记录")

            return {
                "processed_conversations": processed_conversations,
                "success": True,
                "message": f"异步并发返点识别分析成功，处理了 {total_tasks} 个任务"
            }

        except Exception as e:
            logger.error(f"异步并发返点识别分析失败: {str(e)}")
            return {
                "processed_conversations": [],
                "success": False,
                "message": f"异步并发返点识别分析失败: {str(e)}"
            }

    async def _analyze_single_conversation(self, chat_content: str) -> dict[str, str]:
        """
        分析单个对话的返点识别原因（异步方法）

        :param chat_content: 原始聊天记录内容
        :return: 返点识别分析结果，包含原因、标签
        """
        if not chat_content or not chat_content.strip():
            return {"原因": "聊天记录为空，无法分析", "标签": "无标签适合"}

        try:
            # 构建提示词
            prompt = self._build_prompt(chat_content)

            # 异步调用大模型
            analysis_result = await self.doubao_client.generate_text(prompt)
            
            # 尝试解析JSON结果
            try:
                result_dict = json.loads(analysis_result.strip())
                return {
                    "原因": result_dict.get("原因", "分析结果格式异常"),
                    "标签": result_dict.get("标签", "无标签适合")
                }
            except json.JSONDecodeError:
                logger.warning(f"大模型返回结果不是有效JSON格式: {analysis_result[:200]}")
                return {"原因": analysis_result.strip(), "标签": "无标签适合"}

        except Exception as e:
            logger.error(f"分析单个对话时出错: {str(e)}")
            return {"原因": f"分析失败: {str(e)[:100]}", "标签": "分析异常"}

    @staticmethod
    def _build_prompt(chat_content: str) -> str:
        """
        构建返点识别分析提示词

        :param chat_content: 原始聊天记录内容
        :return: 构建的提示词
        """
        rebate_identification_prompt = Template(REBATE_IDENTIFICATION)
        prompt = rebate_identification_prompt.render(chat_content=chat_content)
        return prompt

    async def identify_rebate_route(self, request: RebateIdentificationRequest) -> RebateIdentificationResponse:
        """
        返点识别分析接口

        :param request: 返点识别请求
        :return: 返点识别响应
        """
        try:
            result = await self.process({"conversations": request.conversations})

            return RebateIdentificationResponse(
                processed_conversations=result["processed_conversations"],
                success=result["success"],
                message=result["message"]
            )

        except Exception as e:
            logger.error(f"返点识别接口调用失败: {str(e)}")
            return RebateIdentificationResponse(
                processed_conversations=[],
                success=False,
                message=f"返点识别分析失败: {str(e)}"
            )
