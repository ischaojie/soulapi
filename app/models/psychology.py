from sqlalchemy import Column, Integer, String

from app.database import Base


class Psychology(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    classify = Column(String, index=True)  # 分类
    knowledge = Column(String, index=True)  # 知识点
    created_at = Column(String)
    updated_at = Column(String)
