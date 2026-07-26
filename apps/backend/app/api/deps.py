from fastapi import Cookie, Depends, Header, HTTPException
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.models import AdminUser


def device_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key:
        raise HTTPException(401, "Missing X-API-Key")
    return x_api_key

def current_admin(
    access_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token = access_token
    if not token and authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
    if not token:
        raise HTTPException(401, "Authentication required")
    try:
        username = decode_token(token)
    except JWTError:
        raise HTTPException(401, "Invalid token") from None
    user = db.scalar(select(AdminUser).where(
        AdminUser.username == username, AdminUser.is_active.is_(True)
    ))
    if not user:
        raise HTTPException(401, "Invalid user")
    return user
