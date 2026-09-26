from sqlalchemy import Column, Integer, String, Float, ForeignKey

from database import Base


class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    centre_id = Column(
        Integer,
        ForeignKey("diagnostic_centres.id"),
        nullable=False
    )