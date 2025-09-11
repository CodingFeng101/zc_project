#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
标签处理智能体 - 合并版本

功能：
1. 处理无合适标签的聊天记录
2. 使用标签识别智能体生成标签
3. 使用标签合并智能体合并标签
4. 输出最终的标签字典

使用方法：
1. 确保已安装所有依赖包
2. 确保豆包模型API配置正确
3. 运行此脚本：python merged_label_processing.py
"""

import json
import os
import sys
import asyncio
from typing import List, Dict, Any

# 添加项目路径到系统路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agents_system.models.doubao import call_doubao

# 标签识别智能体的prompt模板
LABEL_RECOGNITION = """
一、任务
基于输入的小红书博主昵称及对应的返点合作聊天记录，直接生成 1-3 个精准匹配场景的标签（标签需贴合 "返点议题未达成一致" 的核心，若记录无返点关联，标签需前置 "无返点关联 -"；若有返点关联，标签需前置 "返点相关 -"）。
二、输入
聊天记录: {{conservation}}
三、标签生成要求
标签格式为 "场景核心 + 关键行为"，避免宽泛表述（如 "博主拒绝合作" 无效，需具体为 "无返点关联 - 博主仅做美食内容拒绝家电推广"）；
标签需完全对应聊天记录内容，不添加无关信息，若记录无返点关联，需明确体现 "无返点沟通" 的场景；若有返点关联，需体现 "返点未达成一致" 的关键矛盾；
每个输入生成 1 个标签，无需额外说明。
"""

# 标签合并智能体的prompt模板
LABEL_MERGE = """
一、任务
对输入的标签列表进行分析，将核心场景一致、表述差异仅为细节的标签合并为 "标准化标签"，输出合并后的标签列表。
二、输入
标签列表: {{label_list}}
三、标签合并要求
核心场景一致的标签归为一类（如 "无返点关联 - 博主仅做美食内容拒绝家电推广" 与 "无返点关联 - 博主因品类不符拒绝家电类合作"，均为 "品类不符导致无返点合作终止"，需合并）；
每类合并后生成 1 个 "标准化标签"，标签需保留核心场景，表述简洁精准，与同类标签的共性场景完全匹配；
仅出现 1 次、无同类场景的标签，直接保留原标签，不强行合并；
对最终标签列表中的每个标签进行定义生成，以键值对的字典方式输出，键是标签，值是定义。
示例：
{"全程未提返点-因博主无推广经验终止": "智能体、博主均未提返点，博主以"没拍过/不会弄"拒绝合作",
"返点有效期太短-按周算": "智能体要"2周达标"，博主需3周"}
"""

async def call_ai_model(prompt: str) -> str:
    """
    调用豆包AI模型的接口函数
    
    :param prompt: 输入的prompt文本
    :return: AI模型返回的结果
    """
    try:
        print(f"调用豆包模型处理prompt: {prompt[:100]}...")
        result = await call_doubao(prompt)
        return result.strip()
    except Exception as e:
        print(f"调用AI模型时发生错误: {e}")
        return ""

def load_missing_conversations(json_file_path: str) -> List[Dict[str, Any]]:
    """
    从JSON文件中加载missing_tag_conversations数据
    
    :param json_file_path: JSON文件路径
    :return: 无标签对话记录列表
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        missing_conversations = data.get('missing_tag_conversations', [])
        print(f"成功加载 {len(missing_conversations)} 条无标签对话记录")
        return missing_conversations
    
    except FileNotFoundError:
        print(f"错误：找不到文件 {json_file_path}")
        return []
    except json.JSONDecodeError:
        print(f"错误：JSON文件格式错误 {json_file_path}")
        return []
    except Exception as e:
        print(f"错误：读取文件时发生异常 {e}")
        return []

async def generate_label_for_conversation(conversation: Dict[str, Any]) -> str:
    """
    为单条对话记录生成标签
    
    :param conversation: 对话记录字典
    :return: 生成的标签
    """
    # 构建prompt
    chat_record = conversation.get('聊天记录', '')
    nickname = conversation.get('小红书昵称', '')
    
    # 使用标签识别智能体的prompt模板
    prompt = LABEL_RECOGNITION.replace('{{conservation}}', chat_record)
    
    print(f"正在为博主 '{nickname}' 生成标签...")
    
    # 调用AI模型生成标签
    generated_label = await call_ai_model(prompt)
    
    return generated_label.strip()

