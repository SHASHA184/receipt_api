from pydantic import BaseModel
from typing import List


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class User(UserCreate):
    id: int

    class Config:
        from_attributes = True