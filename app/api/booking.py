"""Booking All APIs endponints (for customer, staff and admins) later we going to separate it if its become more huge and almost makes more difficulties to control"""

from fastapi import APIRouter

router = APIRouter(prefix="/v1/booking", tags=["booking"])

""" we will start with staff/admin first APIs then we gradually moved to customer """
