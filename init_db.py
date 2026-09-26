from database import Base, engine
from models.user import User
from models.diagnostic_centre import DiagnosticCentre
from models.diagnostic_test import DiagnosticTest
from models.booking import Booking
from models.payment import Payment

Base.metadata.create_all(bind=engine)

print("Database tables created successfully!")