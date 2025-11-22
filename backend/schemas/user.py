from pydantic import BaseModel

class UserRegister(BaseModel):
    email: str
    password: str
    nickname: str

class UserLogin(BaseModel):
    email: str
    password: str
