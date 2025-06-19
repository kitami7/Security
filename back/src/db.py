import aiomysql
from aiomysql import Pool
from fastapi import HTTPException
from src.config import get_settings

pool: Pool = None

# データベース接続プールを初期化する関数
async def init_db_pool():
    global pool
    try:
        settings = get_settings()
        pool = await aiomysql.create_pool(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            db=settings.MYSQL_DB,
            minsize=1,
            maxsize=10,
            autocommit=True,
        )
    except Exception as e:
        print("データベース接続エラー")
        raise HTTPException(status_code=500, detail=f"Database connectionection error: {e}")

# 接続プールを取得する関数
def get_pool() -> Pool:
    global pool
    if pool is None:
        raise HTTPException(status_code=500, detail="Database connectionection pool is not initialized")
    return pool

# 接続とカーソルを取得する非同期ジェネレータ    
async def get_conn_and_cursor():
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            yield conn, cursor