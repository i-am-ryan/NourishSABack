import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import os
from unittest.mock import Mock, patch

# Set test environment
os.environ["DEBUG"] = "true"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-key"

from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
async def async_client():
    """Create an async test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_supabase():
    """Mock Supabase client for testing"""
    with patch('app.dependencies.create_client') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        
        # Mock table operations
        mock_table = Mock()
        mock_instance.table.return_value = mock_table
        
        # Mock select operations
        mock_select = Mock()
        mock_table.select.return_value = mock_select
        mock_select.eq.return_value = mock_select
        
        # Mock execute with default empty result
        mock_execute = Mock()
        mock_execute.data = []
        mock_execute.count = 0
        mock_select.execute.return_value = mock_execute
        
        # Mock insert operations
        mock_insert = Mock()
        mock_table.insert.return_value = mock_insert
        mock_insert.execute.return_value = mock_execute
        
        # Mock update operations
        mock_update = Mock()
        mock_table.update.return_value = mock_update
        mock_update.eq.return_value = mock_update
        mock_update.execute.return_value = mock_execute
        
        yield mock_instance

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "full_name": "Test User",
        "phone_number": "0123456789",
        "user_type": "donor",
        "password": "TestPassword123",
        "confirm_password": "TestPassword123"
    }

@pytest.fixture
def sample_user_profile():
    """Sample user profile for testing"""
    return {
        "id": "test-user-id-123",
        "email": "test@example.com",
        "full_name": "Test User",
        "phone_number": "0123456789",
        "user_type": "donor",
        "is_active": True,
        "is_verified": False,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "password_hash": "$2b$12$hashed_password_here"
    }

@pytest.fixture
def auth_headers():
    """Generate auth headers with valid JWT token"""
    from app.auth import auth_manager
    
    token_data = {
        "user_id": "test-user-id-123",
        "email": "test@example.com",
        "user_type": "donor"
    }
    
    access_token = auth_manager.create_access_token(token_data)
    
    return {
        "Authorization": f"Bearer {access_token}"
    }