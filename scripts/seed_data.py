"""
Database seeder for the vehicle-rental schema.

WHERE TO PUT THIS FILE
-----------------------
Save it as:  scripts/seed_data.py   (sibling to your existing scripts/sql/)

HOW TO RUN
----------
    python -m scripts.seed_data
  or
    python scripts/seed_data.py

REQUIREMENTS
------------
    pip install faker

BEFORE RUNNING
--------------
1. Run alembic migrations first: `alembic upgrade head`
2. Make sure the `btree_gist` extension is installed (scripts/sql/btree_gist_setup.sql)
   -- required by the ExcludeConstraints on bookings/maintenance_blocks.
"""

import random
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from faker import Faker

# Allows running as `python scripts/seed_data.py` from repo root without
# having installed the project as a package.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.database import SessionLocal
from app.models.audit_logs import AuditLog
from app.models.booking import Booking, BookingStatusHistory
from app.models.condition_reports import (
    ConditionReport,
    ConditionReportImage,
)
from app.models.coupons import Coupon, CouponUsage
from app.models.enums import (
    BookingStatus,
    DiscountType,
    FuelType,
    LicenseStatus,
    NotificationChannel,
    NotificationStatus,
    PaymentStatus,
    PaymentType,
    ReportType,
    TransmissionType,
    UserRole,
    VehicleStatus,
)
from app.models.location import Location
from app.models.maintenance import MaintenanceBlock
from app.models.notifications import Notification
from app.models.payments import Payment
from app.models.reviews import Review
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleCategory, VehicleImage

fake = Faker()
Faker.seed(42)
random.seed(42)

# Try to reuse your real password hasher so seeded users can actually log
# in through your normal auth flow. Falls back to bcrypt directly if the
# function name/path is different in your codebase.
try:
    from app.core.security import hash_password
except ImportError:
    from passlib.context import CryptContext

    _pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(password: str) -> str:
        return _pwd_ctx.hash(password)


SEED_PASSWORD = "Password123!"

BD_CITIES = ["Dhaka", "Chittagong", "Sylhet", "Khulna", "Rajshahi"]

CATEGORY_DEFS = [
    ("Economy", "Budget-friendly compact cars for city driving."),
    ("Sedan", "Comfortable mid-size sedans for business or family trips."),
    ("SUV", "Spacious SUVs suited for longer trips and rough roads."),
    ("Luxury", "Premium vehicles for a high-end experience."),
    ("Van / Minivan", "Large-capacity vehicles for groups and families."),
    ("Pickup Truck", "Utility trucks for cargo and heavy loads."),
]

CAR_MAKES_MODELS = [
    ("Toyota", "Corolla"),
    ("Toyota", "Premio"),
    ("Toyota", "RAV4"),
    ("Honda", "Civic"),
    ("Honda", "CR-V"),
    ("Nissan", "Sunny"),
    ("Nissan", "X-Trail"),
    ("Hyundai", "Elantra"),
    ("Hyundai", "Tucson"),
    ("Mitsubishi", "Pajero"),
    ("BMW", "5 Series"),
    ("Mercedes-Benz", "E-Class"),
    ("Suzuki", "Alto"),
    ("Suzuki", "Ertiga"),
]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def seed_users(session, n_customers: int = 15) -> dict:
    users = {"admin": [], "support": [], "fleet_staff": [], "customer": []}

    fixed = [
        ("Admin User", "admin@example.com", UserRole.admin),
        ("Support Agent", "support@example.com", UserRole.support),
        ("Fleet Manager", "fleet@example.com", UserRole.fleet_staff),
    ]
    for name, email, role in fixed:
        u = User(
            id=uuid.uuid4(),
            name=name,
            email=email,
            password=hash_password(SEED_PASSWORD),
            role=role,
            date_of_birth=fake.date_of_birth(minimum_age=25, maximum_age=55),
            is_active=True,
            is_verified=True,
            license_status=LicenseStatus.approved,
        )
        session.add(u)
        users[role.value].append(u)

    for i in range(n_customers):
        u = User(
            id=uuid.uuid4(),
            name=fake.name(),
            email=f"customer{i + 1}@example.com",
            password=hash_password(SEED_PASSWORD),
            role=UserRole.customer,
            date_of_birth=fake.date_of_birth(minimum_age=20, maximum_age=65),
            is_active=True,
            is_verified=random.choice([True, True, False]),
            license_number=fake.bothify(text="DL#######"),
            license_status=random.choice(
                [LicenseStatus.approved, LicenseStatus.approved, LicenseStatus.pending]
            ),
        )
        session.add(u)
        users["customer"].append(u)

    session.flush()
    return users


