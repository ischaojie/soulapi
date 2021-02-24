from typing import TypeVar, Generic, Type, Optional, Any, List, Union, Dict

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from .database import engine, Base
from .models import User, Psychology
from .schemas import UserCreate, UserUpdate, PsychologyCreate, PsychologyUpdate
from .utils import get_hashed_password, verify_password

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """crud base class"""
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
            self, db: Session, *, skip: int = 0, limit: int = 10
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj: CreateSchemaType) -> ModelType:
        # db compatible with json
        db_obj = self.model(**obj.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
            self,
            db: Session,
            *,
            db_obj: ModelType,
            obj: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        update model, the update field can be Pydantic model or dict
        :param db: db session
        :param db_obj: updated db model
        :param obj: obj need to change
        :return: db model
        """
        # db data
        obj_data = jsonable_encoder(db_obj)

        if isinstance(obj, dict):
            update_data = obj
        else:
            # if pydantic model, convert to dict
            update_data = obj.dict(exclude_unset=True)

        # if need updated field in db_obj, update it
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        # update
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """crud for user"""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj: UserCreate) -> User:
        """create normal user"""
        db_user = User(
            email=obj.email,
            hashed_password=get_hashed_password(obj.password),
            full_name=obj.full_name,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def create_superuser(self, db: Session, *, obj: UserCreate) -> User:
        """create super user"""
        db_superuser = User(
            email=obj.email,
            hashed_password=get_hashed_password(obj.password),
            full_name=obj.full_name,
            is_superuser=True,
            is_confirm=True,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )

        db.add(db_superuser)
        db.commit()
        db.refresh(db_superuser)
        return db_superuser

    def update(
            self, db: Session, *, db_obj: UserUpdate, obj: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj, dict):
            update_data = obj
        else:
            update_data = obj.dict(exclude_unset=True)

        if update_data.get("password"):
            hashed_password = get_hashed_password(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj=obj)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


user = CRUDUser(User)


class CRUDPsychology(CRUDBase[Psychology, PsychologyCreate, PsychologyUpdate]):
    def get_psychology_random(self, db: Session) -> Psychology:
        if engine.name == "sqlite" or "postgresql":
            return db.query(Psychology).order_by(func.random()).first()
        elif engine.name == "mysql":
            return db.query(Psychology).order_by(func.rand()).first()
        elif engine.name == "oracle":
            return db.query(Psychology).order_by("dbms_random.value").first()

    def get_psychology_daily(self, db: Session) -> Psychology:
        pass


psychology = CRUDPsychology(Psychology)
