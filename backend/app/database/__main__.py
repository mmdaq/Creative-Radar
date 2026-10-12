"""
Creative Radar — 数据库初始化入口

用法：
    cd backend
    python -m app.database
"""
from backend.app.database.database import init_db

if __name__ == "__main__":
    init_db()
