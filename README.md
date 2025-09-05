# Agents System

一个基于豆包大模型的智能代理系统，用于中餐相关的问答、信息填充和数据保存等任务。

## 项目概述

Agents System 是一个多代理协作的智能系统，主要功能包括：
- 调度代理（Dispatch Agent）：负责任务分发和路由
- 填充代理（Fill Agent）：负责信息补全和数据填充
- 全局问答代理（Global QA Agent）：处理通用问答任务
- 保存代理（Save Agent）：负责数据持久化存储

## 项目结构

```
agents_system/
├── main.py                    # 主入口文件
├── requirements.txt           # 依赖包列表
├── config/
│   └── settings.py           # 配置文件
├── agents/                   # 代理模块
│   ├── dispatch_agent.py     # 调度代理
│   ├── fill_agent.py         # 填充代理
│   ├── globalqaagent.py      # 全局问答代理
│   └── save_agent.py         # 保存代理
├── core/                     # 核心模块
│   ├── base_agent.py         # 基础代理类
│   ├── registry.py           # 代理注册器
│   └── unified_service.py    # 统一服务
├── models/
│   └── doubao.py            # 豆包模型封装
├── utils/                    # 工具模块
│   ├── logger.py            # 日志工具
│   └── similarity_retrieve.py # 相似度检索
├── data/
│   └── qa.sql               # 问答数据
└── logs/                    # 日志目录
```

## 快速开始

### 环境要求

- Python 3.8+
- MySQL 数据库
- 豆包大模型 API 访问权限

### 安装依赖

```bash
pip install -r requirements.txt
```

### 环境配置

1. 复制环境变量模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，配置以下参数：

```env
# 项目基本信息
PROJECT_NAME=Agents System
PROJECT_VERSION=1.0.0
DEBUG=False

# 豆包大模型配置
DOUBAO_API_KEY=your_doubao_api_key_here
DOUBAO_MODEL_NAME=doubao-1-5-pro-32k-250115

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/agents_system.log

# 嵌入模型配置
EMBEDDING_MODEL=doubao-embedding-large-text-250515
```


### 运行项目

```bash
python main.py
```
