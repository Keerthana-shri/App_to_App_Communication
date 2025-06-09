from datetime import datetime

from pydantic import UUID4, BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Attributes:
        username (str): Unique username for the user.
        email (str): Email address of the user.
        password (str): Password for the user account.
    """

    name: str = Field(..., min_length=3, example="Arjun Kumar")
    email: EmailStr = Field(..., example="arjun@example.com")
    password: str = Field(..., min_length=8, max_length=15, example="Password123")


class UserRegisterResponse(BaseModel):
    """
    Schema for user registration response.

    Attributes:
        message (str): Confirmation message indicating successful registration.
    """

    id: UUID4 = Field(example="a057320f-bae9-43ed-974a-b2cd81f88f93")
    email: EmailStr = Field(example="arjun@email.com")
    name: str = Field(..., min_length=3, example="Arjun Kumar")
    created_at: datetime = Field(example="2023-10-01T12:00:00Z")


class UserLoginInput(BaseModel):
    email: EmailStr = Field(..., example="arjun@example.com")
    password: str = Field(..., example="Password123")


class UserLoginOutput(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huIiwidXNlcm5hbWUiOiJqb2huIiwicm9sZSI6InVzZXIiLCJ1c2VyX2lkIjoiYTA1NzMyMGYtYmFlOS00M2VkLTk3NGEtYjJjZDgxZjg4ZjkzIiwiZXhwIjoxNzM2ODQ3Nzc2fQ.2rNhLoBZyuRK3EVUlY1OAq7aTfBThnxjxLn-4PkiMeI",
    )
    token_type: str = Field(default="Bearer", example="Bearer")


class TokenInfo(BaseModel):
    """
    Schema for user registration response.

    Attributes:
        message (str): Confirmation message indicating successful registration.
    """

    id: UUID4 = Field(example="a057320f-bae9-43ed-974a-b2cd81f88f93")
    email: EmailStr = Field(example="arjun@email.com")
    name: str = Field(..., min_length=3, example="Arjun Kumar")

    class Config:
        """
        Configuration settings for Pydantic model serialization.

        Attributes:
            from_attributes (bool): Enables model population from ORM objects.
        """

        from_attributes = True
