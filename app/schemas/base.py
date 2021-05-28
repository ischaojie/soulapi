from datetime import datetime, timezone

from pydantic import BaseModel, validator


class DateTimeMixin(BaseModel):
    """DateTime Mixin for created time and updated time"""

    created_at: datetime = None
    updated_at: datetime = None

    @validator("created_at", "updated_at", pre=True, always=True)
    def default_datetime(cls, value):
        """auto complete datetime"""
        return value or datetime.now()

def convert_datetime_to_realworld(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class Msg(BaseModel):
    msg: str


class Lunar(BaseModel):
    date: str
    ganzhi_year: str
    ganzhi_month: str
    ganzhi_day: str
    shengxiao: str