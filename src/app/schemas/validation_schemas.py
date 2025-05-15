from pydantic import UUID4, BaseModel


class ConsumerValidationRequest(BaseModel):
    consumer_id: UUID4
    secret_hash: str


class ProviderValidationRequest(BaseModel):
    provider_id: UUID4
    secret_hash: str


class ApiKeyValidationRequest(BaseModel):
    api_key: str
    provider_id: UUID4
