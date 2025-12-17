from pydantic import BaseModel
from datetime import datetime
from fastapi_users import schemas
import uuid


# Schemas de usuario para fastapi-users
class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


# Schemas de Post
class PostCreate(BaseModel):
    caption: str
    url: str
    file_type: str
    file_name: str


class PostResponse(BaseModel):
    id: str
    caption: str
    url: str
    file_type: str
    file_name: str
    created_at: datetime
    user_id: str

    class Config:
        from_attributes = True