from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from src.app.config.settings import app_config
from src.app.schemas.auth_schemas import (
    UserLoginInput,
    UserLoginOutput,
    UserRegisterRequest,
)
from src.app.services.unit_of_work import UnitOfWork


class AuthService:
    """
    Service for handling secret encryption and verification.
    """

    def __init__(self):
        self.uow = UnitOfWork()
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def create_access_token(data: dict) -> str:
        """
        Creates access token using python-jose library
        """
        to_encode = data.copy()
        to_encode["user_id"] = str(to_encode["user_id"])
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=int(app_config["ACCESS_TOKEN_EXPIRE_MINUTES"])
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, app_config["SECRET_KEY"], algorithm=app_config["ALGORITHM"]
        )
        return encoded_jwt

    def get_password_hash(self, password: str) -> str:
        """
        Hashes the password using passlib.
        """
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifies a password using passlib.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def refresh_token(self, token: str) -> dict:
        """
        Refreshes an access token.
        """
        if not token:
            raise HTTPException(
                status_code=401, detail="Authorization Header Not Provided"
            )
        try:
            to_encode = jwt.decode(
                token, app_config["SECRET_KEY"], algorithms=[app_config["ALGORITHM"]]
            )
            to_encode.pop("exp", None)  # Remove old expiration
            access_token = self.create_access_token(to_encode)
            return {"access_token": access_token, "token_type": "Bearer"}
        except ExpiredSignatureError as exc:
            raise HTTPException(status_code=401, detail="Token has expired.") from exc
        except JWTError as exc:
            raise HTTPException(status_code=401, detail="Invalid token.") from exc

    def register(self, data: UserRegisterRequest):
        """
        Registers a new user.

        """
        with self.uow as uow:
            user = uow.user.get(email=data.email)
            if user:
                raise HTTPException(status_code=409, detail="Email already exists.")
            hashed_password = self.get_password_hash(data.password)
            uow.user.add(name=data.name, email=data.email, password=hashed_password)
            return uow.user.get(email=data.email)

    def login(self, login_data: UserLoginInput) -> UserLoginOutput:
        """
        Logs in a user and returns an access token.
        """
        with self.uow as uow:
            user = uow.user.get(email=login_data.email)
            if not user or not self.verify_password(login_data.password, user.password):
                raise HTTPException(
                    status_code=401, detail="Invalid email or password."
                )
            access_token = self.create_access_token(
                data={"user_id": str(user.id), "email": user.email, "name": user.name}
            )
            return UserLoginOutput(access_token=access_token, token_type="Bearer")
