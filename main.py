

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
app = FastAPI()


@app.get("/")
def home():
    return {"message": "EVE Healthcare Backend is running"}

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from models.diagnostic_centre import DiagnosticCentre
from schemas import (
    UserCreate,
    UserLogin,
    DiagnosticCentreCreate,
    DiagnosticTestCreate,
    BookingCreate,
    PaymentCreate,
    PaymentWebhook
)
from models.payment import Payment
from models.booking import Booking
from models.diagnostic_test import DiagnosticTest
from auth import hash_password, verify_password, create_access_token, verify_token

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("user_id")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return user_id

@app.post("/signup")
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id
    }

@app.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_correct = verify_password(
        user.password,
        existing_user.password_hash
    )

    if not password_correct:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "user_id": existing_user.id
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/me")
def get_me(current_user_id: int = Depends(get_current_user)):
    return {
        "user_id": current_user_id
    }

@app.post("/centres")
def create_centre(
    centre: DiagnosticCentreCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    new_centre = DiagnosticCentre(
        name=centre.name,
        location=centre.location
    )

    db.add(new_centre)
    db.commit()
    db.refresh(new_centre)

    return {
        "message": "Diagnostic centre created successfully",
        "centre_id": new_centre.id
    }

@app.post("/tests")
def create_test(
    test: DiagnosticTestCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    centre = db.query(DiagnosticCentre).filter(
        DiagnosticCentre.id == test.centre_id
    ).first()

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic centre not found"
        )

    new_test = DiagnosticTest(
        name=test.name,
        price=test.price,
        centre_id=test.centre_id
    )

    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    return {
        "message": "Diagnostic test created successfully",
        "test_id": new_test.id
    }

@app.get("/centres")
def get_centres(db: Session = Depends(get_db)):
    centres = db.query(DiagnosticCentre).all()

    return centres
@app.get("/tests")
def get_tests(db: Session = Depends(get_db)):
    tests = db.query(DiagnosticTest).all()

    return tests

@app.post("/bookings")
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    test = db.query(DiagnosticTest).filter(
        DiagnosticTest.id == booking.test_id
    ).first()

    if not test:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic test not found"
        )

    centre = db.query(DiagnosticCentre).filter(
        DiagnosticCentre.id == booking.centre_id
    ).first()

    if not centre:
        raise HTTPException(
            status_code=404,
            detail="Diagnostic centre not found"
        )

    if test.centre_id != booking.centre_id:
        raise HTTPException(
            status_code=400,
            detail="Test does not belong to this diagnostic centre"
        )

    new_booking = Booking(
        user_id=current_user_id,
        test_id=booking.test_id,
        centre_id=booking.centre_id,
        appointment_datetime=booking.appointment_datetime,
        amount=test.price,
        status="PENDING"
    )

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return {
        "message": "Booking created successfully",
        "booking_id": new_booking.id,
        "amount": new_booking.amount,
        "status": new_booking.status
    }
@app.post("/payments")
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user)
):
    booking = db.query(Booking).filter(
        Booking.id == payment.booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to pay for this booking"
        )

    if booking.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail="Booking is not pending"
        )

    # Simulate a successful payment
    payment_status = "SUCCESS"

    new_payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=payment_status
    )

    db.add(new_payment)

    booking.status = "CONFIRMED"

    db.commit()
    db.refresh(new_payment)

    return {
        "message": "Payment processed successfully",
        "payment_id": new_payment.id,
        "booking_id": booking.id,
        "amount": new_payment.amount,
        "payment_status": new_payment.status,
        "booking_status": booking.status
    }

@app.post("/payments/webhook")
def payment_webhook(
    webhook: PaymentWebhook,
    db: Session = Depends(get_db)
):

    existing_payment = db.query(Payment).filter(
        Payment.event_id == webhook.event_id
    ).first()
    
    if existing_payment:
        return {
            "message": "Webhook already processed",
            "booking_id": existing_payment.booking_id,
            "booking_status": "ALREADY_PROCESSED"
        }

    
    booking = db.query(Booking).filter(
        Booking.id == webhook.booking_id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )
    payment = db.query(Payment).filter(
    Payment.booking_id == booking.id
    ).first()

    if payment:
        payment.event_id = webhook.event_id
    else:
        payment = Payment(
            booking_id=booking.id,
            amount=booking.amount,
            status=webhook.status,
            event_id=webhook.event_id
        )
    db.add(payment)

    if webhook.status == "SUCCESS":
        booking.status = "CONFIRMED"

    elif webhook.status == "FAILED":
        booking.status = "FAILED"

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment status"
        )

    db.commit()
    db.refresh(booking)

    return {
        "message": "Payment webhook processed",
        "booking_id": booking.id,
        "booking_status": booking.status
    }