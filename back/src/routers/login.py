from fastapi import APIRouter, Cookie, Depends, Form, HTTPException, Response, status
from typing import Annotated, Optional, Tuple
from src.config import Settings, get_settings
from src.dependencies.auth import get_cur_user, get_refresh_token_from_cookie
from src.repositories.user import UserRepo
from src.schemas.login import Login
from src.schemas.token import Token, TokenPayload
from aiomysql import Connection, DictCursor
from src.db import get_conn_and_cursor
from src.schemas.user import UserOut, UserOutDB
from src.security import verify_pw, create_access_token, create_refresh_token
from datetime import datetime, timedelta
import logging
from jose import jwt
from jose.exceptions import JWTError

router = APIRouter(
    prefix="",
    tags=["Login"]
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

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# ログイン
@router.post("/login", responses={
    200: {"description": "ログイン成功"},
    401: {"description": "認証失敗"},
    500: {"description": "サーバーエラー"}
})
async def login(
    response: Response,
    fd: Login,
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor)
):
    try:
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)

        user = await user_repo.get(fd.email)

        # メールアドレスをユーザーを検索
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが無効です",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # パスワードの検証
        if not verify_pw(fd.pw, user.pw):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="メールアドレスまたはパスワードが無効です",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # アクセストークンの生成
        access_token_and_exp: tuple[str, datetime] = create_access_token(
            payload=TokenPayload(
                sub=fd.email
            )
        )
        access_token, access_token_exp = access_token_and_exp

        # リフレッシュトークンの生成
        refresh_token_and_exp: tuple[str, datetime] = create_refresh_token(
            payload=TokenPayload(
                sub=fd.email
            )
        )
        refresh_token, refresh_token_exp = refresh_token_and_exp

        # クッキーにセット
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,
            expires=int(access_token_exp.timestamp())
        )
        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            secure=False,
            expires=int(refresh_token_exp.timestamp())
        )

        return {
            "msg": "ログインが成功しました"
        }


    except HTTPException as e:
        raise e
    except Exception as e:
        # 予期しないエラーが発生した場合は500エラーを返す
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="内部サーバーエラー",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
    
# ログアウト
@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {
        "msg": "Cookieが削除されました"
    }

@router.get("/me", response_model=UserOutDB)
async def get_own(cur_user: UserOutDB = Depends(get_cur_user)):
    print(cur_user)
    return cur_user

# リフレッシュ
@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token = Depends(get_refresh_token_from_cookie),
    settings: Settings = Depends(get_settings),
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor)
):
    try:
        print(refresh_token)
        # トークンを検証
        payload = jwt.decode(
            token=refresh_token,
            key=settings.TOKEN_SECRET_KEY,
            algorithms=settings.TOKEN_ALGORITHM
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        # ユーザーの存在を検証
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)
        user = user_repo.get(email=email)
        if user is None:
            raise credentials_exception

                # アクセストークンの生成
        access_token_and_exp: tuple[str, datetime] = create_access_token(
            payload=TokenPayload(
                sub=email
            )
        )
        access_token, access_token_exp = access_token_and_exp

        # リフレッシュトークンの生成
        refresh_token_and_exp: tuple[str, datetime] = create_refresh_token(
            payload=TokenPayload(
                sub=email
            )
        )
        refresh_token, refresh_token_exp = refresh_token_and_exp

        # トークンをCookieに格納
        response.set_cookie(
            key="access_tokenr",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=False,
            samesite="none",
            expires=int(access_token_exp.timestamp())
        )
        response.set_cookie(
            key="refresh_token",
            value=f"Bearer {refresh_token}",
            httponly=True,
            secure=False,
            samesite="none",
            expires=int(refresh_token_exp.timestamp())
        )

        return {
            "msg": "リフレッシュが成功しました"
        }


    except JWTError as err:
        raise credentials_exception

