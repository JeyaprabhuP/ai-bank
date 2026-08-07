from fastapi import APIRouter, HTTPException
from models.schemas import LoginRequest, LoginResponse
from utils.security import authenticate_user, create_access_token

router = APIRouter(tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = authenticate_user(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({
        "sub": user["username"],
        "role": user["role"],
        "customer_id": user["customer_id"],
    })
    return LoginResponse(
        access_token=token,
        role=user["role"],
        username=user["username"],
        customer_id=user["customer_id"],
    )
