# import asyncio
# import json
# import mysql.connector  # 仅使用mysql相关包
# import numpy as np
# from openai import AsyncOpenAI
# from typing import List, Dict
#
# from agents_system.config.settings import settings
#
# # 初始化OpenAI客户端
# openai_client = AsyncOpenAI(
#     api_key=settings.API_KEY,
#     base_url=settings.BASE_URL
# )
#
# # 数据库配置（不依赖DictCursor导入）
# DB_CONFIG = {
#     'host': settings.DB_HOST,
#     'user': settings.DB_USER,
#     'password': settings.DB_PASSWORD,
#     'database': settings.DB_NAME,
#     'charset': 'utf8mb4'
# }
#
#
# async def batch_get_vectors(sentences: List[str], model: str = settings.EMBEDDING_MODEL) -> Dict[str, List[float]]:
#     """获取句子向量"""
#     response = await openai_client.embeddings.create(
#         model=model,
#         input=sentences
#     )
#     return {word: emb for word, emb in zip(sentences, [x.embedding for x in response.data])}
#
#
# def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
#     """计算余弦相似度"""
#     a = np.array(vector_a, dtype=float)
#     b = np.array(vector_b, dtype=float)
#
#     if len(a) != len(b):
#         raise ValueError("向量长度必须相同")
#     if not np.any(a) or not np.any(b):
#         raise ValueError("不允许零向量")
#
#     dot_product = np.dot(a, b)
#     norm_a = np.linalg.norm(a)
#     norm_b = np.linalg.norm(b)
#
#     return np.clip(dot_product / (norm_a * norm_b), -1.0, 1.0)
#
#
# async def search_similar_in_group(query: str, graph_uuid: str, top_n: int = 5):
#     """在指定组内搜索最相似的句子（修复游标问题）"""
#     # 1. 获取查询句子的向量
#     query_vectors = await batch_get_vectors([query])
#     query_vector = query_vectors[query]
#
#     # 2. 从数据库获取指定组的句子向量
#     conn = None
#     try:
#         # 建立连接时不指定游标类型
#         conn = mysql.connector.connect(**DB_CONFIG)
#         # 创建游标时显式指定为字典游标（关键修复）
#         cursor = conn.cursor(dictionary=True)  # 这里指定dictionary=True
#
#         # 只查询指定graph_uuid组的句子
#         sql = """
#         SELECT id, group_uuid, question, answer, vector, vector_model, create_time
#         FROM sentence_vector
#         WHERE group_uuid = %s
#         """
#
#         cursor.execute(sql, (graph_uuid,))
#         results = cursor.fetchall()  # 现在返回的是字典列表
#
#         if not results:
#             print(f"未找到group_uuid为{graph_uuid}的句子")
#             return []
#
#         # 3. 计算相似度并排序
#         similarity_results = []
#         for row in results:
#             try:
#                 stored_vector = json.loads(row['vector'])
#                 similarity = cosine_similarity(query_vector, stored_vector)
#                 row_with_sim = row.copy()
#                 row_with_sim['similarity'] = float(similarity)
#                 similarity_results.append(row_with_sim)
#             except Exception as e:
#                 print(f"处理句子ID {row['id']} 时出错: {str(e)}")
#                 continue
#
#         # 4. 按相似度降序排序并返回前N个结果
#         similarity_results.sort(key=lambda x: x['similarity'], reverse=True)
#         results =  similarity_results[:top_n]
#         info = ""
#         for result in results:
#             info += f"问题: {result['question']} 答案: {result['answer']}\n"
#         return info
#     except mysql.connector.Error as e:
#         print(f"数据库操作出错: {str(e)}")
#         raise
#     finally:
#         if conn and conn.is_connected():
#             conn.close()
#
#
# # 使用示例
# async def main():
#     query_sentence = "目前你们和哪些平台达人合作？"
#     target_group_uuid = "dbd188e7-ee4d-47fb-9c8f-4b6e9da24086"
#
#     results = await search_similar_in_group(query_sentence, target_group_uuid)
#     print(results)
#
#
# if __name__ == "__main__":
#     asyncio.run(main())
