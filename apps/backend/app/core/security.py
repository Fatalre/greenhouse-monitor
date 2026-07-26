import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from jose import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()

def hash_password(value: str) -> str:
    return password_hash.hash(value)

def verify_password(value: str, hashed: str) -> bool:
    return password_hash.verify(value, hashed)

def generate_api_key() -> str:
    return secrets.token_urlsafe(32)

def hash_api_key(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()

def verify_api_key(value: str, hashed: str) -> bool:
    return secrets.compare_digest(hash_api_key(value), hashed)

def create_token(subject: str, minutes: int) -> str:
    exp = datetime.now(UTC) + timedelta(minutes=minutes)
    return jwt.encode({"sub": subject, "exp": exp}, settings.app_secret_key, algorithm="HS256")

def decode_token(token: str) -> str:
    return str(jwt.decode(token, settings.app_secret_key, algorithms=["HS256"])["sub"])
