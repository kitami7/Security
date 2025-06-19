from typing import Tuple
from aiomysql import Connection, DictCursor
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from src.dependencies.auth import get_cur_user
from src.schemas.user import UserInDB, UserOut, UserInCreate, UserInUpdate, UserOutDB
from src.repositories.user import UserRepo
from src.security import get_hashed_pw
from src.db import get_conn_and_cursor

# ユーザー情報を管理するためのFastAPIルーターを定義します。
# このルーターは、ユーザーのCRUD操作を提供します。
# ユーザー情報の取得、作成、更新、削除を行うエンドポイントを含みます。
# ルーターのパスは "/users" で、タグは "user" です。
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ユーザー情報を取得するエンドポイント
@router.get("/{email}", responses={
    200: {"description": "ユーザー一覧取得", "model": UserOut},
    404: {"description": "ユーザーが存在しません"},
    500: {"description": "サーバーエラー"}
})
async def get_user(
    email: str,
    user = Depends(get_cur_user),
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor)
) -> UserOut:
    try:
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)
        user = await user_repo.get(email)
   
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ユーザー：{email} は存在しません"
            )
        
        return UserOut(
            email=user.email,
            pw=user.pw
        )
    
    except HTTPException as err:
        raise err
    
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サーバーエラー: {err}"
        )

# ユーザー情報の一覧を取得するエンドポイント
@router.get("/", responses={
    200: {"description": "List of users", "model": list[UserOut]},
    404: {"description": "No users found"},
    500: {"description": "サーバーエラー"}
})
async def get_users(
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor),
    user = Depends(get_cur_user)
) -> list[UserOut]:
    try:
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)
        users = await user_repo.get_all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが存在しません"
            )
        
        return [UserOut(email=user.email, pw=user.pw) for user in users]
    
    except HTTPException as err:
        raise err
    
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サーバーエラー: {err}"
        )

# ユーザーを作成するエンドポイント
@router.post("/", responses={
    201: {"description": "ユーザーが正常に作成されました"},
    400: {"description": "このメールアドレスは既に登録されています"},
    500: {"description": "サーバーエラー"}   
})
async def create_user(
    user_in: UserInCreate,
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor)
):
    try:
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)

        user = await user_repo.get(user_in.email)
        
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="このメールアドレスは既に登録されています"
            )
        
        await user_repo.create(UserInDB(
            email=user_in.email,
            pw=get_hashed_pw(user_in.pw)
        ))

        await conn.commit()
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": "ユーザーが正常に作成されました"}
        )
    
    except HTTPException as err:
        raise err
    
    except Exception as err:
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サーバーエラー: {err}"
        )

# ユーザーを削除するエンドポイント
@router.delete("/{email}", responses={
    200: {"description": "ユーザーが正常に削除されました"},
    404: {"description": "ユーザーが存在しません"},
    500: {"description": "サーバーエラー"}
})
async def delete_user(
    email: str,
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor)
):
    try:
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)
        
        user = await user_repo.get(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ユーザー：{email} は存在しません"
            )
        
        await user_repo.delete(email)
        await conn.commit()
        
        return {"message": f"ユーザー：{email} が正常に削除されました"}
    
    except HTTPException as err:
        raise err
    
    except Exception as err:
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サーバーエラー: {err}"
        )

# ユーザー情報を更新するエンドポイント
@router.put("/{email}", responses={
    200: {"description": "ユーザーが正常に更新されました"},
    404: {"description": "ユーザーが存在しません"},
    500: {"description": "サーバーエラー"}
})
async def update_user(
    email: str,
    user_in: UserInUpdate,
    conn_cursor: Tuple[Connection, DictCursor] = Depends(get_conn_and_cursor)
):
    try:
        conn, cursor = conn_cursor
        user_repo = UserRepo(cursor)
        
        user = await user_repo.get(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ユーザー：{email} は存在しません"
            )
                
        await user_repo.update(UserInDB(
            email=email,
            pw=user_in.pw
        ))

        await conn.commit()
        
        return {"message": f"ユーザー：{email} が正常に更新されました"}
    
    except HTTPException as err:
        raise err
    
    except Exception as err:
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"サーバーエラー: {err}"
        )