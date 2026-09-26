from fastapi import APIRouter, status

from doc_processor.api.dependencies import AuthServiceDep
from doc_processor.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"],)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    user = await auth_service.register(
        email=str(request.email),
        password=request.password,
    )

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:

    access_token = await auth_service.login(
        email=str(request.email),
        password=request.password,
    )

    return TokenResponse(
        access_token=access_token,
    )