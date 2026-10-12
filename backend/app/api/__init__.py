"""
Creative Radar — API 路由注册

聚合所有 API 模块。
"""
from fastapi import APIRouter

from .items import router as items_router
from .cards import router as cards_router
from .favorites import router as favorites_router
from .search import router as search_router
from .sources import router as sources_router
from .settings import router as settings_router
from .collect import router as collect_router
from .email import router as email_router

main = APIRouter()

# 数据采集
main.include_router(collect_router, prefix="/collect", tags=["collect"])

# 数据列表
main.include_router(items_router, prefix="/items", tags=["items"])

# AI 卡片
main.include_router(cards_router, prefix="/cards", tags=["cards"])

# 收藏
main.include_router(favorites_router, prefix="/favorites", tags=["favorites"])

# 搜索
main.include_router(search_router, prefix="/search", tags=["search"])

# 数据源
main.include_router(sources_router, prefix="/sources", tags=["sources"])

# 邮件
main.include_router(email_router, prefix="/email", tags=["email"])

# 配置
main.include_router(settings_router, prefix="/settings", tags=["settings"])
