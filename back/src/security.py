# fastapiのハッシュ化関数を使用して、パスワードのハッシュ化と検証を行います。
from fastapi import Depends
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from typing import Union
from datetime import timezone
from src.schemas.token import TokenPayload
from src.config import Settings, get_settings

# パスワードのハッシュ化と検証を行うためのコンテキストを作成
pw_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_pw(
    plain_pw: str,
    hashed_pw: str
) -> bool:
    """
    ハッシュ化されたパスワードと平文のパスワードを比較する関数
    :param plain_pw: 平文のパスワード
    :param hashed_pw: ハッシュ化されたパスワード
    :return: パスワードが一致する場合はTrue、一致しない場合はFalse
    """
    return pw_ctx.verify(plain_pw, hashed_pw)

def get_hashed_pw(pw: str) -> str:
    """
    パスワードをハッシュ化する関数
    :param pw: ハッシュ化するパスワード
    :return: ハッシュ化されたパスワード
    """
    return pw_ctx.hash(pw)

# アクセストークンを発行
def create_access_token(
    payload: TokenPayload
) -> tuple[str, datetime]:
    settings: Settings = get_settings()
    to_encode = payload.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_ACCESS_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)
    return encoded_jwt, expire

# リフレッシュトークンを発行
def create_refresh_token(
    payload: TokenPayload
) -> tuple[str, datetime]:
    to_encode = payload.model_dump()
    settings: Settings = get_settings()
    to_encode = payload.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_REFRESH_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.TOKEN_SECRET_KEY, settings.TOKEN_ALGORITHM)
    return encoded_jwt, expire

