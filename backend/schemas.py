from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class ProfileBase(BaseModel):
    age_group: Optional[str] = None
    gender: Optional[str] = None
    language: Optional[str] = None

class ProfileCreate(ProfileBase):
    user_id: int

class ProfileResponse(ProfileBase):
    id: int
    user_id: int

class ProfileUpdate(ProfileBase):
    pass

    class Config:
        orm_mode = True
