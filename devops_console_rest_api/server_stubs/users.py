from uuid import UUID

from pydantic import EmailStr
from devops_console_rest_api.core.security import verify_password, get_password_hash
from devops_console_rest_api.core.config import settings
from devops_console_rest_api.models import User, UserInDB, UserCreate


class UserServerStub:
    def __init__(self) -> None:
        self._users: list[UserInDB] = []
        # FIXME this flow only works for development and testing purposes
        for (username, user) in settings.MOCK_USERS.items():
            self.create_user(
                UserCreate(
                    username=username,
                    email=user["email"],
                    full_name=user["full_name"],
                    password=user["password"],
                )
            )
        # add superuser with superpowers
        su = UserCreate(
            username=settings.SUPERUSER_USERNAME,
            email=settings.SUPERUSER_USERNAME,
            full_name=settings.SUPERUSER_USERNAME,
            password=settings.SUPERUSER_PASSWORD,
            is_admin=True,
        )
        self.create_user(su)

    def get_user(
        self, *, uuid: UUID | None = None, email: EmailStr | None = None
    ) -> UserInDB | None:
        for u in self._users:
            if uuid and uuid == str(u.uuid):
                return u
            if email and email == u.email:
                return u
        return None

    def verify_user(self, user: UserInDB, password: str) -> bool:
        return verify_password(password, user.hashed_pw)

    def create_user(self, user: UserCreate) -> None:
        user_in_db = UserInDB(**user.dict(), hashed_pw=get_password_hash(user.password))

        self._users.append(user_in_db)
