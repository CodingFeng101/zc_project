#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from typing import Dict, List, Any
from collections import Counter


def extract_tags_from_prompt() -> List[str]:
    """
    从提示词文件中提取所有标签

    :return: 标签列表
    """
    # 定义标签体系（基于提示词文件内容的108个细化标签）
    tags = [
        "全程未提返点-因博主无推广经验终止",
        "全程未提返点-因博主对产品无兴趣终止",
        "全程未提返点-仅停留在合作邀请无后续",
        "全程未提返点-信息索取不含返点字段",
        "智能体未主动引返点-聚焦内容细节",
        "智能体未主动引返点-聚焦账号审核",
        "智能体未主动引返点-聚焦品牌介绍",
        "智能体未主动引返点-聚焦合作流程",
        "博主提返点后未承接-智能体转移至信息索取",
        "博主提返点后未承接-智能体转移至合作要求",
        "博主提返点后未承接-智能体沉默无回应",
        "博主提返点后未承接-智能体答非所问",
        "返点议题中途中断-智能体突然结束对话",
        "返点议题中途中断-智能体跳转至等通知",
        "返点议题中途中断-因信任争议搁置",
        "返点议题中途中断-智能体切换博主对接",
        "返点需求触达-信息待补充-博主仅礼貌回应",
        "返点需求触达-信息待补充-博主重复问合作方式",
        "返点需求触达-信息待补充-博主无任何回应",
        "返点需求触达-信息待补充-博主仅反馈非返点信息",
        "返点需求触达-博主疑问合作-问内容要求",
        "返点需求触达-博主疑问合作-问推广形式",
        "返点需求触达-博主疑问合作-问产品细节",
        "返点需求触达-博主疑问合作-问合作风险",
        "返点需求触达-沟通无效中断-博主用不文明用语",
        "返点需求触达-沟通无效中断-博主明确拒填",
        "返点需求触达-沟通无效中断-博主答非所问",
        "返点需求触达-沟通无效中断-博主发无意义表情",
        "返点比例低于预期-博主报具体比例被拒",
        "返点比例低于预期-博主报区间比例被拒",
        "返点比例低于预期-博主对比过往合作被拒",
        "返点比例低于预期-博主对比同行被拒",
        "返点基数计算争议-销售额vs净利润",
        "返点基数计算争议-税前vs税后",
        "返点基数计算争议-总GMVvs扣退款GMV",
        "返点基数计算争议-单品vs全品类销售额",
        "结算周期过长-月结vs季结",
        "结算周期过长-30天vs60天账期",
        "结算周期过长-达标后立即结vs固定日结",
        "结算周期过长-短期合作即时结vs分期结",
        "阶梯返点门槛太高-销量门槛",
        "阶梯返点门槛太高-曝光门槛",
        "阶梯返点门槛太高-转化门槛",
        "阶梯返点门槛太高-复购门槛",
        "返点形式不接受-货补vs现金",
        "返点形式不接受-分期返vs一次性返",
        "返点形式不接受-虚拟权益vs现金",
        "返点形式不接受-股权vs现金",
        "返点协商博弈-智能体要求提比例博主小幅让步",
        "返点协商博弈-智能体绑定附加量博主拒",
        "返点协商博弈-博主提比例智能体小幅让步未达预期",
        "返点协商博弈-双方互不让步",
        "返点规则未明确-未说计算方式",
        "返点规则未明确-未说达标条件",
        "返点规则未明确-未说结算节点",
        "返点规则未明确-未说比例梯度",
        "数据统计争议-品牌后台vs博主后台",
        "数据统计争议-第三方工具vs平台原生",
        "数据统计争议-自然流量vs含付费",
        "数据统计争议-点击量vs成交量",
        "退单扣返点争议-未说扣点比例",
        "退单扣返点争议-未说追溯期",
        "退单扣返点争议-已结返点是否追回",
        "退单扣返点争议-部分退单是否按比例扣",
        "返点附加条件未提前说-后期提独家合作",
        "返点附加条件未提前说-后期提多笔记",
        "返点附加条件未提前说-后期提投流要求",
        "返点附加条件未提前说-后期提售后维护",
        "返点有效期太短-按天算",
        "返点有效期太短-按周算",
        "返点有效期太短-按活动周期算",
        "担心返点不兑现-质疑品牌支付能力",
        "担心返点不兑现-质疑智能体权限",
        "担心返点不兑现-质疑行业口碑",
        "无返点协议保障-仅口头约定",
        "无返点协议保障-协议不含返点条款",
        "无返点协议保障-协议后补",
        "过往案例无说服力-无具体数据",
        "过往案例无说服力-无真实账号",
        "过往案例无说服力-案例领域不符",
        "数据不透明顾虑-无实时查看权",
        "数据不透明顾虑-无明细",
        "数据不透明顾虑-无第三方审计",
        "品牌资质影响信任-成立时间短",
        "品牌资质影响信任-无行业认证",
        "品牌资质影响信任-有负面",
        "博主提诉求直接拒-拒提返点比例",
        "博主提诉求直接拒-拒缩结算周期",
        "博主提诉求直接拒-拒改返点形式",
        "异议回应态度敷衍-模板话术",
        "异议回应态度敷衍-模糊话术",
        "异议回应态度敷衍-推卸责任",
        "无替代方案妥协-仅让再考虑",
        "无替代方案妥协-仅让等通知",
        "无替代方案妥协-仅让降诉求",
        "反驳博主诉求-否定粉丝价值",
        "反驳博主诉求-否定过往业绩",
        "反驳博主诉求-否定诉求合理性",
        "返点与其他权益绑定争议-绑定流量扶持",
        "返点与其他权益绑定争议-绑定样品购买",
        "返点与其他权益绑定争议-绑定售后",
        "跨平台返点差异-对比抖音",
        "跨平台返点差异-对比微博",
        "跨平台返点差异-对比私域",
        "新人博主返点歧视-同粉丝量低于成熟号",
        "返点扣税争议-未提前说扣税",
        "返点扣税争议-对扣税比例有异议",
        "返点扣税争议-对扣税方式有异议",
        "返点相关-未达成一致",
        "返点相关-博主拒绝返点但有其他权益",
        "返点相关-博主提出返点要求待确认",
        "返点相关-智能体要求45%以上返点博主有不同回应",
        "返点相关-博主不知返点含义或填写数值问题",
        "返点相关-智能体邀博主合作返点待确定",
        "无返点关联-博主因各种非返点原因拒绝合作",
        "无返点关联-智能体邀博主合作未涉及返点沟通",
        "无返点关联-未进行返点沟通相关情况",
        "无返点关联-智能体提交合作信息无返点沟通",
        "返点相关-博主提出返点由机构负责获认可",
        "返点相关 - 未达成一致",
        "返点相关 - 博主拒绝返点但有其他权益",
        "返点相关 - 博主提出返点要求待确认",
        "返点相关 - 智能体要求45%以上返点博主有不同回应",
        "返点相关 - 博主不知返点含义或填写数值问题",
        "返点相关 - 智能体邀博主合作返点待确定",
        "无返点关联 - 博主因各种非返点原因拒绝合作",
        "无返点关联 - 智能体邀博主合作未涉及返点沟通",
        "无返点关联 - 未进行返点沟通相关情况",
        "无返点关联 - 智能体提交合作信息无返点沟通",
        "返点相关 - 博主提出返点由机构负责获认可"
    ]

    return tags


