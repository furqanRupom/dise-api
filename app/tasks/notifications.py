# app/tasks/notifications.py
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from jinja2 import Environment, FileSystemLoader

from app.core.celery import celery_app
from app.core.config import settings

jinja_env = Environment(loader=FileSystemLoader("app/templates"))


@celery_app.task(
    name="send_license_decision_email",
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def send_license_decision_mail(
    user_email: str,
    user_name: str,
    status: str,
    reason: str | None = None,
) -> None:
    is_approved = status == "approved"
    subject = "License Approved!" if is_approved else "Update on Your License Request"
    template_name = "license-approved.html" if is_approved else "license-rejected.html"

    template = jinja_env.get_template(template_name)
    html_content = template.render(
        name=user_name,
        reason=reason,
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.MAIL_FROM
    msg["To"] = user_email
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
        server.starttls()
        server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
        server.send_message(msg)
