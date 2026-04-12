from fastapi import APIRouter, HTTPException, status

from app.container import APP_CONTAINER
from app.domain.services.auth_service import (
    InvalidCredentialsError,
    UsernameAlreadyExistsError,
)
from app.presentation.api.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(request: RegisterRequest) -> UserResponse:
    auth_service = APP_CONTAINER.auth_service()
    try:
        user = await auth_service.register(request.username, request.password)
    except UsernameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already taken",
        )
    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    auth_service = APP_CONTAINER.auth_service()
    try:
        access_token = await auth_service.login(request.username, request.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return TokenResponse(access_token=access_token)
