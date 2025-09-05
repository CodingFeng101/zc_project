# #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# from typing import List, Dict
# from pydantic import BaseModel
# from fastapi import APIRouter
#
# from agents_system.core.base_agent import BaseAgent
# from agents_system.models.doubao import DoubaoModel, logger
# from agents_system.utils.similarity_retrieve import search_similar_in_group
#
#
# class GlobalQARequest(BaseModel):
#     """
#     选号需求填写请求模型
#
#     :param conversations: 聊天历史记录
#     :param form: 当前表单状态
#     """
#     conversations: List[Dict[str, str]]
#
#
# class GlobalQAResponse(BaseModel):
#     """
#     选号需求填写响应模型
#
#     :param response: 智能体回复内容
#     :param success: 处理是否成功
#     :param message: 处理结果消息
#     """
#     response: str | None
#     is_manual: bool
#     reference: str | None
#     success: bool
#     message: str
#
#
# class GlobalQAgent(BaseAgent):
#     """选号需求填写智能体"""
#
#     def __init__(self):
#         super().__init__(name="GlobalQAAgent")
#         self.name = "全局QA智能体"
#         self.description = "负责回答用户提出的一系列问题"
#         self.doubao_client = DoubaoModel()
#         # self._setup_routes()
#
#     def _setup_routes(self) -> None:
#         """设置路由"""
#         router = APIRouter(prefix=f"/{self.__class__.__name__.lower().replace('agent', '')}")
#         router.post("/fill", response_model=GlobalQARequest)(self.qa_route)
#         self.router = router
#
#     async def process(self, data: GlobalQARequest) -> GlobalQAResponse:
#         """
#         处理选号需求填写
#
#         :param data: 包含聊天历史、用户输入和表单状态的数据
#         :return: 处理结果
#         """
#         try:
#             conversations = data.get("conversations", [])
#             user_input = next((m.get('content') for m in reversed(conversations) if m.get('role') == "user"), "")
#             info = await search_similar_in_group(query=user_input, graph_uuid="31428a7e-8ed0-41e4-bd48-f872f8f78e06")
#             # 构建提示词
#             prompt = f"""
#             背景信息: {info}
#             用户问题: {user_input}
#             请你只根据这些背景信息回答用户问题，你不可以自由发挥，你的语气要温和耐心，模仿背景信息回答的语气来回答，回答尽可能简略一些，
#             如果你无法回答这个问题或者这个问题和背景信息没有关系，请你只输出一个大写字母N,不要输出任何多余的内容
#             """
#
#             # 调用大模型生成回复
#             answer = await self.doubao_client.generate_text(prompt)
#
#             logger.info(f"全局QA智能体完成，用户输入: {user_input[:50]}...")
#             reference = ""
#             is_manual = False
#             response = ""
#             if answer == "N":
#                 is_manual = True
#             elif answer.count("*") or answer.count("X") > 0:
#                 is_manual = True
#                 reference = response
#             else:
#                 response = answer
#             response = GlobalQAResponse(
#                 response = response.strip(),
#                 is_manual = is_manual,
#                 reference = reference,
#                 success = True,
#                 message = "全局QA智能体完成"
#             )
#             return response
#
#         except Exception as e:
#             logger.error(f"全局QA智能体调用失败: {str(e)}")
#             return GlobalQAResponse(
#                 response = "抱歉，系统暂时无法处理您的请求，请稍后再试。",
#                 is_manual = True,
#                 reference = "",
#                 success = False,
#                 message = f"全局QA智能体调用失败: {str(e)}"
#             )
#
#     async def qa_route(self, request: GlobalQARequest) -> GlobalQAResponse:
#         """
#         选号需求填写接口
#
#         :param request: 选号需求填写请求
#         :return: 选号需求填写响应
#         """
#
#         return await self.process(request)
