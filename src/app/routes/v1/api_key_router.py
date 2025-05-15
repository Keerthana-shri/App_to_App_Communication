from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.app.config.database import get_db
from src.app.config.settings import app_config
from src.app.schemas.api_key_schema import (
    APIKeyCreate,
    APIKeyDetailResponse,
    APIKeyListResponse,
    APIKeyResponse,
    APIKeyUpdate,
)
from src.app.services.api_key_service import APIKeyService
from src.app.services.unit_of_work import APIKeyUnitOfWork

router = APIRouter(tags=["Consumer"])


@router.post("/consumers/{consumer_id}/api-keys", response_model=APIKeyResponse)
def generate_api_key(
    consumer_id: UUID, request: APIKeyCreate, db: Session = Depends(get_db)
):
    """**Generates an API key for a consumer application.**

    This endpoint handles the creation of a new API key for a consumer application. It validates the provided details and securely generates the API key.

    **Args:**

        consumer_id (UUID): The ID of the consumer application.
        request (APIKeyCreate): The request payload containing API key details.
        db (Session): The database session dependency.

    **Returns:**

        APIKeyResponse: The response containing the generated API key.

    **Raises:**

        HTTPException: If validation fails or any error occurs during API key generation.
    """
    service = APIKeyService(
        uow=APIKeyUnitOfWork(),
    )
    try:
        response = service.generate_api_key(
            consumer_application_id=consumer_id,
            provider_application_id=request.provider_id,
            secret_hash=request.secret_hash,
            api_key_owner_id=request.api_key_owner_id,
            permissions=request.permissions,
            expires_at=request.expires_at,
            comment=request.comment,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/consumers/{consumer_id}/api-keys", response_model=APIKeyListResponse)
def get_all_api_keys(
    consumer_id: UUID,
    page: int = Query(1),
    page_size: int = Query(10),
    db: Session = Depends(get_db),
):
    """**Retrieves all API keys for a consumer application.**

    This endpoint fetches all API keys associated with a consumer application, with pagination support.

    **Args:**

        consumer_id (UUID): The ID of the consumer application.
        page (int): The page number for pagination.
        page_size (int): The number of items per page.
        db (Session): The database session dependency.

    **Returns:**

        APIKeyListResponse: The response containing the list of API keys.

    **Raises:**

        HTTPException: If any error occurs during retrieval.
    """
    service = APIKeyService(uow=APIKeyUnitOfWork())
    response = service.get_all_api_keys(
        consumer_id=consumer_id, page=page, page_size=page_size
    )
    return response


@router.get(
    "/consumers/{consumer_id}/api-keys/{api_key_id}",
    response_model=APIKeyDetailResponse,
)
def get_api_key(consumer_id: UUID, api_key_id: UUID, db: Session = Depends(get_db)):
    """**Retrieves a specific API key for a consumer application.**

    This endpoint fetches details of a specific API key associated with a consumer application.

    **Args:**

        consumer_id (UUID): The ID of the consumer application.
        api_key_id (UUID): The ID of the API key.
        db (Session): The database session dependency.

    **Returns:**

        APIKeyDetailResponse: The response containing the API key details.

    **Raises:**

        HTTPException: If the API key is not found.
    """
    service = APIKeyService(uow=APIKeyUnitOfWork())
    api_key = service.get_api_key(api_key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.patch("/consumers/{consumer_id}/api-keys/{api_key_id}")
def update_api_key(
    consumer_id: UUID,
    api_key_id: UUID,
    request: APIKeyUpdate,
    db: Session = Depends(get_db),
):
    """**Updates an existing API key for a consumer application.**

    This endpoint handles the update of an existing API key's details, ensuring restricted fields are not modified.

    **Args:**

        consumer_id (UUID): The ID of the consumer application.
        api_key_id (UUID): The ID of the API key.
        request (APIKeyUpdate): The request payload containing updated API key details.
        db (Session): The database session dependency.

    **Returns:**

        dict: A message confirming the successful update.

    **Raises:**

        HTTPException: If any error occurs during the update.
    """
    service = APIKeyService(uow=APIKeyUnitOfWork())
    restricted_fields = {
        "provider_id",
        "consumer_id",
        "api_key_owner_id",
        "created_at",
        "updated_at",
        "api_key_id",
    }
    request_data = request.dict(exclude_unset=True)
    for field in restricted_fields:
        if field in request_data:
            if field in {"provider_id", "consumer_id"}:
                return {
                    "message": "To change provider_id or consumer_id, go to the application table."
                }
            elif field == "api_key_owner_id":
                return {"message": "To change api_key_owner_id, go to the user table."}
            else:
                return {"message": f"{field} cannot be changed."}
    return service.update_api_key(api_key_id, **request_data)


@router.delete("/consumers/{consumer_id}/api-keys/{api_key_id}")
def delete_api_key(consumer_id: UUID, api_key_id: UUID, db: Session = Depends(get_db)):
    """**Deletes an API key for a consumer application.**

    This endpoint handles the deletion of a specific API key associated with a consumer application.

    **Args:**

        consumer_id (UUID): The ID of the consumer application.
        api_key_id (UUID): The ID of the API key.
        db (Session): The database session dependency.

    **Returns:**

        dict: A message confirming the successful deletion.

    **Raises:**

        HTTPException: If any error occurs during deletion.
    """
    service = APIKeyService(uow=APIKeyUnitOfWork())
    return service.delete_api_key(api_key_id)
