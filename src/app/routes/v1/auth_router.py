from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.schemas.auth_schemas import (
    TokenInfo,
    UserLoginInput,
    UserLoginOutput,
    UserRegisterRequest,
    UserRegisterResponse,
)
from src.app.services.auth_services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
auth_service = AuthService()


@router.post("/register", status_code=201, response_model=UserRegisterResponse)
def register(register_data: UserRegisterRequest):
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
    return auth_service.register(data=register_data)


@router.post("/login", response_model=UserLoginOutput)
def login(register_data: UserLoginInput):
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
    return auth_service.login(login_data=register_data)


@router.post("/refresh", response_model=UserLoginOutput)
def refresh(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    current_user: UserRegisterResponse = Depends(auth_service.get_current_user),
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
    return auth_service.refresh_token(token=token.credentials)


@router.get("/me", response_model=TokenInfo)
def me(current_user: UserRegisterResponse = Depends(auth_service.get_current_user)):
    """
    **Returns the current authenticated user.**

    This endpoint retrieves the details of the currently authenticated user.

    **Parameters:**

        current_user (UserRegisterResponse): The current authenticated user.

    **Returns:**

        TokenInfo: The details of the current user, including their ID, email, and name.
    """
    return current_user
