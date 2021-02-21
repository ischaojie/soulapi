from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator, EmailStr


def convert_datetime_to_realworld(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class DateTimeMixin(BaseModel):
    """DateTime Mixin for created time and updated time"""
    created_at: datetime = None
    updated_at: datetime = None

    @validator("created_at", "updated_at", pre=True, always=True)
    def default_datetime(cls, value):
        """auto complete datetime"""
        return value or datetime.now()


class PsychologyClassifyEnum(str, Enum):
    normal = 'normal'  # 普通心理学
    experiment = 'experiment'  # 实验心理学
    education = 'education'  # 教育心理学
    society = 'society'  # 社会心理学


class PsychologyBase(DateTimeMixin):
    classify: PsychologyClassifyEnum
    knowledge: str


class PsychologyCreate(PsychologyBase):
    pass


class PsychologyUpdate(PsychologyBase):
    pass


class Psychology(PsychologyBase):
    id: int

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_realworld}


# User schemas

# Shared properties
class UserBase(DateTimeMixin):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    is_confirm: bool = False
    full_name: Optional[str] = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


# token schemas

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None


class Msg(BaseModel):
    msg: str
