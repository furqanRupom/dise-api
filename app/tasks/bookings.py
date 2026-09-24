from app.core.celery import celery_app
from app.db.database import SessionLocal
from app.services.booking_service import BookingService


@celery_app.task(name="bookings.expire_pending_approvals")
def expire_pending_approvals_task() -> int:
    """Expire booking whoose approval deadline passed"""

    db = SessionLocal()

    try:
        service = BookingService(db)
        expired_count = service.expire_pending_approvals()
        return expired_count
    finally:
        db.close()
