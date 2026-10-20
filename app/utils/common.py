"""Business-timezone helpers shared by fleet and payment services.

TODO: move BUSINESS_TZ to settings (and use it in booking_service.create_booking too).
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

BUSINESS_TZ = ZoneInfo("Asia/Dhaka")


def business_today() -> date:
    return datetime.now(BUSINESS_TZ).date()