def seed_locations(session) -> list[Location]:
    locations = []
    for city in BD_CITIES:
        loc = Location(
            id=uuid.uuid4(),
            name=f"{city} Downtown Branch",
            city=city,
            address=fake.street_address() + f", {city}, Bangladesh",
            latitude=round(random.uniform(20.5, 26.5), 6),
            longitude=round(random.uniform(88.0, 92.5), 6),
            is_active=True,
        )
        session.add(loc)
        locations.append(loc)
    session.flush()
    return locations


def seed_categories(session) -> list[VehicleCategory]:
    cats = []
    for name, desc in CATEGORY_DEFS:
        c = VehicleCategory(id=uuid.uuid4(), name=name, description=desc)
        session.add(c)
        cats.append(c)
    session.flush()
    return cats


def seed_vehicles(
    session, categories: list[VehicleCategory], locations: list[Location], n: int = 20
) -> list[Vehicle]:
    vehicles = []
    used_plates: set[str] = set()
    for i in range(n):
        make, model = random.choice(CAR_MAKES_MODELS)
        plate = fake.unique.bothify(text="DHA-####")
        while plate in used_plates:
            plate = fake.unique.bothify(text="DHA-####")
        used_plates.add(plate)

        v = Vehicle(
            id=uuid.uuid4(),
            category_id=random.choice(categories).id,
            location_id=random.choice(locations).id,
            make=make,
            model=model,
            year=random.randint(2015, 2024),
            license_plate=plate,
            transmission=random.choice(list(TransmissionType)),
            fuel_type=random.choice(list(FuelType)),
            seats=random.choice([2, 4, 5, 7]),
            daily_rate=random.choice([1500, 2000, 2500, 3500, 5000, 8000]),
            currency="BDT",
            deposit_amount=random.choice([5000, 10000, 15000]),
            requires_approval=random.choice([False, False, True]),
            status=VehicleStatus.available,
            odometer_km=random.randint(1000, 80000),
        )
        session.add(v)
        vehicles.append(v)

    session.flush()

    # 2 images per vehicle
    for v in vehicles:
        for sort_order in range(2):
            session.add(
                VehicleImage(
                    id=uuid.uuid4(),
                    vehicle_id=v.id,
                    image_url=f"https://picsum.photos/seed/{v.id}-{sort_order}/800/600",
                    sort_order=sort_order,
                )
            )
    session.flush()
    return vehicles


def seed_coupons(session) -> list[Coupon]:
    coupons = []
    defs = [
        ("WELCOME10", DiscountType.percentage, 10),
        ("SAVE500", DiscountType.fixed_amount, 500),
        ("EID2026", DiscountType.percentage, 15),
    ]
    for code, dtype, value in defs:
        c = Coupon(
            id=uuid.uuid4(),
            code=code,
            discount_type=dtype,
            discount_value=value,
            max_usage=100,
            usage_count=0,
            valid_from=now_utc() - timedelta(days=30),
            valid_to=now_utc() + timedelta(days=90),
            is_active=True,
        )
        session.add(c)
        coupons.append(c)
    session.flush()
    return coupons


