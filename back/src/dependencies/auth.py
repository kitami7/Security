from typing import Tuple
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from aiomysql import Connection, DictCursor
from jose.exceptions import JWTError
import logging

from src.config import Settings, get_settings
from src.db import get_conn_and_cursor
from src.repositories.user import UserRepo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# ロガーの初期化
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# ログ出力フォーマットの設定
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# コンソールへの出力ハンドラー
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# アクセストークンをクッキーから取得
def get_access_token_from_cookie(
    access_token: str | None = Cookie(default=None)
):
    # 最初にアクセストークンがない場合に例外を出す
    if access_token is None:
        raise credentials_exception

    # 次にBearerでない場合に例外を出す
    if not access_token.startswith("Bearer "):
        raise credentials_exception

    # Bearerトークンを取り除く
    access_token = access_token[len("Bearer "):]
    return access_token

# リフレッシュトークンをクッキーから取得
def get_refresh_token_from_cookie(
    refresh_token: str | None = Cookie(default=None)
):
    # 最初にリフレッシュトークンがない場合に例外を出す
    if refresh_token is None:
        raise credentials_exception

    # 次にBearerでない場合に例外を出す
    if not refresh_token.startswith("Bearer "):
        raise credentials_exception

    # Bearerトークンを取り除く
    refresh_token = refresh_token[len("Bearer "):]
    return refresh_token

# 現在のユーザー情報を取得する
async def get_cur_user(
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor),
    settings: Settings = Depends(get_settings),    
    token: str = Depends(get_access_token_from_cookie)
):
    try:
        # トークンをデコード（有効期限も自動敵に検証する）
        payload = jwt.decode(
            token=token,
            key=settings.TOKEN_SECRET_KEY,
            algorithms=settings.TOKEN_ALGORITHM
        )
        email = payload.get("sub")

        # メール番号があるか検証
        if email is None:
            logger.warning(f"Authentication failed: Missing email in token. Token: {token}")
            raise credentials_exception
        
        # ユーザーを検証
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)
        user = await user_repo.get(email=email)
        if not user:
            logger.warning(f"Authentication failed: User not found for email: {email}")
            raise credentials_exception
        
        return user
    except JWTError as err:
        logger.warning(f"Authentication failed: Invalid token. Error: {err}. Token: {token}")
        raise credentials_exception
