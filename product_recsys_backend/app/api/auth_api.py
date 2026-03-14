from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserOut
from typing import List

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/users", response_model=List[UserOut])
def get_users(db: Session = Depends(get_db)):
    """
    Get all users (simple list endpoint)
    """
    users = db.query(User).all()
    return users

@router.post("/login", response_model=UserOut)
def login(
    username: str = Body(..., embed=True),
    password: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    Simple login: find user by username (dummy password check).
    Returns user_id and username.
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Simple dummy check (replace with real hash check later if needed)
    if password != "123":  # Demo password
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return user

