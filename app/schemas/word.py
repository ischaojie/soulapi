# Word schemas
from datetime import datetime

from .base import DateTimeMixin, convert_datetime_to_realworld
from typing import Optional


class WordBase(DateTimeMixin):
    origin: Optional[str]
    pronunciation: Optional[str]
    translation: Optional[str]


class WordCreate(WordBase):
    origin: str


class WordUpdate(WordBase):
    pass


class Word(WordBase):
    id: int

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_realworld}
