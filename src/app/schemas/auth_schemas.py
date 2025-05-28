from pydantic import UUID4, BaseModel, Field


class UserRegisterRequest(BaseModel):
    """
    Schema for user registration request.

    Attributes:
        username (str): Unique username for the user.
        email (str): Email address of the user.
        password (str): Password for the user account.
    """

    name: str = Field(..., min_length=3, example="Arjun Kumar")
    email: str = Field(..., min_length=3, example="arjun@example.com")
    password: str = Field(..., min_length=8, max_length=15, example="Password123")


class UserLoginInput(BaseModel):
    email: str = Field(..., min_length=3, example="arjun@example.com")
    password: str = Field(..., example="Password123")


class UserLoginOutput(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huIiwidXNlcm5hbWUiOiJqb2huIiwicm9sZSI6InVzZXIiLCJ1c2VyX2lkIjoiYTA1NzMyMGYtYmFlOS00M2VkLTk3NGEtYjJjZDgxZjg4ZjkzIiwiZXhwIjoxNzM2ODQ3Nzc2fQ.2rNhLoBZyuRK3EVUlY1OAq7aTfBThnxjxLn-4PkiMeI",
    )
    token_type: str = Field(default="Bearer", example="Bearer")
