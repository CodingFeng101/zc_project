#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import json
import re
from typing import Any


def extract_excel_data(input_file_path: str, output_file_path: str) -> None:
    """
    从Excel文件中提取数据并保存为JSON格式

    :param input_file_path: Excel文件路径
    :param output_file_path: 输出JSON文件路径
    """
    try:
        # 读取Excel文件
        df = pd.read_excel(input_file_path)

        # 查找匹配的列名
        nickname_col = None
        chat_col = None
        rebate_col = None

        for col in df.columns:
            col_str = str(col).strip()
            if '小红书昵称' in col_str or col_str == '昵称':
                nickname_col = col
            elif col_str == '聊天记录':  # 精确匹配，避免匹配到"聊天记录总结"
                chat_col = col
            elif '返点' in col_str:
                rebate_col = col

        if not nickname_col or not chat_col:
            raise ValueError("未找到必需的列：小红书昵称或聊天记录")

        # 过滤数据
        filtered_data = []
        for _, row in df.iterrows():
            # 检查返点列是否包含数字
            if rebate_col and pd.notna(row[rebate_col]):
                rebate_value = str(row[rebate_col]).strip()
                if re.search(r'\d', rebate_value):
                    continue

            # 检查必需字段是否为空
            if pd.isna(row[nickname_col]) or pd.isna(row[chat_col]):
                continue

            nickname = str(row[nickname_col]).strip()
            chat_record = str(row[chat_col]).strip()

            if nickname and chat_record:
                filtered_data.append({
                    "小红书昵称": nickname,
                    "聊天记录": chat_record
                })

        # 保存为JSON文件
        with open(output_file_path, 'w', encoding='utf-8') as f:
            json.dump(filtered_data, f, ensure_ascii=False, indent=2)

        print(f"成功提取 {len(filtered_data)} 条记录，已保存到 {output_file_path}")

    except Exception as e:
        print(f"处理失败: {str(e)}")


if __name__ == "__main__":
    input_path = r"D:\PycharmProjects\zc_project\agents_system\data\建联后的信息.xlsx"
    output_path = r"D:\PycharmProjects\zc_project\agents_system\data\jianlian.json"

    extract_excel_data(input_path, output_path)