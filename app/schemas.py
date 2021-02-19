from enum import Enum

from pydantic import BaseModel


class PsychologyClassifyEnum(str, Enum):
    normal = 'normal'  # 普通心理学
    experiment = 'experiment'  # 实验心理学
    education = 'education'  # 教育心理学
    society = 'society'  # 社会心理学


class PsychologyBase(BaseModel):
    classify: PsychologyClassifyEnum
    knowledge: str


class PsychologyCreate(PsychologyBase):
    pass


class Psychology(PsychologyBase):
    id: int

    class Config:
        orm_mode = True
