from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
DATABASE_URL = "postgresql+psycopg://mratunjay@localhost/eve_healthcare"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()


try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Test result:", result.scalar())

except Exception as e:
    print("Database connection failed!")
    print(e)

