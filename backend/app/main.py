"""
Creative Radar — FastAPI 后端入口
"""
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import main as api_router
from .config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="Creative Radar API",
        version="0.1.0",
        description="每日创意情报 + 灵感学习卡片 + 邮件推送系统",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    app.include_router(api_router, prefix="/api")

    @app.get("/")
    def root():
        return {"name": "Creative Radar", "version": "0.1.0", "status": "ok"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
