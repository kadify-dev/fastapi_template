from datetime import datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import InvalidTokenError, TokenError, TokenExpiredError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_token(data: dict, expire_delta: timedelta) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + expire_delta
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token, token_type):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        exp = payload.get("exp")
        current_token_type = payload.get("type")

        if current_token_type != token_type:
            raise InvalidTokenError(detail="Invalid token type")

        if not exp:
            raise InvalidTokenError(detail="Token expiration not set")

        if datetime.utcfromtimestamp(exp) < datetime.utcnow():
            raise TokenExpiredError()

        sub = payload.get("sub")
        if not sub:
            raise InvalidTokenError(detail="Subject not found in token")

        return sub

    except jwt.PyJWTError as e:
        raise TokenError(detail=str(e))
