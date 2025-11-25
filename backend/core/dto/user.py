from pydantic import BaseModel
from uuid import UUID


class BaseUserSchema(BaseModel):
    id: UUID
    email: str
    username: str

