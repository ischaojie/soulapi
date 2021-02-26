from fastapi import FastAPI, APIRouter

from app.config import settings
from app.routers import psychologies_router, user_router, login_router, utils_router, word_router

# openapi tags metadata
tags_metadata = [
    {
        "name": "psychologies",
        "description": "Manage psychologies knowledge. Even you can get them daily.",
    },
    {
        "name": "words",
        "description": "Manage words translation. Even you can get them daily.",
    }
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="The Soul api",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# api v1 router
app_v1 = APIRouter()
app_v1.include_router(
    psychologies_router, prefix="/psychologies", tags=["psychologies"]
)
app_v1.include_router(word_router, prefix="/words", tags=["words"])
app_v1.include_router(user_router, prefix="/users", tags=["users"])
app_v1.include_router(login_router, tags=["login"])
app_v1.include_router(utils_router, prefix="/utils", tags=["utils"])

app.include_router(app_v1, prefix=settings.API_V1_STR)


@app.get("/")
def home():
    return {"message": settings.DATABASE_URI}
