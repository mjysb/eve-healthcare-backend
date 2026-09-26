from sqlalchemy import Column, Integer, DateTime, Float, String, ForeignKey
from datetime import datetime, timezone

from database import Base


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    test_id = Column(
        Integer,
        ForeignKey("diagnostic_tests.id"),
        nullable=False
    )

    centre_id = Column(
        Integer,
        ForeignKey("diagnostic_centres.id"),
        nullable=False
    )

    appointment_datetime = Column(
        DateTime,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )