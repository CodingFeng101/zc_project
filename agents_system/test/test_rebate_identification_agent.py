#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import aiohttp

from agents_system.utils.logger import get_logger

logger = get_logger(__name__)


class RebateIdentificationAgentTester:
    """返点识别智能体测试类"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_endpoint = f"{base_url}/rebateidentification/identify-rebate"
        self.test_results: List[Dict[str, Any]] = []

    def load_test_data(self, file_path: str, limit: int = 500) -> List[Dict[str, str]]:
        """
        加载测试数据

        :param file_path: 数据文件路径
        :param limit: 限制加载的数据条数
        :return: 测试数据列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 取前limit条数据
            test_data = data[:limit] if len(data) > limit else data
            logger.info(f"成功加载 {len(test_data)} 条测试数据")
            return test_data
        except Exception as e:
            logger.error(f"加载测试数据失败: {str(e)}")
            return []

    async def test_api_endpoint(self, conversations: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        通过HTTP请求测试API端点

        :param conversations: 对话数据
        :return: 测试结果
        """
        start_time = time.time()
        
        try:
            # 准备请求数据
            request_data = {"conversations": conversations}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_endpoint,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
            end_time = time.time()
            processing_time = end_time - start_time
            
            test_result = {
                "test_type": "api_endpoint",
                "timestamp": datetime.now().isoformat(),
                "input_count": len(conversations),
                "processing_time_seconds": processing_time,
                "success": response.status == 200,
                "status_code": response.status,
                "api_response": response_data
            }
            
            logger.info(f"API端点测试完成，处理 {len(conversations)} 条数据，耗时 {processing_time:.2f} 秒，状态码: {response.status}")
            return test_result
            
        except Exception as e:
            end_time = time.time()
            processing_time = end_time - start_time
            
            test_result = {
                "test_type": "api_endpoint",
                "timestamp": datetime.now().isoformat(),
                "input_count": len(conversations),
                "processing_time_seconds": processing_time,
                "success": False,
                "error": str(e),
                "api_response": None
            }
            
            logger.error(f"API端点测试失败: {str(e)}")
            return test_result

    async def run_all_tests(self, data_file_path: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        运行所有测试

        :param data_file_path: 测试数据文件路径
        :param limit: 数据限制条数
        :return: 所有测试结果
        """
        logger.info("开始RebateIdentificationAgent测试")
        
        # 加载测试数据
        test_data = self.load_test_data(data_file_path, limit)
        
        if not test_data:
            logger.error("没有可用的测试数据")
            return []
        
        # 测试API端点
        api_result = await self.test_api_endpoint(test_data)
        self.test_results.append(api_result)
        
        logger.info("RebateIdentificationAgent测试完成")
        return self.test_results

    def save_results(self, output_file: str) -> None:
        """
        保存测试结果

        :param output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            logger.info(f"测试结果已保存到: {output_file}")
        except Exception as e:
            logger.error(f"保存测试结果失败: {str(e)}")


async def main():
    """主测试函数"""
    tester = RebateIdentificationAgentTester()
    
    # 运行测试
    data_file = r"D:\PycharmProjects\zc_project\agents_system\data\output\conversation_processor_test_results.json"
    results = await tester.run_all_tests(data_file, limit=1000)
    
    # 保存结果
    output_file = r"D:\PycharmProjects\zc_project\agents_system\data\output\rebate_identification_test_results.json"
    tester.save_results(output_file)
    
    return results


if __name__ == "__main__":
    asyncio.run(main())