from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: int | str | None = None

class Login(BaseModel):
    username: str
    password: str
