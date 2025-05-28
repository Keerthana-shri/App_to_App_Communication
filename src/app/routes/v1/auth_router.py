from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.schemas.auth_schemas import (
    UserLoginInput,
    UserLoginOutput,
    UserRegisterRequest,
)
from src.app.services.auth_services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register(register_data: UserRegisterRequest, services=Depends(AuthService)):
    """
    **User Registration endpoint**

    This endpoint allows users to register by providing their details.

    **Parameters:**

        register_data (UserRegisterRequest): The registration details provided by the user.

    **Returns:**

        None: The response does not return any content, but a successful registration will return a 201 status code.

    **Raises:**

        HTTPException: If the registration data is invalid or if an error occurs during the registration process.
    """
    return services.register(data=register_data)


@router.post("/login", response_model=UserLoginOutput)
def login(register_data: UserLoginInput, services=Depends(AuthService)):
    """
    **User Login endpoint**

    This endpoint allows users to log in by providing their credentials.

    **Parameters:**

        register_data (UserLoginInput): The login credentials provided by the user.

    **Returns:**

        UserLoginOutput: The response containing the access token and refresh token.

    **Raises:**

        HTTPException: If the login credentials are invalid or if an error occurs during the login process.
    """
    return services.login(login_data=register_data)


@router.post("/refresh", response_model=UserLoginOutput)
def refresh(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    services=Depends(AuthService),
):
    """
    **Refreshes the access token using the provided token.**

    This endpoint validates the refresh token and issues a new access token.

    **Parameters:**

        token (HTTPAuthorizationCredentials): The refresh token provided in the Authorization header.

    **Returns:**

        UserLoginOutput: The response containing the new access token and refresh token.

    **Raises:**

        HTTPException: If the refresh token is invalid or expired.
    """
    return services.refresh_token(token=token.credentials)
