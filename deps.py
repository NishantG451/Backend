from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlalchemy.orm import Session

from database import SessionLocal
from models import User
from config import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    user = db.query(User).filter(User.id == payload["id"]).first()

    if not user:
        raise HTTPException(401, "Invalid user")

    return user