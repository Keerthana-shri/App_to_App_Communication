from pydantic import UUID4, BaseModel, Field


class ConsumerValidationRequest(BaseModel):
    consumer_id: UUID4 = Field(..., example="b9fd40b8-07a3-45dc-a253-e34d7d5dd73b")
    secret_hash: str = Field(..., example="8fdf8419-99e1-423e-947d-3513c1a02d92")


class ProviderValidationRequest(BaseModel):
    provider_id: UUID4 = Field(..., example="40d46134-a885-4e17-91ce-0be66ce832ff")
    secret_hash: str = Field(..., example="62f1a7e2-b1e7-4648-827c-0367aa3ed0f2")


class ApiKeyValidationRequest(BaseModel):
    api_key: str = Field(
        ...,
        example="gAAAAABoN2Sx2PVMeBXutBAIUctRT-gnxHUYUWS4tFpMjVV7NQkRipAA9qkyt45zIRV-CIroLdQLCJqoEqMzeofFba5t9YJUiSVuEYIKVJVa0_HtC0VVqKNqvvx4lhsTXjiTkGXtxhrp",
    )
    provider_id: UUID4 = Field(..., example="40d46134-a885-4e17-91ce-0be66ce832ff")
    secret_hash: str = Field(..., example="62f1a7e2-b1e7-4648-827c-0367aa3ed0f2")
