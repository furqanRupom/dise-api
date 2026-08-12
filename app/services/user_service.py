import uuid

from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.settings import hash_password, verify_password
from app.models import User
from app.schemas.response import SendRespose
from app.schemas.user import ChangePassword, UserUpdate


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def update_user(self, user_id: uuid.UUID, payload: UserUpdate):
        user = self.db.query(User).filter_by(id=user_id).first()
        update_data = payload.model_dump(
            exclude_unset=True,
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        result = self.db.execute(
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )
        updated_user = result.scalar_one_or_none()
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        self.db.commit()
        return SendRespose(
            success=True,
            message="User updated successfully",
            data=updated_user,
        )

    async def change_password(self, user_id: uuid.UUID, payload: ChangePassword):
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        verify_pass = verify_password(payload.current_password, user.password)
        if not verify_pass:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        hash_pass = hash_password(payload.new_password)
        user.password = hash_pass
        self.db.commit()
        return SendRespose(
            success=True,
            message="Password changed successfully",
            data=None,
        )

    async def delete_account(self, user_id: uuid.UUID):
        user = self.db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.is_deleted = True
        self.db.commit()
        return SendRespose(
            success=True,
            message="Account deleted successfully",
            data=None,
        )
