from sqlalchemy import Column, Integer, String, DateTime, Boolean

from app.database import Base


class Psychology(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    classify = Column(String, index=True)  # 分类
    knowledge = Column(String, index=True)  # 知识点
    created_at = Column(String)
    updated_at = Column(String)


class Word(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin = Column(String, index=True, unique=True, nullable=False)
    pronunciation = Column(String)
    translation = Column(String)

    created_at = Column(String)
    updated_at = Column(String)


class User(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    full_name = Column(String, index=True)  # full name
    email = Column(String, unique=True, index=True, nullable=False)  # email
    hashed_password = Column(String, nullable=False)  # password
    is_active = Column(Boolean, default=True)  # is a active user
    is_superuser = Column(Boolean, default=False)  # is superuser
    is_confirm = Column(Boolean, default=False)  # is confirmed user

    created_at = Column(String)
    updated_at = Column(String)
