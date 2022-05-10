from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field

# Shared properties
class UserBase(BaseModel):
    username: str | None
    email: EmailStr | None = None
    full_name: str | None = None
    is_admin: bool = False


# Properties to receive via API on creation
class UserCreate(UserBase):
    username: str
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str | None = None


class UserInDBBase(UserBase):
    uuid: UUID = Field(default_factory=uuid4)


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_pw: str
