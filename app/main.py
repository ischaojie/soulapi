from typing import List

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas, crud
from .database import SessionLocal, engine

# create all model to db
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/psychologies/", response_model=schemas.Psychology)
def create_psychology(psychology: schemas.PsychologyCreate, db: Session = Depends(get_db)):
    """create a psychology knowledge"""
    return crud.create_psychology(db, psychology)


@app.get("/psychologies/", response_model=List[schemas.Psychology])
def read_psychologies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """read limited psychologies knowledge"""
    psychologies = crud.get_psychologies(db, skip, limit)
    return psychologies


@app.get("psychologies/random", response_model=schemas.Psychology)
def read_psychology_random(db: Session = Depends(get_db)):
    """read psychology random"""
    db_psychology = crud.get_psychology_random(db)
    if db_psychology is None:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@app.get("psychologies/daily", response_model=schemas.Psychology)
def read_psychology_daily(db: Session = Depends(get_db)):
    """read psychology random every day"""
    db_psychology = crud.get_psychology_daily(db)
    if db_psychology is None:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology


@app.get("/psychologies/{pid}", response_model=schemas.Psychology)
def read_psychology(pid: int, db: Session = Depends(get_db)):
    """read psychology by id"""
    db_psychology = crud.get_psychology(db, pid)
    if db_psychology is None:
        raise HTTPException(status_code=404, detail="psychology knowledge not found")
    return db_psychology
