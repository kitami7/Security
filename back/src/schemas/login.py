from src.schemas.base import BaseSchema

class Login(BaseSchema):
    email: str
    pw: str