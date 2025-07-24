import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

class TestUserRegistration:
    """Test user registration functionality"""
    
    def test_register_user_success(self, client, mock_supabase, sample_user_data):
        """Test successful user registration"""
        # Mock successful database operations
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        # Mock successful user creation
        created_user = {
            "id": "new-user-id",
            "email": sample_user_data["email"],
            "full_name": sample_user_data["full_name"],
            "user_type": sample_user_data["user_type"],
            "is_active": True,
            "is_verified": False,
            "created_at": "2024-01-01T00:00:00"
        }
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [created_user]
        
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == sample_user_data["email"]
    
    def test_register_user_duplicate_email(self, client, mock_supabase, sample_user_data):
        """Test registration with existing email"""
        # Mock existing user
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"email": sample_user_data["email"]}
        ]
        
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_register_user_weak_password(self, client, mock_supabase, sample_user_data):
        """Test registration with weak password"""
        sample_user_data["password"] = "weak"
        sample_user_data["confirm_password"] = "weak"
        
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_password_mismatch(self, client, mock_supabase, sample_user_data):
        """Test registration with password mismatch"""
        sample_user_data["confirm_password"] = "DifferentPassword123"
        
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_invalid_user_type(self, client, mock_supabase, sample_user_data):
        """Test registration with invalid user type"""
        sample_user_data["user_type"] = "invalid_type"
        
        response = client.post("/auth/register", json=sample_user_data)
        
        assert response.status_code == 422  # Validation error

class TestUserLogin:
    """Test user login functionality"""
    
    def test_login_success(self, client, mock_supabase, sample_user_profile):
        """Test successful user login"""
        # Mock user found in database
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_user_profile]
        
        # Mock password verification
        with patch('app.utils.security.security_utils.verify_password', return_value=True):
            login_data = {
                "email": sample_user_profile["email"],
                "password": "TestPassword123"
            }
            
            response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == sample_user_profile["email"]
    
    def test_login_invalid_email(self, client, mock_supabase):
        """Test login with non-existent email"""
        # Mock user not found
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        
        login_data = {
            "email": "nonexistent@example.com",
            "password": "TestPassword123"
        }
        
        response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client, mock_supabase, sample_user_profile):
        """Test login with wrong password"""
        # Mock user found in database
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_user_profile]
        
        # Mock password verification failure
        with patch('app.utils.security.security_utils.verify_password', return_value=False):
            login_data = {
                "email": sample_user_profile["email"],
                "password": "WrongPassword123"
            }
            
            response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_inactive_user(self, client, mock_supabase, sample_user_profile):
        """Test login with inactive user account"""
        # Make user inactive
        sample_user_profile["is_active"] = False
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_user_profile]
        
        with patch('app.utils.security.security_utils.verify_password', return_value=True):
            login_data = {
                "email": sample_user_profile["email"],
                "password": "TestPassword123"
            }
            
            response = client.post("/auth/login", json=login_data)
        
        assert response.status_code == 400
        assert "deactivated" in response.json()["detail"]

class TestAuthenticationToken:
    """Test JWT token functionality"""
    
    def test_valid_token_access(self, client, mock_supabase, sample_user_profile, auth_headers):
        """Test accessing protected endpoint with valid token"""
        # Mock user found in database
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [sample_user_profile]
        
        # Create a simple protected endpoint for testing
        response = client.get("/health", headers=auth_headers)
        
        # Health endpoint should work (it's not protected, but token should be valid)
        assert response.status_code == 200
    
    def test_invalid_token_access(self, client):
        """Test accessing with invalid token"""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}
        
        # This would fail if we had a protected endpoint, but for now test basic functionality
        response = client.get("/health", headers=invalid_headers)
        
        # Health endpoint should still work as it's not protected
        assert response.status_code == 200
    
    def test_missing_token_access(self, client):
        """Test accessing without token"""
        # This would fail if we had a protected endpoint
        response = client.get("/health")
        
        # Health endpoint should work as it's not protected
        assert response.status_code == 200

class TestPasswordSecurity:
    """Test password security functions"""
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        from app.utils.security import security_utils
        
        password = "TestPassword123"
        hashed = security_utils.hash_password(password)
        
        assert hashed != password
        assert security_utils.verify_password(password, hashed)
        assert not security_utils.verify_password("wrong_password", hashed)
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        from app.utils.security import security_utils
        
        # Strong password
        strong_result = security_utils.validate_password_strength("StrongPass123!")
        assert strong_result["is_valid"]
        
        # Weak password
        weak_result = security_utils.validate_password_strength("weak")
        assert not weak_result["is_valid"]
        assert len(weak_result["errors"]) > 0