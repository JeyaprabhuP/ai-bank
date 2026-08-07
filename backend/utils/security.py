"""JWT authentication utilities."""
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "dev-secret-key-change-me-in-production"  # demo only
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# Demo users. In production this would come from an identity provider / user DB.
DEMO_USERS = {
    "admin": {"password": "admin123", "role": "supervisor", "customer_id": None},
    "customer": {"password": "customer123", "role": "customer", "customer_id": "CUST0001"},
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = DEMO_USERS.get(username)
    if not user or user["password"] != password:
        return None
    return {"username": username, "role": user["role"], "customer_id": user["customer_id"]}


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_token(token)
    return {
        "username": payload.get("sub"),
        "role": payload.get("role"),
        "customer_id": payload.get("customer_id"),
    }
