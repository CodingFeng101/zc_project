#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
from typing import List, Dict


def convert_excel_to_conversation_json(excel_file_path: str, output_json_path: str = None) -> List[Dict[str, str]]:
    """
    将Excel文件转换为conversation_processor_agent所需的JSON格式

    :param excel_file_path: Excel文件路径
    :param output_json_path: 输出JSON文件路径（可选）
    :return: 转换后的数据列表
    """
    try:
        # 读取Excel文件
        print(f"正在读取Excel文件: {excel_file_path}")
        df = pd.read_excel(excel_file_path)

        # 显示Excel文件的基本信息
        print(f"Excel文件形状: {df.shape} (行:列)")
        print(f"列名: {list(df.columns)}")
        print("\n前5行数据预览:")
        print(df.head())

        # 检查必要的列是否存在
        required_columns = ['小红书昵称', '聊天记录']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            print(f"\n警告: 缺少必要的列: {missing_columns}")
            print("可用的列名:", list(df.columns))

            # 尝试智能匹配列名
            column_mapping = {}
            for req_col in required_columns:
                for df_col in df.columns:
                    if req_col in str(df_col) or str(df_col) in req_col:
                        column_mapping[req_col] = df_col
                        print(f"自动匹配: '{req_col}' -> '{df_col}'")
                        break

            if len(column_mapping) < len(required_columns):
                print("\n请手动指定列名映射:")
                for i, col in enumerate(df.columns):
                    print(f"{i}: {col}")

                nickname_col_idx = input("请输入'小红书昵称'对应的列索引: ")
                chat_col_idx = input("请输入'聊天记录'对应的列索引: ")

                try:
                    nickname_col = df.columns[int(nickname_col_idx)]
                    chat_col = df.columns[int(chat_col_idx)]
                    column_mapping = {'小红书昵称': nickname_col, '聊天记录': chat_col}
                except (ValueError, IndexError):
                    raise ValueError("无效的列索引")
        else:
            column_mapping = {'小红书昵称': '小红书昵称', '聊天记录': '聊天记录'}

        # 数据清洗和转换
        print("\n开始数据转换...")

        # 获取原始数据行数
        original_count = len(df)
        print(f"原始数据行数: {original_count}")

        # 转换为所需格式并进行严格的空值过滤
        conversations = []
        filtered_count = 0

        for index, row in df.iterrows():
            # 获取昵称和聊天记录，处理各种空值情况
            nickname_raw = row[column_mapping['小红书昵称']]
            chat_record_raw = row[column_mapping['聊天记录']]

            # 严格的空值检查和清理
            nickname = ""
            chat_record = ""

            # 处理昵称
            if pd.notna(nickname_raw) and nickname_raw is not None:
                nickname = str(nickname_raw).strip()
                # 排除只包含空白字符、"nan"、"null"等无效值
                if nickname.lower() in ['nan', 'null', 'none', ''] or not nickname:
                    nickname = ""

            # 处理聊天记录
            if pd.notna(chat_record_raw) and chat_record_raw is not None:
                chat_record = str(chat_record_raw).strip()
                # 排除只包含空白字符、"nan"、"null"等无效值
                if chat_record.lower() in ['nan', 'null', 'none', ''] or not chat_record:
                    chat_record = ""

            # 严格过滤：昵称或聊天记录任一为空则排除
            if not nickname or not chat_record:
                filtered_count += 1
                print(
                    f"过滤第{index + 1}行 - 昵称: '{nickname}', 聊天记录: '{chat_record[:50]}{'...' if len(chat_record) > 50 else ''}'")
                continue

            conversation_dict = {
                "小红书昵称": nickname,
                "聊天记录": chat_record
            }
            conversations.append(conversation_dict)

        print(f"\n数据过滤统计:")
        print(f"- 原始数据行数: {original_count}")
        print(f"- 过滤掉的行数: {filtered_count}")
        print(f"- 有效数据行数: {len(conversations)}")
        print(f"- 过滤率: {filtered_count / original_count * 100:.2f}%")

        if len(conversations) == 0:
            print("\n警告: 没有有效数据！所有行都被过滤掉了。")
            return []

        # 保存到JSON文件（如果指定了输出路径）
        if output_json_path:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(conversations, f, ensure_ascii=False, indent=2)
            print(f"JSON文件已保存到: {output_json_path}")

        # 显示转换结果示例
        print("\n转换结果示例（前3条有效数据）:")
        for i, conv in enumerate(conversations[:3]):
            print(f"第{i + 1}条:")
            print(f"  小红书昵称: {conv['小红书昵称']}")
            print(f"  聊天记录: {conv['聊天记录'][:100]}{'...' if len(conv['聊天记录']) > 100 else ''}")
            print()

        return conversations

    except FileNotFoundError:
        print(f"错误: 找不到文件 {excel_file_path}")
        return []
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return []


