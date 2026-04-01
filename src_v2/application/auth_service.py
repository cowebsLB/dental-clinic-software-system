from dataclasses import dataclass
from typing import Optional

import bcrypt

from src_v2.application.ports import UserRepository
from src_v2.shared.result import Result


@dataclass(frozen=True)
class Session:
    user_id: str
    username: str
    role: str


class AuthService:
    def __init__(self, users: UserRepository):
        self._users = users
        self._active_session: Optional[Session] = None

    def login(self, username: str, password: str) -> Result[Session]:
        user = self._users.get_by_username(username)
        if not user or not user.is_active:
            return Result.failure("Invalid credentials")
        if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
            return Result.failure("Invalid credentials")
        session = Session(user_id=user.id, username=user.username, role=user.role)
        self._active_session = session
        return Result.success(session)

    def logout(self) -> None:
        self._active_session = None

    def current_session(self) -> Optional[Session]:
        return self._active_session
