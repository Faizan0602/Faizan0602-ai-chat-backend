from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db  # or from core.dependencies
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.core.security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(email=body.email, hashed_password=hash_password(body.password))
    db.add(user); db.commit(); db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.hashed_password
    ):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token(
        sub=user.email,
        role=user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }