from datetime import datetime
from typing import Optional

from redis import Redis
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import engine
from .base import CRUDBase
from ..models.word import Word
from ..schemas.word import WordCreate, WordUpdate


class CRUDWord(CRUDBase[Word, WordCreate, WordUpdate]):
    def get_by_origin(self, db: Session, *, origin: str) -> Optional[Word]:
        return db.query(Word).filter(Word.origin == origin).first()

    def get_word_random(self, db: Session) -> Word:
        if engine.name == "sqlite" or "postgresql":
            return db.query(Word).order_by(func.random()).first()
        elif engine.name == "mysql":
            return db.query(Word).order_by(func.rand()).first()
        elif engine.name == "oracle":
            return db.query(Word).order_by("dbms_random.value").first()

    def get_word_daily(self, db: Session, redis: Redis) -> Optional[Word]:
        # get cache from redis
        redis_data = redis.hgetall("word_daily")
        # only time equal current day read from redis
        if redis_data and redis_data.get(b"date").decode("utf-8") == datetime.strftime(
                datetime.now(), "%Y%m%d"
        ):
            # get word model
            db_word = self.get(db, id=redis_data.get(b"id").decode("utf-8"))
        else:
            # if time not today, get random from db
            # and then save to redis cache
            db_word = self.get_word_random(db)
            if not db_word:
                return None
            redis.hset("word_daily", "id", db_word.id)
            now = datetime.strftime(datetime.now(), "%Y%m%d")
            redis.hset("word_daily", "date", now)

        return db_word


word = CRUDWord(Word)
