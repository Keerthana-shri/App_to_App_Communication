from fastapi import status
from fastapi import APIRouter
from src.app.services.generate_secret_service import generate_application_secret
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends

router = APIRouter(tags=["Generate Secret"], prefix="/application")

@router.post("/generate-secret", status_code=status.HTTP_201_CREATED)
def generate_secret_for_application(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """
    Generate a secure random secret for an application.

    This endpoint generates a cryptographically secure secret string
    that can be used as an application's secret key.

    Returns:

        dict: A dictionary containing the generated secret string under the "secret" key.
    """
    secret = generate_application_secret()
    return {"secret": secret}