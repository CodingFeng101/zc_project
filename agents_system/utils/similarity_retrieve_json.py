import asyncio
import json
import os
import numpy as np
from openai import AsyncOpenAI
from typing import List, Dict

# 初始化OpenAI客户端
openai_client = AsyncOpenAI(
    api_key="fb1a7bd2-fca4-47e0-9ea4-ef8661f01b7e",
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)


async def batch_get_vectors(sentences: List[str], model: str = "doubao-embedding-large-text-250515") -> Dict[str, List[float]]:
    """获取句子向量"""
    response = await openai_client.embeddings.create(
        model=model,
        input=sentences
    )
    return {word: emb for word, emb in zip(sentences, [x.embedding for x in response.data])}


def cosine_similarity(vector_a: List[float], vector_b: List[float]) -> float:
    """计算余弦相似度"""
    a = np.array(vector_a, dtype=float)
    b = np.array(vector_b, dtype=float)

    if len(a) != len(b):
        raise ValueError("向量长度必须相同")
    if not np.any(a) or not np.any(b):
        raise ValueError("不允许零向量")

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    return np.clip(dot_product / (norm_a * norm_b), -1.0, 1.0)


async def search_similar_in_group(query: str, group_uuid: str, top_n: int = 5, file_name: str = r"D:\PycharmProjects\zc_project\agents_system\utils\QAsql.json"):
    """在指定组内搜索最相似的句子（从JSON文件中检索）"""
    # 1. 获取查询句子的向量
    query_vectors = await batch_get_vectors([query])
    query_vector = query_vectors[query]

    # 2. 从JSON文件获取指定组的句子向量
    try:
        if not os.path.exists(file_name):
            print(f"文件 {file_name} 不存在")

        # 读取JSON文件内容
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 确保数据是列表格式
        if not isinstance(data, list):
            data = [data]

        # 查找指定group_uuid的组
        target_group = next((group for group in data if group.get("group_uuid") == group_uuid), None)

        if not target_group or "entries" not in target_group:
            print(f"未找到group_uuid为{group_uuid}的句子组")
            return []

        # 3. 计算相似度并排序
        similarity_results = []
        for entry in target_group["entries"]:
            try:
                stored_vector = entry['vector']
                similarity = cosine_similarity(query_vector, stored_vector)
                entry_with_sim = entry.copy()
                entry_with_sim['similarity'] = float(similarity)
                similarity_results.append(entry_with_sim)
            except Exception as e:
                print(f"处理句子 '{entry.get('question', '未知')}' 时出错: {str(e)}")
                continue

        # 4. 按相似度降序排序并返回前N个结果
        similarity_results.sort(key=lambda x: x['similarity'], reverse=True)
        results = similarity_results[:top_n]

        # 格式化结果信息
        info = ""
        for result in results:
            info += f"问题: {result['question']} 答案: {result['answer']}\n"

        return info.strip()  # 去除末尾多余的换行

    except Exception as e:
        print(f"处理文件时出错: {str(e)}")
        raise


# 使用示例
async def main():
    query_sentence = "目前你们和哪些平台达人合作？"
    target_group_uuid = "b51a2fef-d824-4b2a-a868-a69fac7eab69"

    results = await search_similar_in_group(query_sentence, target_group_uuid)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
