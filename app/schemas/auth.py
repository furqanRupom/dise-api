from pydantic import BaseModel,EmailStr

class UserBase(BaseModel):
    name:str
    email:EmailStr


class Register(UserBase):
    password:str

class RegisterResponse(UserBase):
    id:int


class Login(BaseModel):
    email:EmailStr
    password:str

class TokenData(BaseModel):
    id:int
    role:str
    
class TokenFair(BaseModel):
    access_token:str
    refresh_token:str