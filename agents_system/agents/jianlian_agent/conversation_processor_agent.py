#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List
from pydantic import BaseModel
from fastapi import APIRouter
from jinja2 import Template
from tqdm.asyncio import tqdm

from agents_system.agents.jianlian_agent.conversation_processor_prompt import CONVERSATION_PROCESS
from agents_system.core.base_agent import BaseAgent
from agents_system.models.doubao import DoubaoModel, logger


class ConversationProcessRequest(BaseModel):
    """
    对话处理请求模型

    :param conversations: 包含多个字典的列表，每个字典包含'小红书昵称'和'聊天记录'字段
    """
    conversations: List[Dict[str, str]]


class ConversationProcessResponse(BaseModel):
    """
    对话处理响应模型

    :param processed_conversations: 处理后的对话列表，保持相同结构但聊天记录字段为 LLM 生成内容
    :param success: 处理是否成功
    :param message: 处理结果消息
    """
    processed_conversations: List[Dict[str, str]]
    success: bool
    message: str


class ConversationProcessorAgent(BaseAgent):
    """对话内容处理智能体（多线程并发版本）"""

    def __init__(self):
        super().__init__(name="ConversationProcessorAgent")
        self.name = "对话内容处理智能体"
        self.description = "负责处理包含多个字典的列表，对每个字典中的聊天记录字段进行大模型处理"
        self.doubao_client = DoubaoModel()
        self._setup_routes()

    def _setup_routes(self) -> None:
        """设置路由"""
        router = APIRouter(prefix=f"/{self.__class__.__name__.lower().replace('agent', '')}")
        router.post("/process-conversation", response_model=ConversationProcessResponse)(self.process_conversation_route)
        self.router = router

    async def process(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        处理对话内容生成（异步并发版本）

        :param data: 包含对话列表的数据
        :return: 处理结果
        """
        try:
            conversations = data.get("conversations", [])

            if not conversations:
                return {
                    "conversations": [],
                    "success": False,
                    "message": "输入的对话列表为空"
                }

            # 准备异步任务列表
            tasks = []
            for conversation in conversations:
                chat_content = conversation.get("聊天记录", "")
                tasks.append(self._process_single_conversation(chat_content))

            total_tasks = len(tasks)
            logger.info(f"开始异步并发处理 {total_tasks} 条聊天记录")

            # 使用 asyncio.gather 进行异步并发处理
            processed_results = await tqdm.gather(
                *tasks,
                desc="异步处理对话"
            )

            # 处理异常结果
            for i, result in enumerate(processed_results):
                if isinstance(result, Exception):
                    logger.error(f"处理任务 {i} 时出错: {str(result)}")
                    processed_results[i] = f"内容生成失败: {str(result)[:100]}"

            # 构建结果列表，保持原数据结构
            processed_conversations = []
            for i, conversation in enumerate(conversations):
                processed_conversation = conversation.copy()
                processed_conversation["聊天记录"] = processed_results[i] or "处理失败"
                processed_conversations.append(processed_conversation)

            logger.info(f"异步并发对话处理完成，成功处理了 {len(processed_conversations)} 条聊天记录")

            return {
                "processed_conversations": processed_conversations,
                "success": True,
                "message": f"异步并发对话处理成功，处理了 {total_tasks} 个任务"
            }

        except Exception as e:
            logger.error(f"异步并发对话处理失败: {str(e)}")
            return {
                "processed_conversations": [],
                "success": False,
                "message": f"异步并发对话处理失败: {str(e)}"
            }

    async def _process_single_conversation(self, chat_content: str) -> str:
        """
        处理单个对话内容（异步方法）

        :param chat_content: 原始聊天记录内容
        :return: 生成的对话内容
        """
        if not chat_content or not chat_content.strip():
            return "有信息缺失，无法识别"

        try:
            # 构建提示词
            prompt = self._build_prompt(chat_content)

            # 异步调用大模型
            generated_content = await self.doubao_client.generate_text(prompt)
            return generated_content.strip()

        except Exception as e:
            logger.error(f"处理单个对话时出错: {str(e)}")
            return f"内容生成失败: {str(e)[:100]}"

    @staticmethod
    def _build_prompt(chat_content: str) -> str:
        """
        构建内容生成提示词

        :param chat_content: 原始聊天记录内容
        :return: 构建的提示词
        """
        conversation_processor_prompt = Template(CONVERSATION_PROCESS)
        prompt = conversation_processor_prompt.render(chat_content=chat_content)
        return prompt

    async def process_conversation_route(self, request: ConversationProcessRequest) -> ConversationProcessResponse:
        """
        对话处理接口

        :param request: 对话处理请求
        :return: 对话处理响应
        """
        try:
            result = await self.process({"conversations": request.conversations})

            return ConversationProcessResponse(
                processed_conversations=result["processed_conversations"],
                success=result["success"],
                message=result["message"]
            )

        except Exception as e:
            logger.error(f"对话处理接口调用失败: {str(e)}")
            return ConversationProcessResponse(
                processed_conversations=[],
                success=False,
                message=f"对话处理失败: {str(e)}"
            )
