from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_token, verify_password
from app.db.session import get_db
from app.models import AdminUser
from app.schemas.admin import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.scalar(select(AdminUser).where(AdminUser.username == data.username))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid credentials")
    token = create_token(user.username, settings.access_token_expire_minutes)
    response.set_cookie(
        "access_token", token, httponly=True, samesite="lax",
        secure=settings.app_env == "production",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return TokenResponse(access_token=token)

@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie("access_token")
