"""POST /webhooks/stripe  (NO auth dependency: Stripe signs the request)."""

import json
import logging
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.services.payment_service import PaymentService
from app.tasks.payments import process_pending_payments_task

logger = logging.getLogger(__name__)
router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
):
    payload = await request.body()  # raw bytes: required for the signature check
    try:
        stripe.Webhook.construct_event(
            payload,
            request.headers.get("stripe-signature", ""),
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except (ValueError, stripe.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook")

    # Signature is verified, so decode to a plain dict for the handlers.
    event = json.loads(payload)

    await run_in_threadpool(PaymentService(db).handle_event, event)

    # Settle refunds / releases queued by this event in the Celery worker.
    # If Redis is down, Stripe must still get its 200: the beat sweeper
    # (payments.process_pending, every 60s) picks the rows up.
    try:
        process_pending_payments_task.delay()
    except Exception:
        logger.exception("Could not enqueue payments.process_pending; beat will retry")
    return {"received": True}
