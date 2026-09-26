from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class DiagnosticCentreCreate(BaseModel):
    name: str
    location: str


class DiagnosticTestCreate(BaseModel):
    name: str
    price: float
    centre_id: int

class BookingCreate(BaseModel):
    test_id: int
    centre_id: int
    appointment_datetime: datetime 
      
class PaymentCreate(BaseModel):
    booking_id: int