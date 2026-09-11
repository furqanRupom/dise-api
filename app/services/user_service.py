import os
import tempfile
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
from app.services.license_service import LicenseDocumentService
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
        front_file: UploadFile,
        back_file: UploadFile,
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

            front_suffix = os.path.splitext(front_file.filename or ".jpg")[1]

            back_suffix = os.path.splitext(back_file.filename or ".jpg")[1]

            front_temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=front_suffix,
            )

            back_temp = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=back_suffix,
            )

            try:
                front_content = await front_file.read()
                back_content = await back_file.read()

                front_temp.write(front_content)
                back_temp.write(back_content)

                front_temp.close()
                back_temp.close()

                license_service = LicenseDocumentService()

                result = license_service.extract(
                    front_image_path=front_temp.name,
                    back_image_path=back_temp.name,
                )

            finally:
                if os.path.exists(front_temp.name):
                    os.remove(front_temp.name)

                if os.path.exists(back_temp.name):
                    os.remove(back_temp.name)

            extracted_license_number = result.front.license_number

            extracted_date_of_birth = result.front.date_of_birth

            if not extracted_license_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract license number from the front document",
                )

            if not extracted_date_of_birth:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not extract date of birth from the front document",
                )

            submitted_license_number = (
                payload.license_number.upper().replace(" ", "").replace("-", "")
            )

            extracted_license_number = (
                extracted_license_number.upper().replace(" ", "").replace("-", "")
            )

            try:
                extracted_dob = datetime.strptime(
                    extracted_date_of_birth,
                    "%d%b%Y",
                ).date()

            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not parse date of birth from the front document",
                ) from e

            if extracted_license_number != submitted_license_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="License number does not match the document",
                )

            if extracted_dob != payload.date_of_birth:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Date of birth does not match the document",
                )

            user.date_of_birth = payload.date_of_birth
            user.license_number = payload.license_number

            await front_file.seek(0)

            license_doc = await upload_image(front_file)

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
                User.id == user_id,
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
