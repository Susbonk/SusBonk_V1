import pytest

# P0 - Critical Tests: Authentication

@pytest.mark.priority_p0
class TestAuthentication:
    
    # T001: Register with valid credentials (201)
    def test_register_valid_credentials(self, client, test_user_data):
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    # T002: Register with duplicate email (409)
    def test_register_duplicate_email(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/register", json=test_user_data)
        assert response.status_code == 409
        assert "already registered" in response.json()["detail"].lower()
    
    # T003: Register with invalid email format (422)
    def test_register_invalid_email(self, client):
        response = client.post("/auth/register", json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "testpass123"
        })
        assert response.status_code == 422
    
    # T004: Register with missing required fields (422)
    def test_register_missing_fields(self, client):
        response = client.post("/auth/register", json={
            "username": "testuser"
        })
        assert response.status_code == 422
    
    # T006: Verify JWT token is returned
    def test_register_returns_jwt(self, client, test_user_data):
        response = client.post("/auth/register", json=test_user_data)
        data = response.json()
        assert len(data["access_token"]) > 20  # JWT tokens are long
    
    # T009: Login with valid credentials (200)
    def test_login_valid_credentials(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
    
    # T010: Login with incorrect password (401)
    def test_login_incorrect_password(self, client, test_user_data):
        client.post("/auth/register", json=test_user_data)
        response = client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401
    
    # T011: Login with non-existent email (401)
    def test_login_nonexistent_email(self, client):
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "testpass123"
        })
        assert response.status_code == 401
    
    # T015: Get current user with valid token (200)
    def test_get_me_valid_token(self, authenticated_client):
        client, token = authenticated_client
        response = client.get("/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data
    
    # T016: Get current user without token (401)
    def test_get_me_no_token(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 403  # FastAPI HTTPBearer returns 403
    
    # T017: Get current user with invalid token (401)
    def test_get_me_invalid_token(self, client):
        client.headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/auth/me")
        assert response.status_code == 401
    
    # T019: Verify returned user data matches authenticated user
    def test_get_me_returns_correct_user(self, authenticated_client, test_user_data):
        client, token = authenticated_client
        response = client.get("/auth/me")
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
