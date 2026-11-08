import datetime
from typing import List, Optional
from pydantic import BaseModel


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str
    is_active: bool = True
    smart_card_uid: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role_names: List[str] = ["Operator"]


class UserResponse(UserBase):
    id: int
    is_superuser: bool
    created_at: datetime.datetime
    roles: List[str] = []

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class SmartCardLoginRequest(BaseModel):
    smart_card_uid: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
