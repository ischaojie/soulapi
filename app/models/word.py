from sqlalchemy import Column, Integer, String

from app.database import Base


class Word(Base):
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    origin = Column(String, index=True, unique=True, nullable=False)
    pronunciation = Column(String)
    translation = Column(String)

    created_at = Column(String)
    updated_at = Column(String)
