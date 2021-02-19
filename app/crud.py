from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine


def get_psychologies(db: Session, skip: int = 0, limit: int = 10):
    """
    get all psychologies knowledge
    :param db: db session
    :param skip: skip column
    :param limit: query limit db line
    :return: all psychologies
    """
    return db.query(models.Psychology).offset(skip).limit(limit).all()


def get_psychology(db: Session, pid: int):
    """
    get psychology by id
    :param db: db session
    :param pid: psychology id
    :return: psychology model
    """
    return db.query(models.Psychology).filter(models.Psychology.id == pid).first()


def get_psychology_random(db: Session):
    """
    get a psychology knowledge random
    :param db: db session
    :return: psychology model
    """
    if engine.name == 'sqlite' or 'postgresql':
        return db.query(models.Psychology).order_by(func.random()).first()
    elif engine.name == 'mysql':
        return db.query(models.Psychology).order_by(func.rand()).first()
    elif engine.name == 'oracle':
        return db.query(models.Psychology).order_by('dbms_random.value').first()


def get_psychology_daily(db: Session):
    """
    get a psychology knowledge random every day
    :param db: db session
    :return: psychology model
    """
    pass


def create_psychology(db: Session, psychology: schemas.PsychologyCreate):
    """
    create a spychology knowledge
    :param db: db session
    :param psychology: psychology schemas
    :return: created psychology
    """
    db_psychology = models.Psychology(classify=psychology.classify, knowledge=psychology.knowledge)
    db.add(db_psychology)
    db.commit()
    # refresh to db
    db.refresh(db_psychology)
    return db_psychology
