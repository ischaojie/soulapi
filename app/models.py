from sqlalchemy import Column, Integer, String

from .database import Base


class Psychology(Base):
    __tablename__ = "psychologies"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    classify = Column(String)  # 分类
    knowledge = Column(String)  # 知识点
