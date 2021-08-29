from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    uid: UUID
    created_at: datetime  # ISO 8601
    name: str
    email: EmailStr

