"""
Seed database with realistic development data.

Run:
    python scripts/seed_data.py

Make sure migrations have already been applied:
    alembic upgrade head
"""

import random
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from faker import Faker

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

SEED_PASSWORD = "Password123!"


try:
    from app.core.security import hash_password
except ImportError:
    from passlib.context import CryptContext

    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
    )

    def hash_password(password: str) -> str:
        return pwd_context.hash(password)


def money(value: int | float | str | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


def coordinate(value: int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.000001"))


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def seed_users(session) -> dict[str, list[User]]:
    users = {
        "admin": [],
        "support": [],
        "fleet_staff": [],
        "customer": [],
    }

    fixed_users = [
        (
            "Admin User",
            "admin@example.com",
            UserRole.admin,
        ),
        (
            "Support Agent",
            "support@example.com",
            UserRole.support,
        ),
        (
            "Fleet Manager",
            "fleet@example.com",
            UserRole.fleet_staff,
        ),
    ]

    password_hash = hash_password(SEED_PASSWORD)

    for name, email, role in fixed_users:
        user = User(
            id=uuid.uuid4(),
            name=name,
            email=email,
            password=password_hash,
            role=role,
            date_of_birth=fake.date_of_birth(
                minimum_age=25,
                maximum_age=55,
            ),
            is_active=True,
            is_verified=True,
            license_status=LicenseStatus.approved,
        )

        session.add(user)
        users[role.value].append(user)

    for index in range(15):
        license_status = random.choice(
            [
                LicenseStatus.approved,
                LicenseStatus.approved,
                LicenseStatus.pending,
                LicenseStatus.unsubmitted,
            ]
        )

        user = User(
            id=uuid.uuid4(),
            name=fake.name(),
            email=f"customer{index + 1}@example.com",
            password=password_hash,
            role=UserRole.customer,
            date_of_birth=fake.date_of_birth(
                minimum_age=20,
                maximum_age=65,
            ),
            is_active=True,
            is_verified=random.choice(
                [
                    True,
                    True,
                    True,
                    False,
                ]
            ),
            license_number=(
                fake.bothify("DL########")
                if license_status != LicenseStatus.unsubmitted
                else None
            ),
            license_status=license_status,
        )

        session.add(user)
        users["customer"].append(user)

    session.flush()

    return users


def seed_locations(session) -> list[Location]:
    locations = []

    cities = {
        "Dhaka": (23.8103, 90.4125),
        "Chittagong": (22.3569, 91.7832),
        "Sylhet": (24.8949, 91.8687),
        "Khulna": (22.8456, 89.5403),
        "Rajshahi": (24.3745, 88.6042),
    }

    for city, (latitude, longitude) in cities.items():
        location = Location(
            id=uuid.uuid4(),
            name=f"{city} Downtown Branch",
            city=city,
            address=f"{fake.street_address()}, {city}, Bangladesh",
            latitude=coordinate(latitude),
            longitude=coordinate(longitude),
            is_active=True,
        )

        session.add(location)
        locations.append(location)

    session.flush()

    return locations


def seed_categories(session) -> list[VehicleCategory]:
    categories = [
        VehicleCategory(
            id=uuid.uuid4(),
            name="Economy",
            description="Affordable compact cars for city travel.",
        ),
        VehicleCategory(
            id=uuid.uuid4(),
            name="Sedan",
            description="Comfortable cars for business and family trips.",
        ),
        VehicleCategory(
            id=uuid.uuid4(),
            name="SUV",
            description="Spacious vehicles for longer trips.",
        ),
        VehicleCategory(
            id=uuid.uuid4(),
            name="Luxury",
            description="Premium vehicles for a comfortable experience.",
        ),
        VehicleCategory(
            id=uuid.uuid4(),
            name="Van / Minivan",
            description="Large vehicles suitable for groups and families.",
        ),
        VehicleCategory(
            id=uuid.uuid4(),
            name="Pickup Truck",
            description="Utility vehicles for cargo and heavy loads.",
        ),
    ]

    session.add_all(categories)
    session.flush()

    return categories


def seed_vehicles(
    session,
    categories: list[VehicleCategory],
    locations: list[Location],
) -> list[Vehicle]:
    vehicles = []

    car_models = [
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

    daily_rates = [
        1500,
        1800,
        2000,
        2500,
        3000,
        3500,
        5000,
        7000,
        9000,
    ]

    for _ in range(20):
        make, model = random.choice(car_models)

        vehicle = Vehicle(
            id=uuid.uuid4(),
            category_id=random.choice(categories).id,
            location_id=random.choice(locations).id,
            make=make,
            model=model,
            year=random.randint(2017, 2025),
            license_plate=fake.unique.bothify("DHA-####"),
            transmission=random.choice(list(TransmissionType)),
            fuel_type=random.choice(list(FuelType)),
            seats=random.choice([4, 5, 5, 5, 7]),
            daily_rate=money(random.choice(daily_rates)),
            currency="BDT",
            deposit_amount=money(
                random.choice(
                    [
                        5000,
                        10000,
                        15000,
                        20000,
                    ]
                )
            ),
            requires_approval=random.choice(
                [
                    False,
                    False,
                    False,
                    True,
                ]
            ),
            status=VehicleStatus.available,
            odometer_km=random.randint(
                1000,
                80000,
            ),
        )

        session.add(vehicle)
        vehicles.append(vehicle)

    session.flush()

    for vehicle in vehicles:
        for sort_order in range(2):
            image = VehicleImage(
                id=uuid.uuid4(),
                vehicle_id=vehicle.id,
                image_url=(
                    f"https://picsum.photos/seed/{vehicle.id}-{sort_order}/800/600"
                ),
                sort_order=sort_order,
            )

            session.add(image)

    session.flush()

    return vehicles


def seed_coupons(session) -> list[Coupon]:
    coupons = [
        Coupon(
            id=uuid.uuid4(),
            code="WELCOME10",
            discount_type=DiscountType.percentage,
            discount_value=money("10"),
            max_usage=100,
            usage_count=0,
            valid_from=now_utc() - timedelta(days=30),
            valid_to=now_utc() + timedelta(days=90),
            is_active=True,
        ),
        Coupon(
            id=uuid.uuid4(),
            code="SAVE500",
            discount_type=DiscountType.fixed_amount,
            discount_value=money("500"),
            max_usage=100,
            usage_count=0,
            valid_from=now_utc() - timedelta(days=30),
            valid_to=now_utc() + timedelta(days=90),
            is_active=True,
        ),
        Coupon(
            id=uuid.uuid4(),
            code="EID2026",
            discount_type=DiscountType.percentage,
            discount_value=money("15"),
            max_usage=100,
            usage_count=0,
            valid_from=now_utc() - timedelta(days=30),
            valid_to=now_utc() + timedelta(days=90),
            is_active=True,
        ),
    ]

    session.add_all(coupons)
    session.flush()

    return coupons


def calculate_discount(
    base_price: Decimal,
    coupon: Coupon | None,
) -> Decimal:
    if coupon is None:
        return Decimal("0.00")

    if coupon.discount_type == DiscountType.percentage:
        discount = base_price * coupon.discount_value / Decimal("100")
    else:
        discount = coupon.discount_value

    discount = discount.quantize(Decimal("0.01"))

    return min(
        discount,
        base_price,
    )


def seed_bookings(
    session,
    users: dict[str, list[User]],
    vehicles: list[Vehicle],
    locations: list[Location],
    coupons: list[Coupon],
) -> list[Booking]:
    bookings = []

    possible_statuses = [
        BookingStatus.completed,
        BookingStatus.completed,
        BookingStatus.confirmed,
        BookingStatus.active,
        BookingStatus.cancelled,
        BookingStatus.pending_payment,
        BookingStatus.rejected,
        BookingStatus.no_show,
    ]

    today = date.today()

    for vehicle in vehicles:
        number_of_bookings = random.randint(1, 3)

        cursor = today - timedelta(days=random.randint(30, 60))

        for _ in range(number_of_bookings):
            duration = random.randint(1, 6)

            start_date = cursor
            end_date = start_date + timedelta(days=duration)

            # Keep bookings non-overlapping.
            cursor = end_date + timedelta(days=random.randint(2, 7))

            customer = random.choice(users["customer"])

            status = random.choice(possible_statuses)

            base_price = (vehicle.daily_rate * Decimal(duration)).quantize(
                Decimal("0.01")
            )

            coupon = random.choice(coupons + [None, None, None])

            discount_amount = calculate_discount(
                base_price,
                coupon,
            )

            total_price = max(
                base_price - discount_amount,
                Decimal("0.00"),
            )

            approval_deadline = None

            if status == BookingStatus.pending_approval:
                approval_deadline = now_utc() + timedelta(hours=24)

            booking = Booking(
                id=uuid.uuid4(),
                customer_id=customer.id,
                vehicle_id=vehicle.id,
                pickup_location_id=random.choice(locations).id,
                dropoff_location_id=random.choice(locations).id,
                start_date=start_date,
                end_date=end_date,
                status=status,
                base_price=base_price,
                discount_amount=discount_amount,
                total_price=total_price,
                currency="BDT",
                coupon_id=(coupon.id if coupon else None),
                deposit_hold_amount=(vehicle.deposit_amount),
                approval_deadline=approval_deadline,
                created_by=customer.id,
            )

            session.add(booking)
            bookings.append(booking)

            if coupon:
                session.add(
                    CouponUsage(
                        id=uuid.uuid4(),
                        coupon_id=coupon.id,
                        customer_id=customer.id,
                        booking_id=booking.id,
                    )
                )

                coupon.usage_count += 1

    session.flush()

    for booking in bookings:
        initial_status = (
            BookingStatus.pending_approval
            if booking.approval_deadline
            else BookingStatus.pending_payment
        )

        session.add(
            BookingStatusHistory(
                id=uuid.uuid4(),
                booking_id=booking.id,
                from_status=None,
                to_status=initial_status.value,
                changed_by=booking.created_by,
                reason="Booking created",
            )
        )

        if booking.status != initial_status:
            session.add(
                BookingStatusHistory(
                    id=uuid.uuid4(),
                    booking_id=booking.id,
                    from_status=initial_status.value,
                    to_status=booking.status.value,
                    changed_by=booking.created_by,
                    reason=(f"Booking moved to {booking.status.value}"),
                )
            )

    session.flush()

    for booking in bookings:
        if booking.status in (
            BookingStatus.pending_payment,
            BookingStatus.pending_approval,
            BookingStatus.rejected,
        ):
            continue

        if booking.status == BookingStatus.cancelled:
            payment_status = PaymentStatus.failed
        else:
            payment_status = PaymentStatus.succeeded

        session.add(
            Payment(
                id=uuid.uuid4(),
                booking_id=booking.id,
                type=PaymentType.charge,
                amount=booking.total_price,
                currency=booking.currency,
                status=payment_status,
                stripe_payment_intent_id=(f"pi_{uuid.uuid4().hex}"),
                idempotency_key=(f"seed_charge_{booking.id}"),
            )
        )

        if booking.status in (
            BookingStatus.confirmed,
            BookingStatus.active,
            BookingStatus.completed,
        ):
            session.add(
                Payment(
                    id=uuid.uuid4(),
                    booking_id=booking.id,
                    type=PaymentType.deposit_hold,
                    amount=booking.deposit_hold_amount,
                    currency=booking.currency,
                    status=PaymentStatus.succeeded,
                    stripe_payment_intent_id=(f"pi_{uuid.uuid4().hex}"),
                    idempotency_key=(f"seed_deposit_{booking.id}"),
                )
            )

        if booking.status == BookingStatus.completed:
            session.add(
                Payment(
                    id=uuid.uuid4(),
                    booking_id=booking.id,
                    type=PaymentType.deposit_release,
                    amount=booking.deposit_hold_amount,
                    currency=booking.currency,
                    status=PaymentStatus.succeeded,
                    stripe_payment_intent_id=(f"pi_{uuid.uuid4().hex}"),
                    idempotency_key=(f"seed_release_{booking.id}"),
                )
            )

    session.flush()

    return bookings


def seed_reviews(
    session,
    bookings: list[Booking],
) -> None:
    for booking in bookings:
        if booking.status != BookingStatus.completed:
            continue

        if random.random() > 0.7:
            continue

        review = Review(
            id=uuid.uuid4(),
            booking_id=booking.id,
            customer_id=booking.customer_id,
            vehicle_id=booking.vehicle_id,
            rating=random.randint(3, 5),
            comment=fake.sentence(nb_words=12),
        )

        session.add(review)

    session.flush()


def seed_condition_reports(
    session,
    bookings: list[Booking],
    staff_id: uuid.UUID,
) -> None:
    for booking in bookings:
        if booking.status not in (
            BookingStatus.active,
            BookingStatus.completed,
        ):
            continue

        check_in_odometer = random.randint(
            10000,
            80000,
        )

        check_in = ConditionReport(
            id=uuid.uuid4(),
            booking_id=booking.id,
            type=ReportType.check_in,
            odometer_km=check_in_odometer,
            fuel_level_pct=random.choice([50, 75, 100]),
            notes=("Vehicle inspected and handed over to customer."),
            recorded_by=staff_id,
        )

        session.add(check_in)
        session.flush()

        session.add(
            ConditionReportImage(
                id=uuid.uuid4(),
                condition_report_id=check_in.id,
                image_url=(f"https://picsum.photos/seed/{check_in.id}/800/600"),
            )
        )

        if booking.status == BookingStatus.completed:
            check_out = ConditionReport(
                id=uuid.uuid4(),
                booking_id=booking.id,
                type=ReportType.check_out,
                odometer_km=(check_in_odometer + random.randint(50, 500)),
                fuel_level_pct=random.choice([25, 50, 75]),
                notes=("Vehicle returned and inspected after rental."),
                recorded_by=staff_id,
            )

            session.add(check_out)
            session.flush()

            session.add(
                ConditionReportImage(
                    id=uuid.uuid4(),
                    condition_report_id=check_out.id,
                    image_url=(f"https://picsum.photos/seed/{check_out.id}/800/600"),
                )
            )

    session.flush()


def seed_maintenance_blocks(
    session,
    vehicles: list[Vehicle],
    staff_id: uuid.UUID,
) -> None:
    selected_vehicles = random.sample(
        vehicles,
        k=max(1, len(vehicles) // 4),
    )

    for vehicle in selected_vehicles:
        start_date = date.today() + timedelta(days=random.randint(60, 90))

        end_date = start_date + timedelta(days=random.randint(1, 4))

        maintenance = MaintenanceBlock(
            id=uuid.uuid4(),
            vehicle_id=vehicle.id,
            start_date=start_date,
            end_date=end_date,
            reason=random.choice(
                [
                    "Scheduled service",
                    "Brake inspection",
                    "Oil change",
                    "Tire replacement",
                    "General maintenance",
                ]
            ),
            created_by=staff_id,
        )

        session.add(maintenance)

    session.flush()


def seed_notifications(
    session,
    users: dict[str, list[User]],
    bookings: list[Booking],
) -> None:
    if not bookings:
        return

    selected_bookings = random.sample(
        bookings,
        k=min(10, len(bookings)),
    )

    for booking in selected_bookings:
        is_sent = random.choice([True, True, True, False])

        notification = Notification(
            id=uuid.uuid4(),
            user_id=booking.customer_id,
            channel=random.choice(list(NotificationChannel)),
            type="booking_status_update",
            payload={
                "booking_id": str(booking.id),
                "status": booking.status.value,
            },
            status=(NotificationStatus.sent if is_sent else NotificationStatus.queued),
            sent_at=(now_utc() if is_sent else None),
        )

        session.add(notification)

    session.flush()


def seed_audit_logs(
    session,
    users: dict[str, list[User]],
    vehicles: list[Vehicle],
) -> None:
    admin = users["admin"][0]

    selected_vehicles = random.sample(
        vehicles,
        k=min(5, len(vehicles)),
    )

    for vehicle in selected_vehicles:
        session.add(
            AuditLog(
                id=uuid.uuid4(),
                actor_id=admin.id,
                action="vehicle.created",
                entity_type="vehicle",
                entity_id=vehicle.id,
                meta={
                    "source": "seed_script",
                },
            )
        )

    session.flush()


def main() -> None:
    print("Starting database seed...")

    with SessionLocal() as session:
        with session.begin():
            print("Creating users...")
            users = seed_users(session)

            print("Creating locations...")
            locations = seed_locations(session)

            print("Creating vehicle categories...")
            categories = seed_categories(session)

            print("Creating vehicles and images...")
            vehicles = seed_vehicles(
                session,
                categories,
                locations,
            )

            print("Creating coupons...")
            coupons = seed_coupons(session)

            print("Creating bookings, status history and payments...")
            bookings = seed_bookings(
                session,
                users,
                vehicles,
                locations,
                coupons,
            )

            print("Creating reviews...")
            seed_reviews(
                session,
                bookings,
            )

            print("Creating condition reports...")
            fleet_staff = users["fleet_staff"][0]

            seed_condition_reports(
                session,
                bookings,
                fleet_staff.id,
            )

            print("Creating maintenance blocks...")
            seed_maintenance_blocks(
                session,
                vehicles,
                fleet_staff.id,
            )

            print("Creating notifications...")
            seed_notifications(
                session,
                users,
                bookings,
            )

            print("Creating audit logs...")
            seed_audit_logs(
                session,
                users,
                vehicles,
            )

    print()
    print("Database seed completed successfully.")
    print()
    print("Seed summary:")
    print(f"  Users: {18}")
    print(f"  Vehicles: {len(vehicles)}")
    print(f"  Bookings: {len(bookings)}")
    print()
    print("Development password:")
    print(f"  {SEED_PASSWORD}")


if __name__ == "__main__":
    main()
