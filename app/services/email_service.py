from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType
from pydantic import NameEmail

from app.core.mail import fm


class EmailService:
    @staticmethod
    async def send_otp_email(email: str, otp: str, background_tasks: BackgroundTasks):
        message = MessageSchema(
            subject="Your Verification Code",
            recipients=[NameEmail(name=email, email=email)],
            template_body={"otp": otp},
            subtype=MessageType.html,
        )
        background_tasks.add_task(fm.send_message, message, template_name="otp.html")

    @staticmethod
    async def send_forgot_password_mail(
        email: str, otp: str, background_tasks: BackgroundTasks
    ):
        message = MessageSchema(
            subject="Reset your password",
            recipients=[NameEmail(name=email, email=email)],
            template_body={"otp": otp},
            subtype=MessageType.html,
        )

        background_tasks.add_task(
            fm.send_message, message, template_name="forgot-password.html"
        )