def seed_bookings(
    session,
    users: dict,
    vehicles: list[Vehicle],
    locations: list[Location],
    coupons: list[Coupon],
):
    """
    IMPORTANT: bookings.excl_no_overlapping_confirmed_bookings only blocks
    overlap between rows where status IN ('confirmed','active'). To keep
    the seeder simple and safe regardless of which statuses get picked,
    each vehicle's bookings are still laid out on non-overlapping date
    ranges (sequential, a few days apart) so it works no matter what.
    """
    statuses_cycle = [
        BookingStatus.completed,
        BookingStatus.completed,
        BookingStatus.confirmed,
        BookingStatus.active,
        BookingStatus.cancelled,
        BookingStatus.pending_payment,
    ]

    bookings: list[Booking] = []
    today = date.today()

    for v in vehicles:
        n_bookings = random.randint(1, 3)
        cursor = today - timedelta(days=random.randint(30, 60))
        for _ in range(n_bookings):
            customer = random.choice(users["customer"])
            duration = random.randint(1, 6)
            start = cursor
            end = start + timedelta(days=duration)
            cursor = end + timedelta(days=random.randint(2, 10))  # gap, avoids overlap

            status = random.choice(statuses_cycle)
            days = (end - start).days or 1
            base_price = float(v.daily_rate) * days
            coupon = random.choice(coupons + [None, None])  # bias towards no coupon
            discount = 0.0
            if coupon:
                if coupon.discount_type == DiscountType.percentage:
                    discount = round(base_price * float(coupon.discount_value) / 100, 2)
                else:
                    discount = float(coupon.discount_value)
            total_price = max(base_price - discount, 0)

            pickup = random.choice(locations)
            dropoff = random.choice(locations)

            b = Booking(
                id=uuid.uuid4(),
                customer_id=customer.id,
                vehicle_id=v.id,
                pickup_location_id=pickup.id,
                dropoff_location_id=dropoff.id,
                start_date=start,
                end_date=end,
                status=status,
                base_price=base_price,
                discount_amount=discount,
                total_price=total_price,
                currency="BDT",
                coupon_id=coupon.id if coupon else None,
                deposit_hold_amount=float(v.deposit_amount),
                approval_deadline=None,
                created_by=customer.id,
            )
            session.add(b)
            bookings.append(b)

            if coupon:
                session.add(
                    CouponUsage(
                        id=uuid.uuid4(),
                        coupon_id=coupon.id,
                        customer_id=customer.id,
                        booking_id=b.id,
                    )
                )
                coupon.usage_count += 1

    session.flush()

    # status history: one "created" row + one row matching current status
    for b in bookings:
        session.add(
            BookingStatusHistory(
                id=uuid.uuid4(),
                booking_id=b.id,
                from_status=None,
                to_status=BookingStatus.pending_payment.value,
                changed_by=b.created_by,
                reason="Booking created",
            )
        )
        if b.status != BookingStatus.pending_payment:
            session.add(
                BookingStatusHistory(
                    id=uuid.uuid4(),
                    booking_id=b.id,
                    from_status=BookingStatus.pending_payment.value,
                    to_status=b.status.value,
                    changed_by=b.created_by,
                    reason=f"Status moved to {b.status.value}",
                )
            )

    # payments: charge for anything past pending_payment
    for b in bookings:
        if b.status == BookingStatus.pending_payment:
            continue
        session.add(
            Payment(
                id=uuid.uuid4(),
                booking_id=b.id,
                type=PaymentType.charge,
                amount=b.total_price,
                currency=b.currency,
                status=PaymentStatus.succeeded
                if b.status != BookingStatus.cancelled
                else PaymentStatus.failed,
                stripe_payment_intent_id=f"pi_{uuid.uuid4().hex[:16]}",
                idempotency_key=f"seed_{b.id}",
            )
        )
        if b.deposit_hold_amount:
            session.add(
                Payment(
                    id=uuid.uuid4(),
                    booking_id=b.id,
                    type=PaymentType.deposit_hold,
                    amount=b.deposit_hold_amount,
                    currency=b.currency,
                    status=PaymentStatus.succeeded,
                    stripe_payment_intent_id=f"pi_{uuid.uuid4().hex[:16]}",
                    idempotency_key=f"seed_deposit_{b.id}",
                )
            )

    session.flush()
    return bookings


def seed_reviews(session, bookings: list[Booking]):
    completed = [b for b in bookings if b.status == BookingStatus.completed]
    for b in completed:
        if random.random() < 0.7:  # not every completed booking gets reviewed
            session.add(
                Review(
                    id=uuid.uuid4(),
                    booking_id=b.id,
                    customer_id=b.customer_id,
                    vehicle_id=b.vehicle_id,
                    rating=random.randint(3, 5),
                    comment=fake.sentence(nb_words=12),
                )
            )
    session.flush()


