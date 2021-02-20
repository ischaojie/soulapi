from fastapi import FastAPI

from app import models
from app.database import engine
from app.routers import psychologies_router, user_router, login_router

# create all model to db
models.Base.metadata.create_all(bind=engine)

# openapi tags metadata
tags_metadata = [
    {
        "name": "psychologies",
        "description": "Manage psychologies knowledge. Even you can get them daily.",
    },
]

app = FastAPI(
    title="SoulAPI",
    description="The Soul api",
    version="1.0.0",
    openapi_tags=tags_metadata
)

# api router
app.include_router(psychologies_router, prefix="/psychologies", tags=["psychologies"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(login_router, tags=["login"])


@app.get("/")
async def home():
    return {"message": "Soul API"}
