import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from core.registry import registry
from agents.dispatch_agent import DispatchAgent
from agents.fill_agent import FillAgent
from agents.save_agent import SaveAgent
from core.unified_service import unified_service

from utils.logger import get_logger

logger = get_logger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    debug=settings.DEBUG
)

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册智能体
dispatch_agent = DispatchAgent()
fill_agent = FillAgent()
save_agent = SaveAgent()

registry.register("dispatch_agent", DispatchAgent)
registry.register("fill_agent", FillAgent)
registry.register("save_agent", SaveAgent)

# 将智能体路由添加到应用
app.include_router(dispatch_agent.router)
app.include_router(fill_agent.router)
app.include_router(save_agent.router)

# 添加统一服务路由
app.include_router(unified_service.router)

# 添加根路径
@app.get("/")
async def root():
    return {
        "message": "Welcome to Agents System",
        "version": settings.PROJECT_VERSION,
        "agents": registry.list_agents()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Agents System")
    uvicorn.run("main:app", host="0.0.0.0", port=8000)