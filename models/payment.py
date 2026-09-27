from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from datetime import datetime, timezone

from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    booking_id = Column(
        Integer,
        ForeignKey("bookings.id"),
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    event_id = Column(
    String(100),
    unique=True,
    nullable=True
    )
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )