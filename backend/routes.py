from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from db import get_db
from models import User, Profile
from schemas import UserCreate, UserLogin, ProfileBase
from auth import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter()


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_profile = Profile(user_id=new_user.id)
    db.add(new_profile)
    db.commit()

    return {"message": "User registered successfully"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Email not registered. Please register first.")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user_email(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    token = authorization.split(" ")[1]
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return email

@router.get("/profile")
def get_profile(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email)
):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_profile = db.query(Profile).filter(Profile.user_id == db_user.id).first()
    if not db_profile or (
        not db_profile.age_group and not db_profile.gender and not db_profile.language
    ):
        return {}  # Treat empty profile as "no profile yet"

    return {
        "age_group": db_profile.age_group,
        "gender": db_profile.gender,
        "language": db_profile.language
    }

@router.put("/profile")
def update_profile(
    profile_data: ProfileBase,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user_email)
):
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_profile = db.query(Profile).filter(Profile.user_id == db_user.id).first()
    if not db_profile:
        db_profile = Profile(user_id=db_user.id)
        db.add(db_profile)

    db_profile.age_group = profile_data.age_group
    db_profile.gender = profile_data.gender
    db_profile.language = profile_data.language

    db.commit()
    db.refresh(db_profile)

    return {"message": "Profile updated successfully"}
