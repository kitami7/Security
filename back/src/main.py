from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from src.routers import user, login

from src.db import init_db_pool, get_pool
import logging

# ログの設定
logger = logging.getLogger("orion2")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# スネークケースの文字列をキャメルケースに変換する関数
def snake_case_to_camel_case(snake_case_str: str) -> str:
    components = snake_case_str.split("_")
    return components[0] + "".join(x.title() for x in components[1:])

# 操作IDをルート名として使用するための関数
def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = snake_case_to_camel_case(route.name)
# 初期化
async def init_app():
    await init_db_pool()
    logger.info("init_app: データベースコネクションプールが初期化されました")

# 終了
async def close_app():
    try:
        pool = get_pool()
        logger.debug(f"close_app: プールの状態: {pool}")
        if pool:
            pool.close()
            await pool.wait_closed()
            logger.info("データベースコネクションプールが正常に閉じられました")
        else:
            logger.info("データベースコネクションプールは初期化されていません")
    except Exception as e:
        logger.error(f"データベースコネクションプールのクローズ中にエラーが発生しました: {e}")

# FastAPIのライフサイクルイベントを使用して、アプリケーションの初期化と終了処理を行います。
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_app()
    try:
        yield
    finally:
        await close_app()

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_credentials=True,
    allow_headers=["*"]
)

# ルーターのインポート
app.include_router(user.router)
app.include_router(login.router)

# 操作IDをルート名として使用する
use_route_names_as_operation_ids(app)