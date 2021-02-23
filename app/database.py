from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

from app.config import settings

# db engine
engine = create_engine(settings.DATABASE_URI, connect_args={"check_same_thread": False})
# local db session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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
