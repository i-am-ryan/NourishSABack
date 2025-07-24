import secrets
import string
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
import re

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityUtils:
    """Utility class for security-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password
    
    @staticmethod
    def generate_verification_token() -> str:
        """Generate a secure verification token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password strength and return detailed feedback"""
        feedback = {
            "is_valid": True,
            "errors": [],
            "strength": "weak"
        }
        
        # Minimum length check
        if len(password) < 8:
            feedback["errors"].append("Password must be at least 8 characters long")
            feedback["is_valid"] = False
        
        # Contains digit
        if not re.search(r"\d", password):
            feedback["errors"].append("Password must contain at least one digit")
            feedback["is_valid"] = False
        
        # Contains uppercase letter
        if not re.search(r"[A-Z]", password):
            feedback["errors"].append("Password must contain at least one uppercase letter")
            feedback["is_valid"] = False
        
        # Contains lowercase letter
        if not re.search(r"[a-z]", password):
            feedback["errors"].append("Password must contain at least one lowercase letter")
            feedback["is_valid"] = False
        
        return feedback
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Basic input sanitization"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ["<", ">", "&", "\"", "'"]
        for char in dangerous_chars:
            text = text.replace(char, "")
        
        return text.strip()
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int = 5, window: int = 300) -> bool:
        """
        Check if request is allowed based on rate limiting
        
        Args:
            key: Unique identifier (e.g., IP address, user ID)
            limit: Maximum requests allowed
            window: Time window in seconds (default: 5 minutes)
        """
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if (now - req_time).total_seconds() < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

# Global instances
security_utils = SecurityUtils()
rate_limiter = RateLimiter()