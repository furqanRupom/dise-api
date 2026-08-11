from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def update_user(self, user_id: str, payload: UserUpdate):
        user = self.db.query(User).filter_by(id=user_id).first()
        update_data = payload.model_dump(
            exclude_unset=True,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        result = self.db.execute(
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )
        updated_user = result.scalar_one_or_none()
        if updated_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        self.db.commit()
