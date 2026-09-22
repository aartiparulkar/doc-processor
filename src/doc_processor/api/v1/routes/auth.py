from fastapi import APIRouter, status

from doc_processor.api.dependencies import AuthServiceDep
from doc_processor.schemas.auth import RegisterRequest, UserResponse

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