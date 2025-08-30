#backend/src/auth/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleOut(RoleBase):
    id: int

    class Config:
        orm_mode = True

# Base schema for user, shared attributes
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    role_id: Optional[int] = None

# This schema is used for creating new users, includes password and role_id
class UserCreate(UserBase):
    password: str
    role_id: int

# This schema is used for reading user data, excluding sensitive information like password
class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    role: Optional[RoleOut] = None

    class Config:
        orm_mode = True

# This schema is used for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


#this will handle the JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"