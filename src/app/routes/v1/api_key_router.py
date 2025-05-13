from datetime import datetime, timezone
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

router = APIRouter()


@router.post("/consumers/{consumer_id}/api-key", response_model=APIKeyResponse)
def generate_api_key(
    consumer_id: UUID, request: APIKeyCreate, db: Session = Depends(get_db)
):
    service = APIKeyService(
        uow=APIKeyUnitOfWork(session_factory=lambda: db),
    )
    try:
        expires_at = datetime.combine(request.expires_at, datetime.max.time()).replace(
            tzinfo=timezone.utc
        )

        response = service.generate_api_key(
            consumer_application_id=consumer_id,
            provider_application_id=request.provider_id,
            secret_hash=request.secret_hash,
            api_key_owner_id=request.api_key_owner_id,
            permissions=request.permissions,
            expires_at=expires_at,
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
    service = APIKeyService(uow=APIKeyUnitOfWork(session_factory=lambda: db))
    response = service.get_all_api_keys(
        consumer_id=consumer_id, page=page, page_size=page_size
    )
    return response


@router.get(
    "/consumers/{consumer_id}/api-key/{api_key_id}", response_model=APIKeyDetailResponse
)
def get_api_key(consumer_id: UUID, api_key_id: UUID, db: Session = Depends(get_db)):
    service = APIKeyService(uow=APIKeyUnitOfWork(session_factory=lambda: db))
    api_key = service.get_api_key(api_key_id)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key


@router.patch("/consumers/{consumer_id}/api-key/{api_key_id}")
def update_api_key(
    consumer_id: UUID,
    api_key_id: UUID,
    request: APIKeyUpdate,
    db: Session = Depends(get_db),
):
    service = APIKeyService(uow=APIKeyUnitOfWork(session_factory=lambda: db))
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
    service.update_api_key(api_key_id, **request_data)
    return {"message": f"API key with ID {api_key_id} has been updated successfully."}


@router.delete("/consumers/{consumer_id}/api-key/{api_key_id}")
def delete_api_key(consumer_id: UUID, api_key_id: UUID, db: Session = Depends(get_db)):
    service = APIKeyService(uow=APIKeyUnitOfWork(session_factory=lambda: db))
    return service.delete_api_key(api_key_id)
