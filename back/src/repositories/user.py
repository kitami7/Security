from aiomysql import DictCursor

from src.schemas.user import UserOutDB, UserInDB

# UserRepo クラスは、ユーザー情報のデータベース操作を行うリポジトリです。
class UserRepo:

    def __init__(
        self,
        cur: DictCursor
    ):
        self.cur = cur

    # ユーザー取得
    async def get(
        self,
        email: str
    ) -> UserOutDB:
        
        sql = """
            SELECT
                email,
                pw
            FROM
                users
            WHERE
                email = %(email)s
        """

        await self.cur.execute(sql, {
            "email": email
        })

        row =  await self.cur.fetchone()
 
        if not row:
            return None
        
        return UserOutDB(**row)
    
    # ユーザー全件取得
    async def get_all(
        self
    ) -> list[UserOutDB]:
        
        sql = """
            SELECT
                email,
                pw
            FROM
                users
        """

        await self.cur.execute(sql)

        rows = await self.cur.fetchall()

        if not rows:
            return []

        return [UserOutDB(**row) for row in rows]

    # ユーザー作成
    async def create(
        self,
        user: UserInDB
    ) -> None:
        
        sql = """
            INSERT INTO users (
                email,
                pw
            ) VALUES (
                %(email)s,
                %(pw)s
            )
        """

        await self.cur.execute(
            sql, user.model_dump()
        )

    # ユーザー更新
    async def update(
        self,
        user: UserInDB
    ) -> None:
        
        sql = """
            UPDATE users
            SET
                pw = %(pw)s
            WHERE
                email = %(email)s
        """

        await self.cur.execute(
            sql, user.model_dump()
        )
    
    # ユーザー削除
    async def delete(
        self,
        email: str
    ) -> None:
        
        sql = """
            DELETE FROM users
            WHERE
                email = %(email)s
        """

        await self.cur.execute(
            sql, {
                "email": email
            }
        )