def seed_condition_reports(session, bookings: list[Booking], staff_id: uuid.UUID):
    relevant = [
        b
        for b in bookings
        if b.status in (BookingStatus.completed, BookingStatus.active)
    ]
    for b in relevant:
        checkin = ConditionReport(
            id=uuid.uuid4(),
            booking_id=b.id,
            type=ReportType.check_in,
            odometer_km=random.randint(1000, 80000),
            fuel_level_pct=random.choice([50, 75, 100]),
            notes="Vehicle in good condition at pickup.",
            recorded_by=staff_id,
        )
        session.add(checkin)
        session.flush()
        session.add(
            ConditionReportImage(
                id=uuid.uuid4(),
                condition_report_id=checkin.id,
                image_url=f"https://picsum.photos/seed/{checkin.id}/600/400",
            )
        )

        if b.status == BookingStatus.completed:
            checkout = ConditionReport(
                id=uuid.uuid4(),
                booking_id=b.id,
                type=ReportType.check_out,
                odometer_km=checkin.odometer_km + random.randint(20, 400),
                fuel_level_pct=random.choice([25, 50, 75]),
                notes="Vehicle returned, minor wear noted.",
                recorded_by=staff_id,
            )
            session.add(checkout)
            session.flush()
            session.add(
                ConditionReportImage(
                    id=uuid.uuid4(),
                    condition_report_id=checkout.id,
                    image_url=f"https://picsum.photos/seed/{checkout.id}/600/400",
                )
            )
    session.flush()


def seed_maintenance_blocks(session, vehicles: list[Vehicle], staff_id: uuid.UUID):
    # Put maintenance a good while in the future, per vehicle, so it can
    # never clash with itself (only one block per vehicle here).
    for v in random.sample(vehicles, k=max(1, len(vehicles) // 4)):
        start = date.today() + timedelta(days=random.randint(60, 90))
        end = start + timedelta(days=random.randint(1, 4))
        session.add(
            MaintenanceBlock(
                id=uuid.uuid4(),
                vehicle_id=v.id,
                start_date=start,
                end_date=end,
                reason=random.choice(
                    ["Scheduled service", "Tire replacement", "Brake inspection"]
                ),
                created_by=staff_id,
            )
        )
    session.flush()


def seed_notifications(session, users: dict, bookings: list[Booking]):
    for b in random.sample(bookings, k=min(10, len(bookings))):
        session.add(
            Notification(
                id=uuid.uuid4(),
                user_id=b.customer_id,
                channel=random.choice(list(NotificationChannel)),
                type="booking_status_update",
                payload={"booking_id": str(b.id), "status": b.status.value},
                status=random.choice(
                    [NotificationStatus.sent, NotificationStatus.queued]
                ),
                sent_at=now_utc() if random.random() < 0.7 else None,
            )
        )
    session.flush()


def seed_audit_logs(session, users: dict, vehicles: list[Vehicle]):
    admin = users["admin"][0]
    for v in random.sample(vehicles, k=min(5, len(vehicles))):
        session.add(
            AuditLog(
                id=uuid.uuid4(),
                actor_id=admin.id,
                action="vehicle.created",
                entity_type="vehicle",
                entity_id=v.id,
                meta={"source": "seed_script"},
            )
        )
    session.flush()


def main():
    with SessionLocal() as session:
        with session.begin():
            print("Seeding users...")
            users = seed_users(session)

            print("Seeding locations...")
            locations = seed_locations(session)

            print("Seeding vehicle categories...")
            categories = seed_categories(session)

            print("Seeding vehicles + images...")
            vehicles = seed_vehicles(session, categories, locations)

            print("Seeding coupons...")
            coupons = seed_coupons(session)

            print("Seeding bookings, status history, payments...")
            bookings = seed_bookings(
                session,
                users,
                vehicles,
                locations,
                coupons,
            )

            print("Seeding reviews...")
            seed_reviews(session, bookings)

            print("Seeding condition reports...")
            staff = users["fleet_staff"][0]
            seed_condition_reports(session, bookings, staff.id)

            print("Seeding maintenance blocks...")
            seed_maintenance_blocks(session, vehicles, staff.id)

            print("Seeding notifications...")
            seed_notifications(session, users, bookings)

            print("Seeding audit logs...")
            seed_audit_logs(session, users, vehicles)

        print(
            f"\nDone. {len(users['customer']) + 3} users, "
            f"{len(vehicles)} vehicles, "
            f"{len(bookings)} bookings. "
            f"All seeded users' password: {SEED_PASSWORD!r}"
        )


if __name__ == "__main__":
    main()
