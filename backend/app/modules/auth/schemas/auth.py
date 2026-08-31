
from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username:str
    email:str
    password:str
    role:str

class LoginRegister(BaseModel):
    email:str
    password:str