import bcrypt
from app.core.config import settings
from jose import jwt
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
import random


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    if not isinstance(password, str):
        raise TypeError("Password must be a string")
    # Convert to bytes and hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def _create_token(data: dict, expires_delta: timedelta, token_type: str):
    to_encode = data.copy()
    expire = datetime.now() + expires_delta

    to_encode.update({
        "exp": expire,
        "type": token_type
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_tokens(data: dict):
    access_token = _create_token(
        data=data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access"
    )

    refresh_token = _create_token(
        data=data,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh"
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception:
        return None
    

def generate_otp(length: int = 6) -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def create_password_reset_token(email: str) -> str:
    """Create a password reset token valid for 15 minutes"""
    expires_delta = timedelta(minutes=15)
    return _create_token(
        data={"sub": email},
        expires_delta=expires_delta,
        token_type="password_reset"
    )


def verify_password_reset_token(token: str) -> str | None:
    """Verify password reset token and return email if valid"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        email: str = payload.get("sub")
        return email
    except Exception:
        return None