def analyze_tag_statistics(file_path: str) -> Dict[str, Any]:
    """
    分析返点识别测试结果中的标签统计

    :param file_path: JSON文件路径
    :return: 标签统计分析结果
    """
    try:
        # 读取JSON文件
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 获取标准标签列表
        standard_tags = extract_tags_from_prompt()

        # 统计变量
        tag_counts = Counter()
        total_conversations = 0
        missing_tag_conversations = []

        # 处理嵌套的数据结构
        conversations = []
        if isinstance(data, list) and len(data) > 0:
            # 检查是否是测试结果格式
            if 'api_response' in data[0] and 'processed_conversations' in data[0]['api_response']:
                for test_result in data:
                    if 'api_response' in test_result and test_result['api_response']:
                        conversations.extend(test_result['api_response'].get('processed_conversations', []))
            else:
                conversations = data
        
        # 遍历所有对话
        for conversation in conversations:
            total_conversations += 1

            # 提取标签字段（扁平化结构）
            tag = conversation.get('标签', '')
            reason = conversation.get('原因', '')

            # 统计标签
            if tag:
                tag_counts[tag] += 1

            # 识别标签缺陷情况（标签为"无标签适合"或不在标准标签列表中）
            if (tag == "无标签适合" or tag not in standard_tags):
                missing_tag_conversations.append({
                    '小红书昵称': conversation.get('小红书昵称', ''),
                    '原因': reason,
                    '标签': tag,
                    '聊天记录': conversation.get('聊天记录', '')
                })

        # 将标签统计按出现次数从大到小排序
        sorted_tag_statistics = dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True))
        
        return {
            'total_conversations': total_conversations,
            'tag_statistics': sorted_tag_statistics,
            'standard_tags': standard_tags,
            'missing_tag_conversations': missing_tag_conversations,
            'missing_tag_count': len(missing_tag_conversations)
        }

    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return {}


