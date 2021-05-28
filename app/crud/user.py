from typing import Optional, Union, Dict, Any

from sqlalchemy.orm import Session

from .base import CRUDBase
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from ..utils import get_hashed_password, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """crud for user"""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj: UserCreate, **kwargs) -> User:
        """create normal user"""
        db_user = User(
            email=obj.email,
            hashed_password=get_hashed_password(obj.password),
            full_name=obj.full_name,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
        )

        if kwargs.get("is_superuser"):
            db_user.is_superuser = True
        if kwargs.get("is_confirm"):
            db_user.is_confirm = True

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
            updated_at=obj.updated_at,
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