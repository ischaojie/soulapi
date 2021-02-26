from typing import Any

import redis
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker
from app.config import settings

# db engine
engine = create_engine(settings.DATABASE_URI, connect_args={"check_same_thread": False})
# redis engine
redis_engine = redis.ConnectionPool(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)

RedisLocal = redis.Redis(connection_pool=redis_engine)

# local db session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# init db create all db model to db tables
def init_db():
    # create all model to db
    Base.metadata.create_all(bind=engine)


# the models Base
@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# @app.on_event("startup")
# async def startup_event():
#     try:
#         pool = await aioredis.create_redis_pool(
#             (REDIS_HOST, REDIS_PORT), encoding='utf-8')
#         logger.info(f"Connected to Redis on {REDIS_HOST} {REDIS_PORT}")
#         app.extra['redis'] = pool
#     except ConnectionRefusedError as e:
#         logger.info(f"cannot connect to redis on {REDIS_HOST} {REDIS_PORT}")
#         return