def print_tag_analysis(result: Dict[str, Any]) -> None:
    """
    打印标签分析结果（按出现次数从大到小排序）

    :param result: 分析结果字典
    """
    print("标签出现频率统计（按次数从大到小排序）:")
    tag_stats = result['tag_statistics']
    for tag, count in sorted(tag_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"{tag}: {count}次")
    
    print(f"\n没有合适标签的对话数量: {result['missing_tag_count']}条")


def print_tag_defect_analysis(result: Dict[str, Any]) -> None:
    """
    打印没有合适标签的对话

    :param result: 分析结果字典
    """
    if result['missing_tag_conversations']:
        print("\n没有合适标签的对话:")
        for i, conv in enumerate(result['missing_tag_conversations'], 1):
            print(f"\n{i}. 昵称: {conv['小红书昵称']}")
            print(f"   原因: {conv['原因']}")
            print(f"   标签: {conv['标签']}")
            print(f"   聊天记录: {conv['聊天记录']}")


def analyze_json_file_tags(json_file_path: str) -> Dict[str, Any]:
    """
    统计JSON文件中所有标签出现次数、无合适标签的聊天记录及数量
    
    :param json_file_path: JSON文件路径
    :return: 统计结果字典
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取标准标签列表
        standard_tags = extract_tags_from_prompt()
        
        # 统计所有标签出现次数
        tag_counts = Counter()
        missing_tag_conversations = []
        
        # 如果是tag_analysis_results.json格式
        if 'tag_statistics' in data:
            tag_counts.update(data['tag_statistics'])
            missing_tag_conversations = data.get('missing_tag_conversations', [])
        else:
            # 如果是其他格式，遍历数据统计
            for item in data:
                if isinstance(item, dict):
                    tag = item.get('标签', '')
                    if tag:
                        tag_counts[tag] += 1
                        if tag == "无标签适合" or tag not in standard_tags:
                            missing_tag_conversations.append({
                                '小红书昵称': item.get('小红书昵称', ''),
                                '原因': item.get('原因', ''),
                                '标签': tag,
                                '聊天记录': item.get('聊天记录', '')
                            })
        
        return {
            'tag_statistics': dict(tag_counts),
            'missing_tag_conversations': missing_tag_conversations,
            'missing_tag_count': len(missing_tag_conversations)
        }
        
    except Exception as e:
        print(f"读取文件时发生错误: {str(e)}")
        return {}


def extract_high_frequency_tags(input_file: str, output_file: str, min_count: int = 10) -> Dict[str, Any]:
    """
    提取出现次数不低于指定次数的标签及其对应的聊天记录
    
    :param input_file: 输入JSON文件路径
    :param output_file: 输出JSON文件路径
    :param min_count: 最小出现次数阈值
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 统计每个标签的出现次数和对应的聊天记录
        tag_conversations = {}
        tag_counts = {}
        
        # 处理嵌套的数据结构
        conversations = []
        if isinstance(data, list) and len(data) > 0:
            # 检查是否是测试结果格式
            if 'api_response' in data[0] and 'processed_conversations' in data[0]['api_response']:
                conversations = data[0]['api_response']['processed_conversations']
            else:
                conversations = data
        
        for item in conversations:
            tags = item.get('标签', [])
            if isinstance(tags, str):
                tags = [tags]
            
            for tag in tags:
                if tag and tag != "无合适标签":
                    if tag not in tag_conversations:
                        tag_conversations[tag] = []
                        tag_counts[tag] = 0
                    
                    tag_conversations[tag].append({
                        '小红书昵称': item.get('小红书昵称', ''),
                        '原因': item.get('原因', ''),
                        '标签': item.get('标签', []),
                        '聊天记录': item.get('聊天记录', '')
                    })
                    tag_counts[tag] += 1
        
        # 筛选出现次数不低于min_count的标签
        high_frequency_tags = {}
        for tag, count in tag_counts.items():
            if count >= min_count:
                high_frequency_tags[tag] = {
                    'count': count,
                    'conversations': tag_conversations[tag]
                }
        
        # 按出现次数从大到小排序
        sorted_high_frequency_tags = dict(
            sorted(high_frequency_tags.items(), key=lambda x: x[1]['count'], reverse=True)
        )
        
        result = {
            'min_count_threshold': min_count,
            'total_high_frequency_tags': len(sorted_high_frequency_tags),
            'high_frequency_tags': sorted_high_frequency_tags
        }
        
        # 保存到JSON文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return result
        
    except Exception as e:
        print(f"处理文件时发生错误: {e}")
        return {}