async def merge_labels(labels: List[str]) -> Dict[str, str]:
    """
    合并标签列表，返回标签字典
    
    :param labels: 标签列表
    :return: 合并后的标签字典
    """
    # 将标签列表转换为字符串
    labels_str = '\n'.join([f"- {label}" for label in labels])
    
    # 使用标签合并智能体的prompt模板
    prompt = LABEL_MERGE.replace('{{label_list}}', labels_str)
    
    print(f"正在合并 {len(labels)} 个标签...")
    
    # 调用AI模型进行标签合并
    merged_result = await call_ai_model(prompt)
    
    try:
        # 尝试解析返回的字典格式结果
        # 这里假设AI返回的是JSON格式的字典
        result_dict = json.loads(merged_result)
        return result_dict
    except json.JSONDecodeError:
        print("警告：AI返回结果不是有效的JSON格式，返回原始结果")
        return {"合并结果": merged_result}

async def process_conversation_with_index(conversation: Dict[str, Any], index: int, total: int) -> str | None:
    """
    处理单条对话记录并返回生成的标签
    
    :param conversation: 对话记录字典
    :param index: 当前处理的索引
    :param total: 总记录数
    :return: 生成的标签或None
    """
    print(f"\n处理第 {index}/{total} 条记录")
    
    try:
        label = await generate_label_for_conversation(conversation)
        if label:
            print(f"生成标签: {label}")
            return label
        else:
            print("未能生成有效标签")
            return None
    except Exception as e:
        print(f"处理对话记录时发生错误: {e}")
        return None

async def main():
    """
    主函数：执行完整的标签处理流程
    """
    print("开始处理无合适标签的聊天记录...")
    
    # 1. 读取JSON文件中的missing_tag_conversations数据
    json_file_path = r"D:\PycharmProjects\zc_project\agents_system\utils\tag_analysis_results.json"
    missing_conversations = load_missing_conversations(json_file_path)
    
    if not missing_conversations:
        print("没有找到需要处理的对话记录")
        return
    
    # 2. 并发处理所有对话记录
    print(f"\n开始并发处理 {len(missing_conversations)} 条记录...")
    
    # 创建并发任务列表
    tasks = [
        process_conversation_with_index(conversation, i + 1, len(missing_conversations))
        for i, conversation in enumerate(missing_conversations)
    ]
    
    # 并发执行所有任务
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 过滤有效的标签结果
    generated_labels = []
    for result in results:
        if isinstance(result, str) and result.strip():
            generated_labels.append(result.strip())
        elif isinstance(result, Exception):
            print(f"任务执行异常: {result}")
    
    print(f"\n共生成 {len(generated_labels)} 个标签")
    
    # 3. 将生成的标签列表传递给标签合并智能体
    if generated_labels:
        print("\n开始标签合并处理...")
        try:
            final_labels_dict = await merge_labels(generated_labels)
            
            # 4. 输出最终结果
            print("\n=== 最终标签字典 ===")
            for label, definition in final_labels_dict.items():
                print(f"{label}: {definition}")
            
            # 保存结果到文件
            output_file = "d:\\PycharmProjects\\zc_project\\agents_system\\test\\generated_labels_result.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(final_labels_dict, f, ensure_ascii=False, indent=2)
            
            print(f"\n结果已保存到: {output_file}")
            
        except Exception as e:
            print(f"标签合并过程中发生错误: {e}")
    else:
        print("没有生成任何标签，无法进行合并")
    
    print("\n处理完成！")

async def run_processing():
    """
    运行标签处理流程
    """
    print("=" * 60)
    print("开始运行标签处理流程")
    print("=" * 60)
    
    try:
        await main()
        print("\n" + "=" * 60)
        print("标签处理流程完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n运行过程中发生错误: {e}")
        print("请检查：")
        print("1. 豆包模型API配置是否正确")
        print("2. 网络连接是否正常")
        print("3. 输入文件是否存在")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(run_processing())
    if success:
        print("\n处理成功完成！")
    else:
        print("\n处理失败，请检查错误信息。")
        sys.exit(1)