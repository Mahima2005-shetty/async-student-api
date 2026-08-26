from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from database import get_db
from schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
)
from auth.auth_service import AuthService
from auth.security import create_access_token
from config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)

    try:
        user = await service.register_user(
            user_data.name,
            user_data.email,
            user_data.password
        )

        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "name": user.name,
            "email": user.email
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    service = AuthService(db)

    try:
        return await service.login_user(
            user_data.email,
            user_data.password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post(
    "/refresh",
    response_model=TokenResponse
)
async def refresh_token(
    request: RefreshTokenRequest
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: missing user ID"
            )

        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        new_access_token = create_access_token({
            "sub": str(user_id)
        })

        return {
            "access_token": new_access_token,
            "refresh_token": request.refresh_token,
            "token_type": "bearer"
        }

    except JWTError as e:
        print("JWT ERROR:", str(e))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )