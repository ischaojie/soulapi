from fastapi import APIRouter

from .v1 import v1

api = APIRouter()
api.include_router(v1, prefix="/v1")
