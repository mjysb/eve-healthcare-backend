from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "EVE Healthcare Backend is running"}

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models.user import User
from schemas import UserCreate
from auth import hash_password
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

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