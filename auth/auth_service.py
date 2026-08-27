from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User, Role
from auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


class AuthService:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(
        self,
        name: str,
        email: str,
        password: str
    ) -> User:

        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("User already exists")

        role_result = await self.db.execute(
            select(Role).where(Role.name == "student")
        )

        student_role = role_result.scalar_one_or_none()

        if not student_role:
            raise ValueError("Default student role not found")

        hashed_password = hash_password(password)

        user = User(
            name=name,
            email=email,
            hashed_password=hashed_password,
            role_id=student_role.id
        )

        self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def login_user(
        self,
        email: str,
        password: str
    ):

        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            password,
            user.hashed_password
        ):
            raise ValueError("Invalid email or password")

        token_data = {
            "sub": str(user.id)
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
