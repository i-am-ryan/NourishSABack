from fastapi import APIRouter, Depends, HTTPException, status, Request
from supabase import Client
from datetime import datetime
import uuid

from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.auth import auth_manager
from app.utils.security import security_utils, rate_limiter
from app.dependencies import get_supabase_client
from app.utils.constants import SUCCESS_MESSAGES, ERROR_MESSAGES

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """Register a new user account"""
    
    # Rate limiting check
    client_ip = request.client.host
    if not rate_limiter.is_allowed(f"register_{client_ip}", limit=5, window=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts. Please try again later."
        )
    
    try:
        # Check if user already exists
        existing_user = supabase.table("user_profiles").select("email").eq("email", user_data.email).execute()
        
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES["USER_EXISTS"]
            )
        
        # Validate password strength
        password_validation = security_utils.validate_password_strength(user_data.password)
        if not password_validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation failed: {', '.join(password_validation['errors'])}"
            )
        
        # Hash password
        hashed_password = security_utils.hash_password(user_data.password)
        
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Create user profile data
        user_profile = {
            "id": user_id,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "phone_number": user_data.phone_number,
            "user_type": user_data.user_type,
            "password_hash": hashed_password,
            "is_active": True,
            "is_verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert user into database
        result = supabase.table("user_profiles").insert(user_profile).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user account"
            )
        
        created_user = result.data[0]
        
        # Create JWT tokens
        token_data = {
            "user_id": user_id,
            "email": user_data.email,
            "user_type": user_data.user_type
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Prepare response
        user_response = UserResponse(
            id=created_user["id"],
            email=created_user["email"],
            full_name=created_user["full_name"],
            user_type=created_user["user_type"],
            is_active=created_user["is_active"],
            is_verified=created_user["is_verified"],
            created_at=created_user["created_at"]
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_manager.expire_minutes * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    request: Request,
    supabase: Client = Depends(get_supabase_client)
):
    """Login user and return JWT tokens"""
    
    # Rate limiting check
    client_ip = request.client.host
    if not rate_limiter.is_allowed(f"login_{client_ip}", limit=10, window=3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    try:
        # Find user by email
        result = supabase.table("user_profiles").select("*").eq("email", user_credentials.email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["INVALID_CREDENTIALS"]
            )
        
        user = result.data[0]
        
        # Verify password
        if not security_utils.verify_password(user_credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["INVALID_CREDENTIALS"]
            )
        
        # Check if user is active
        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated. Please contact support."
            )
        
        # Update last login
        supabase.table("user_profiles").update({
            "last_login": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user["id"]).execute()
        
        # Create JWT tokens
        token_data = {
            "user_id": user["id"],
            "email": user["email"],
            "user_type": user["user_type"]
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token(token_data)
        
        # Prepare response
        user_response = UserResponse(
            id=user["id"],
            email=user["email"],
            full_name=user["full_name"],
            user_type=user["user_type"],
            is_active=user["is_active"],
            is_verified=user["is_verified"],
            created_at=user["created_at"]
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_manager.expire_minutes * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )