import pandas as pd

# 读取源Excel文件
input_file = r'D:\PycharmProjects\chat_jianlian\data_jianlian.xlsx'
output_file = r'D:\PycharmProjects\chat_jianlian\data_jianlian1.xlsx'

try:
    # 1. 读取Excel文件的前10行（保留原始读取逻辑）
    df = pd.read_excel(input_file, nrows=15000)

    # 2. 筛选掉“第一列”为null的行（第一列默认列名用 df.columns[0] 获取，适配任意列名）
    # dropna(subset=[列名]): 仅删除指定列中为null的行，其他列null不影响
    first_col_name = df.columns[0]  # 获取第一列的列名（无论原表第一列叫什么）
    df_filtered = df.dropna(subset=[first_col_name])

    # 3. 保存筛选后的数据到新Excel文件
    df_filtered.to_excel(output_file, index=False)

    # 打印结果信息
    print(f"成功读取前10行数据，筛选掉第一列（{first_col_name}）为null的行后，保存到 {output_file}")
    print(f"筛选前数据形状: {df.shape} (行:列)")
    print(f"筛选后数据形状: {df_filtered.shape} (行:列)")
    print(f"共筛选掉 {df.shape[0] - df_filtered.shape[0]} 行第一列为null的数据")
    if not df_filtered.empty:
        print("筛选后前几行数据预览:")
        print(df_filtered.head())

except FileNotFoundError:
    print(f"错误: 找不到文件 {input_file}")
except Exception as e:
    print(f"处理文件时出错: {e}")