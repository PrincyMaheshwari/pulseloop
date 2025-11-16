from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from app.core.config import settings
from app.utils.auth import get_current_user as auth_get_current_user

router = APIRouter()

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Dev login endpoint - simple echo bypass when AUTH_DEV_BYPASS is enabled
@router.post("/login")
async def login(email: Optional[str] = None, password: Optional[str] = None):
    """Login endpoint - dev bypass mode returns mock token"""
    if settings.AUTH_DEV_BYPASS:
        return TokenResponse(
            access_token="dev-bypass-token",
            token_type="bearer"
        )
    raise HTTPException(
        status_code=501, 
        detail="Production login not yet implemented. Use Azure AD authentication or enable AUTH_DEV_BYPASS for local development."
    )

@router.get("/me")
async def get_me(current_user=Depends(auth_get_current_user)):
    """Get current user"""
    return {
        "id": current_user["id"],
        "email": current_user.get("email"),
        "organization_id": current_user.get("organization_id"),
        "role": current_user.get("role"),
    }


