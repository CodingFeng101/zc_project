#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import List, Dict, Any
from pydantic import BaseModel
from fastapi import APIRouter

from agents_system.agents.second_bargaining_agent.dispatch_agent import DispatchAgent, DispatchRequest
from agents_system.agents.second_bargaining_agent.fill_agent import FillAgent, FillRequest
from agents_system.agents.second_bargaining_agent.globalqaagent import GlobalQARequest, GlobalQAgent
from agents_system.agents.second_bargaining_agent.save_agent import SaveAgent, SaveRequest
from agents_system.models.doubao import logger


class SecondBargainingRequest(BaseModel):
    """
    统一API请求模型

    :param form: 表单列表
    :param conversations: 聊天记录
    """
    form: Dict[str, Any] = {}
    conversations: List[Dict[str, str]]
    status: str = "1"


class SecondBargainingResponse(BaseModel):
    """
    统一API响应模型

    :param form: 更新后的表单
    :param is_manual: 是否转人工
    :param agent_response: 智能体回复内容
    :param status: 处理状态，1表示成功，0表示失败
    :param reference: 参考信息
    """
    form: Dict[str, Any] = {}
    is_manual: bool = False
    agent_response: str | None = ""
    status: str = "1"
    reference: str | None = ""
    cooperation_status: str = ""


class SecondBargainingService:
    """统一服务，封装三个智能体的完整流程"""

    def __init__(self):
        self.dispatch_agent = DispatchAgent()
        self.fill_agent = FillAgent()
        self.save_agent = SaveAgent()
        self.globalqa_agent = GlobalQAgent()
        self.router = APIRouter(prefix="/secondbargaining")
        self._setup_routes()
        logger.info("Initialized SecondBargainingService")

    def _setup_routes(self) -> None:
        """设置路由"""
        self.router.post("/process", response_model=SecondBargainingResponse)(self.process_request)

    async def process_request(self, request: SecondBargainingRequest) -> SecondBargainingResponse:
        """
        处理统一API请求

        :param request: 统一请求对象
        """
        try:
            # 步骤1：调用调度智能体进行路由判断
            dispatch_request = DispatchRequest(
                conversations=request.conversations
            )

            dispatch_response = await self.dispatch_agent.dispatch_route(dispatch_request)

            if not dispatch_response.success:
                return SecondBargainingResponse(
                    form=request.form,
                    agent_response="",
                )

            route_code = dispatch_response.route_code
            logger.info(f"Dispatch agent returned route code: {route_code}")

            # 步骤2：根据路由代码处理
            if route_code == "1":
                # 转接至二次议价智能体
                return await self._handle_fill_agent(request)
            elif route_code == "2":
                # 转接至全局QA智能体（预留接口）
                return await self._handle_global_qa(request)
            elif route_code == "3":
                return SecondBargainingResponse(
                    agent_response="好的，清单已确认，后续将按此推进合作",
                    form=request.form,
                    status="0",
                )
            else:
                return SecondBargainingResponse(
                    form=request.form,
                    agent_response="",
                    status="1"
                )

        except Exception as e:
            logger.error(f"Error processing SecondBargaining request: {str(e)}")
            return SecondBargainingResponse(
                form=request.form,
                agent_response="",
            )

    async def _handle_fill_agent(self, request: SecondBargainingRequest) -> SecondBargainingResponse:
        """
        处理选号智能体流程

        :param request: 原始请求
        """
        try:
            # 步骤3：调用选号智能体
            fill_request = FillRequest(
                conversations=request.conversations,
                # form=request.form
            )

            fill_response = await self.fill_agent.fill_route(fill_request)

            if not fill_response.success:
                return SecondBargainingResponse(
                    form=request.form,
                    agent_response="",
                )
            request.conversations.append({"role": "assistant", "content": fill_response.response})
            # 步骤5：调用保存智能体
            save_request = SaveRequest(
                conversations=request.conversations,
                form=request.form
            )

            save_response = await self.save_agent.save_route(save_request)
            logger.info(f"豆包回答: {fill_response.response}")
            logger.info(f"表单:{save_response.updated_form}")
            logger.info(f"聊天记录:{request.conversations}")

            if not save_response.success:
                return SecondBargainingResponse(
                    form=request.form,
                    agent_response=fill_response.response,
                )

            # 分析合作状态智能体


            # 步骤6：返回最终结果
            return SecondBargainingResponse(
                form=save_response.updated_form,
                agent_response=fill_response.response,
            )

        except Exception as e:
            logger.error(f"Error in fill agent flow: {str(e)}")
            return SecondBargainingResponse(
                form=request.form,
                agent_response="",
                status="1",
                reference="666"
            )

    async def _handle_global_qa(self, request: SecondBargainingRequest) -> SecondBargainingResponse:
        """
        处理全局QA智能体流程（预留接口）

        :param request: 原始请求
        """
        try:
            qa_request = GlobalQARequest(
                conversations=request.conversations
            )
            qa_response = await self.globalqa_agent.qa_route(qa_request)
            if not qa_response.success:
                return SecondBargainingResponse(
                    form=request.form,
                    agent_response=qa_response.response,
                    is_manual=qa_response.is_manual,
                    reference=qa_response.reference,
                    status="1",
                )
            logger.info(f"全局QA回答: {qa_response.response}")
            logger.info(f"转人工: {qa_response.is_manual}")
            logger.info(f"参考信息: {qa_response.reference}")
            return SecondBargainingResponse(
                form=request.form,
                is_manual=qa_response.is_manual,
                agent_response=qa_response.response,
                status="1",
                reference="666"
            )
        except Exception as e:
            logger.error(f"Error in global QA flow: {str(e)}")
            return SecondBargainingResponse(
                form=request.form,
                agent_response="",
                status="1",
                reference="6"
            )


# 全局统一服务实例
SecondBargaining_service = SecondBargainingService()