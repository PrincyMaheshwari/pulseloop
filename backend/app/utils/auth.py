from typing import Optional

from fastapi import Header, HTTPException, status

from app.core.config import settings
from app.services.user_service import user_service
from app.utils.azure_ad import AzureADVerifier, AzureADVerificationError

_verifier: Optional[AzureADVerifier] = None

if settings.AZURE_AD_TENANT_ID and settings.AZURE_AD_CLIENT_ID:
    try:
        _verifier = AzureADVerifier(
            tenant_id=settings.AZURE_AD_TENANT_ID,
            audiences=settings.azure_ad_audiences,
        )
    except Exception as exc:  # pragma: no cover - configuration errors
        raise RuntimeError(f"Failed to initialise Azure AD verifier: {exc}") from exc


def _get_dev_bypass_user() -> dict:
    claims = {
        "oid": settings.AUTH_DEV_BYPASS_USER_OID,
        "preferred_username": settings.AUTH_DEV_BYPASS_USER_EMAIL,
        "email": settings.AUTH_DEV_BYPASS_USER_EMAIL,
        "name": settings.AUTH_DEV_BYPASS_USER_NAME,
        "roles": [settings.AUTH_DEV_BYPASS_USER_ROLE],
        "tid": settings.AUTH_DEV_BYPASS_TENANT_ID,
    }
    user = user_service.get_or_create_user_from_claims(claims)
    return {
        "id": user["id"],
        "email": user.get("email"),
        "organization_id": user.get("organization_id"),
        "role": user.get("role", settings.AZURE_AD_DEFAULT_ROLE),
        "claims": claims,
    }


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Validate a bearer token and return the associated user record."""
    if settings.AUTH_DEV_BYPASS:
        # Development bypass: ignore tokens entirely when enabled.
        return _get_dev_bypass_user()

    if not _verifier:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Azure AD authentication is not configured",
        )

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header missing")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid bearer token")

    try:
        claims = _verifier.validate(token)
    except AzureADVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    try:
        user = user_service.get_or_create_user_from_claims(claims)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to provision user account",
        ) from exc

    return {
        "id": user["id"],
        "email": user.get("email"),
        "organization_id": user.get("organization_id"),
        "role": user.get("role", settings.AZURE_AD_DEFAULT_ROLE),
        "claims": claims,
    }

