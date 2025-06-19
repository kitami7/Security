from .base import BaseSchema

class UserInDB(BaseSchema):
    email: str
    pw: str

class UserOutDB(BaseSchema):
    email: str
    pw: str

class UserOut(BaseSchema):
    email: str
    pw: str

class UserInUpdate(BaseSchema):
    pw: str

class UserInCreate(BaseSchema):
    email: str
    pw: str