def main():
    """主函数"""
    # 输入文件路径
    input_file = r"d:\PycharmProjects\zc_project\agents_system\data\output\rebate_identification_test_results.json"
    # 输出文件路径
    output_file = r"d:\PycharmProjects\zc_project\agents_system\utils\tag_analysis_results.json"
    # 高频标签输出文件路径
    high_frequency_output_file = r"d:\PycharmProjects\zc_project\agents_system\utils\high_frequency_tags.json"

    try:
        print(f"正在分析文件: {input_file}")
        result = analyze_tag_statistics(input_file)

        if result:
            # 输出标签统计到控制台
            print("\n标签出现频率统计（按次数从大到小排序）:")
            tag_stats = result['tag_statistics']
            for tag, count in sorted(tag_stats.items(), key=lambda x: x[1], reverse=True):
                print(f"{tag}: {count}次")

            print(f"\n没有合适标签的对话数量: {result['missing_tag_count']}条")

            # 保存结果到JSON文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"\n统计结果已保存到: {output_file}")
            
            # 提取高频标签及其对应的聊天记录
            print("\n正在提取出现次数不低于10次的标签...")
            high_freq_result = extract_high_frequency_tags(input_file, high_frequency_output_file, 10)
            
            if high_freq_result:
                print(f"\n找到 {high_freq_result['total_high_frequency_tags']} 个出现次数不低于10次的标签")
                print(f"高频标签数据已保存到: {high_frequency_output_file}")
                
                # 显示高频标签统计
                print("\n高频标签统计:")
                for tag, data in high_freq_result['high_frequency_tags'].items():
                    print(f"{tag}: {data['count']}次 (包含{len(data['conversations'])}条聊天记录)")
            
            # 输出部分无合适标签的对话示例
            if result['missing_tag_conversations']:
                print("\n无合适标签的对话示例（前5条）:")
                for i, conv in enumerate(result['missing_tag_conversations'][:5], 1):
                    print(f"\n{i}. 昵称: {conv['小红书昵称']}")
                    print(f"   原因: {conv['原因']}")
                    print(f"   标签: {conv['标签']}")
                    print(f"   聊天记录: {conv['聊天记录'][:100]}...")
                    
        else:
            print("分析失败，请检查文件路径和格式")
            
    except FileNotFoundError:
        print(f"文件不存在: {input_file}")
    except Exception as e:
        print(f"处理文件时发生错误: {e}")


if __name__ == "__main__":
    main()
