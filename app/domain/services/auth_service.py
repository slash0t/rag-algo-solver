import uuid
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.domain.exceptions import DomainException
from app.domain.repositories.user import UserRepository
from app.infrastructure.database.models import User
from app.settings.jwt import JWTConfig


class UsernameAlreadyExistsError(DomainException):
    pass


class InvalidCredentialsError(DomainException):
    pass


class AuthService:
    def __init__(self, user_repo: UserRepository, jwt_config: JWTConfig) -> None:
        self._user_repo = user_repo
        self._jwt_config = jwt_config
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def register(self, username: str, password: str) -> User:
        existing = await self._user_repo.get_by_username(username)
        if existing is not None:
            raise UsernameAlreadyExistsError(f"Username '{username}' is already taken")

        user = User(
            username=username,
            password_hash=self._pwd_context.hash(password),
        )
        return await self._user_repo.create(user)

    async def login(self, username: str, password: str) -> str:
        user = await self._user_repo.get_by_username(username)
        if user is None or not self._pwd_context.verify(password, user.password_hash):
            raise InvalidCredentialsError("Invalid username or password")

        return self._create_access_token(user.id)

    def _create_access_token(self, user_id: uuid.UUID) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._jwt_config.access_token_expire_minutes,
        )
        payload = {
            "sub": str(user_id),
            "exp": expire,
        }
        return jwt.encode(
            payload,
            self._jwt_config.secret_key,
            algorithm=self._jwt_config.algorithm,
        )

    def decode_token(self, token: str) -> uuid.UUID:
        payload = jwt.decode(
            token,
            self._jwt_config.secret_key,
            algorithms=[self._jwt_config.algorithm],
        )
        return uuid.UUID(payload["sub"])
