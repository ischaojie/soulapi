from datetime import datetime
from typing import Optional

from .base import CRUDBase
from app.models.psychology import Psychology

from app.schemas.psychology import PsychologyCreate, PsychologyUpdate
from redis import Redis
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import engine


class CRUDPsychology(CRUDBase[Psychology, PsychologyCreate, PsychologyUpdate]):
    def get_psychology_random(self, db: Session) -> Psychology:
        if engine.name == "sqlite" or "postgresql":
            return db.query(Psychology).order_by(func.random()).first()
        elif engine.name == "mysql":
            return db.query(Psychology).order_by(func.rand()).first()
        elif engine.name == "oracle":
            return db.query(Psychology).order_by("dbms_random.value").first()

    def get_psychology_daily(self, db: Session, redis: Redis) -> Optional[Psychology]:
        # get cache from redis
        redis_data = redis.hgetall("psychology_daily")
        # only time equal current day read from redis
        if redis_data and redis_data.get(b"date").decode("utf-8") == datetime.strftime(
            datetime.now(), "%Y%m%d"
        ):
            # get psychology model
            db_psychology = self.get(db, id=redis_data.get(b"id").decode("utf-8"))
        else:
            # if time not today, get random from db
            # and then save to redis cache
            db_psychology = self.get_psychology_random(db)
            if not db_psychology:
                return None
            redis.hset("psychology_daily", "id", db_psychology.id)
            now = datetime.strftime(datetime.now(), "%Y%m%d")
            redis.hset("psychology_daily", "date", now)

        return db_psychology


psychology = CRUDPsychology(Psychology)