from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.services.api_key_service import APIKeyService
from src.app.services.unit_of_work import UnitOfWork

router = APIRouter(tags=["API Keys"])


@router.post("/api-keys/rotate", status_code=200)
def rotate_api_keys(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
):
    """**Rotates all active API keys.**

    This endpoint triggers the rotation of all active API keys.

    **Returns:**

        dict: A message indicating the successful rotation of API keys.

    **Raises:**

        HTTPException: If an error occurs during the rotation process.
    """
    service = APIKeyService(uow=UnitOfWork())
    count = service.rotate_api_keys()
    return {"message": f"{count} active API keys rotated"}
