from pydantic import BaseModel, EmailStr
from typing import List, Optional
from app.utils import get_password_hash


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    def to_dict(self):
        data = self.model_dump()
        data["hashed_password"] = get_password_hash(data.pop("password"))
        return data


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

    def to_dict(self):
        data = self.model_dump(exclude_none=True)
        if data.get("password", None):
            data["hashed_password"] = get_password_hash(data.pop("password"))
        return data


class User(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True
