"""
Auth API router - authentication endpoints
"""

import typing
from typing import Annotated

from fastapi import APIRouter, Depends, Response, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)

from .use_case import AuthUseCase, get_auth_use_case
from . import schemas
from .schemas import Platform


router = APIRouter(prefix="/v1/auth", tags=["Authentication"])


@router.post("/token", summary="Get OAuth2 access token")
async def login_for_access_token(
    form_data: typing.Annotated[OAuth2PasswordRequestForm, Depends()],
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> schemas.GetAccessTokenResponse:
    """Get access token using username and password."""
    return await use_case.login_for_access_token(form_data)


@router.post("/login", response_model=schemas.Token)
async def login(
    response: Response,
    form_data: schemas.SignIn,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> schemas.Token:
    """Login and get access + refresh tokens."""
    token = await use_case.authenticate(form_data)
    if form_data.platform == Platform.WEB:
        response.set_cookie(
            key="refresh_token",
            value=token.refresh_token,
            httponly=True,
            samesite="strict",
            secure=True,  # Recommended for production
        )
        # Hide refresh token from the response body
        token.refresh_token = None

    return token


@router.post("/logout", response_model=schemas.Message)
async def logout(
    response: Response,
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> schemas.Message:
    """Logout and clear refresh token cookie."""
    await use_case.logout()
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="strict",
        secure=True,  # Recommended for production
    )
    return schemas.Message(detail="Successfully logged out")


@router.get("/refresh_token")
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Security(HTTPBearer())],
    use_case: AuthUseCase = Depends(get_auth_use_case),
) -> schemas.GetAccessTokenResponse:
    """Refresh access token using refresh token."""
    return await use_case.refresh_token(credentials)
