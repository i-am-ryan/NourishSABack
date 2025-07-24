from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from supabase import Client, create_client
from app.auth import auth_manager
from app.models.user import UserProfile
from app.config import settings

# HTTP Bearer token scheme
security = HTTPBearer()

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: Client = Depends(get_supabase_client)
) -> UserProfile:
    """Get current authenticated user from JWT token"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verify the token
        payload = auth_manager.verify_token(credentials.credentials)
        
        # Extract user information from token
        email: str = payload.get("email")
        user_id: str = payload.get("user_id")
        
        if email is None or user_id is None:
            raise credentials_exception
        
        # Fetch user from database
        result = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        if not result.data:
            raise credentials_exception
        
        user_data = result.data[0]
        return UserProfile(**user_data)
        
    except Exception:
        raise credentials_exception

async def get_current_active_user(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """Get current active user (must be active)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_admin(current_user: UserProfile = Depends(get_current_active_user)):
    """Require admin user type"""
    if current_user.user_type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user