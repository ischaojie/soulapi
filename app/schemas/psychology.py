from datetime import datetime
from enum import Enum
from typing import Optional

from .base import DateTimeMixin, convert_datetime_to_realworld


class PsychologyClassifyEnum(str, Enum):
    normal = "normal"  # 普通心理学
    experiment = "experiment"  # 实验心理学
    education = "education"  # 教育心理学
    society = "society"  # 社会心理学
    develop = "develop"  # 发展心理学
    measure = "measure"  # 测量心理学
    statistics = "statistics"  # 统计心理学


class PsychologyBase(DateTimeMixin):
    classify: Optional[PsychologyClassifyEnum]
    knowledge: Optional[str]


class PsychologyCreate(PsychologyBase):
    classify: PsychologyClassifyEnum
    knowledge: str


class PsychologyUpdate(PsychologyBase):
    pass


class Psychology(PsychologyBase):
    id: int

    class Config:
        orm_mode = True
        json_encoders = {datetime: convert_datetime_to_realworld}
