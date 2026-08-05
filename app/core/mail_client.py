from fastapi import BackgroundTasks
from fastapi_mail import MessageSchema, MessageType
from pydantic import NameEmail

from app.core.mail import fm


async def send_otp_mail(
    email: str,
    otp: str,
    background_tasks: BackgroundTasks,
) -> None:
    message = MessageSchema(
        subject="Your Verification Code",
        recipients=[NameEmail(name=email, email=email)],
        template_body={"otp": otp},
        subtype=MessageType.html,
    )

    background_tasks.add_task(
        fm.send_message,
        message,
        template_name="otp.html",
    )


async def send_forgot_password_mail(
    email: str,
    otp: str,
    background_tasks: BackgroundTasks,
) -> None:
    message = MessageSchema(
        subject="Reset Your Password",
        recipients=[NameEmail(name=email, email=email)],
        template_body={"otp": otp},
        subtype=MessageType.html,
    )

    background_tasks.add_task(
        fm.send_message,
        message,
        template_name="forgot-password.html",
    )
