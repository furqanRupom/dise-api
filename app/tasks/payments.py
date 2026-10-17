import uuid

from app.core.celery import celery_app
from app.db.database import SessionLocal
from app.services.payment_service import PaymentService


@celery_app.task(name="payments.post_cancel")
def post_cancel_payments_task(booking_id: str) -> None:
    """After a customer cancels: kill any open PaymentIntent, then settle
    the refund / deposit-release rows cancel_booking queued."""
    db = SessionLocal()
    try:
        svc = PaymentService(db)
        svc.cancel_open_charge(uuid.UUID(booking_id))
        svc.process_pending()
    finally:
        db.close()


@celery_app.task(name="payments.process_pending")
def process_pending_payments_task() -> int:
    """Sweeper: settle pending refunds, deposit releases and captures."""
    db = SessionLocal()
    try:
        return PaymentService(db).process_pending()
    finally:
        db.close()
