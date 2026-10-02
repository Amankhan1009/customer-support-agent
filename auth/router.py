from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import LoginRequest, TokenResponse, UserResponse
from auth.security import (
    create_access_token,
    create_user,
    get_current_user,
    get_user,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: LoginRequest) -> TokenResponse:
    if get_user(request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered.",
        )
    create_user(request.username, request.password)
    token = create_access_token({"sub": request.username})
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest) -> TokenResponse:
    user = get_user(request.username)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token({"sub": request.username})
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return UserResponse(username=current_user["username"])