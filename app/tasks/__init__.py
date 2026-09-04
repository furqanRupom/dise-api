# app/tasks/__init__.py
from app.tasks.notifications import send_license_decision_mail

__all__ = ["send_license_decision_mail"]
