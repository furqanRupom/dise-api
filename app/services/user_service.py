import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.cloudinary import delete_image, upload_image
from app.core.security import hash_password, verify_password
from app.models import LicenseStatus, User
from app.schemas.user import (
    ChangePassword,
    LicenseDecisionRequest,
    LicenseSubmitRequest,
    UserUpdate,
)
from app.tasks.notifications import (
    send_license_decision_mail,
)


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
        return updated_user

    async def update_avatar(
        self,
        user_id: uuid.UUID,
        file: UploadFile,
    ) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Upload new image to Cloudinary
        result = await upload_image(file)

        # Update user
        user.avatar_url = result["url"]

        try:
            self.db.commit()
            self.db.refresh(user)

        except SQLAlchemyError:
            self.db.rollback()
            delete_image(result["url"])

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update avatar",
            )

        return user

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

    async def delete_account(self, user_id: uuid.UUID):
        user = (
            self.db.query(User)
            .filter(User.id == user_id, User.deleted_at.is_(None))
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    async def submit_license(
        self,
        user_id: uuid.UUID,
        payload: LicenseSubmitRequest,
        license_document: UploadFile,
    ):
        try:
            user = self.db.scalar(
                select(User).where(
                    User.id == user_id,
                    User.is_active.is_(True),
                    User.deleted_at.is_(None),
                )
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            user.date_of_birth = payload.date_of_birth
            user.license_number = payload.license_number

            license_doc = await upload_image(license_document)

            user.license_document_url = license_doc["url"]
            user.license_status = LicenseStatus.pending

            self.db.commit()
            self.db.refresh(user)

            return user

        except HTTPException:
            raise

        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to submit license",
            ) from e

    async def list_pending_licences(self):
        pending_license_users = self.db.scalars(
            select(User).where(
                User.license_status == LicenseStatus.pending,
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            )
        ).all()
        return pending_license_users

    async def decide_licenses(
        self, user_id: uuid.UUID, payload: LicenseDecisionRequest
    ):

        user = self.db.scalar(
            select(User).where(
                User.license_status == LicenseStatus.pending,
                User.deleted_at.is_(None),
                User.is_active.is_(True),
            )
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found or inactive",
            )

        if user.license_status != LicenseStatus.pending:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="License decision has already been processed",
            )

        user.license_status = payload.decision

        self.db.commit()
        self.db.refresh(user)
        # Dispatch background email notification
        send_license_decision_mail.delay(
            user_email=user.email,
            user_name=user.name,
            status=payload.decision,
            reason=payload.reason,
        )