def validate_conversations(conversations: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    二次验证对话数据，确保没有空值

    :param conversations: 对话数据列表
    :return: 验证后的对话数据列表
    """
    valid_conversations = []
    invalid_count = 0

    for i, conv in enumerate(conversations):
        nickname = conv.get('小红书昵称', '').strip()
        chat_record = conv.get('聊天记录', '').strip()

        # 再次严格检查
        if not nickname or not chat_record or nickname.lower() in ['nan', 'null', 'none'] or chat_record.lower() in [
            'nan', 'null', 'none']:
            invalid_count += 1
            print(
                f"二次验证过滤第{i + 1}条数据 - 昵称: '{nickname}', 聊天记录: '{chat_record[:30]}{'...' if len(chat_record) > 30 else ''}'")
            continue

        valid_conversations.append(conv)

    if invalid_count > 0:
        print(f"\n二次验证过滤了 {invalid_count} 条无效数据")

    return valid_conversations


def create_conversation_processor_input(conversations: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    """
    创建conversation_processor_agent的标准输入格式

    :param conversations: 对话数据列表
    :return: 标准输入格式
    """
    # 二次验证数据
    validated_conversations = validate_conversations(conversations)

    return {
        "conversations": validated_conversations
    }


def main():
    """主函数"""
    # Excel文件路径
    excel_file = r"D:\PycharmProjects\zc_project\agents_system\data\data_jianlian.xlsx"

    # 输出JSON文件路径
    json_output = r"D:\PycharmProjects\zc_project\agents_system\data\conversation_data.json"

    # 转换Excel到JSON
    conversations = convert_excel_to_conversation_json(excel_file, json_output)

    if conversations:
        # 创建conversation_processor_agent的输入格式（包含二次验证）
        processor_input = create_conversation_processor_input(conversations)

        # 保存为conversation_processor_agent的输入格式
        processor_input_file = r"d:\PycharmProjects\zc_project\conversation_processor_input.json"
        with open(processor_input_file, 'w', encoding='utf-8') as f:
            json.dump(processor_input, f, ensure_ascii=False, indent=2)

        print(f"\nconversation_processor_agent输入文件已保存到: {processor_input_file}")

        # 最终数据统计
        final_count = len(processor_input['conversations'])
        print(f"\n最终数据统计:")
        print(f"- 最终有效记录数: {final_count}")
        print(f"- 所有记录都包含有效的昵称和聊天记录")

        # 数据质量检查
        nickname_lengths = [len(conv['小红书昵称']) for conv in processor_input['conversations']]
        chat_lengths = [len(conv['聊天记录']) for conv in processor_input['conversations']]

        print(f"\n数据质量统计:")
        print(f"- 昵称长度范围: {min(nickname_lengths)} - {max(nickname_lengths)} 字符")
        print(f"- 聊天记录长度范围: {min(chat_lengths)} - {max(chat_lengths)} 字符")
        print(f"- 平均聊天记录长度: {sum(chat_lengths) / len(chat_lengths):.1f} 字符")
    else:
        print("转换失败，请检查Excel文件格式或数据质量")


if __name__ == "__main__":
    main()