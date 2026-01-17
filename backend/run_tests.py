#!/usr/bin/env python3
"""
Simple test runner for SusBonk API
Runs tests without requiring pytest installation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.helper import Base, get_db
from main import app
from database.models import Prompt, User
from api.security import hash_password

# Setup test database
TEST_DATABASE_URL = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def setup(self):
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)
        self.db = TestingSessionLocal()
    
    def teardown(self):
        self.db.close()
        Base.metadata.drop_all(bind=engine)
        if os.path.exists("test.db"):
            os.remove("test.db")
    
    def run_test(self, name, test_func):
        try:
            self.setup()
            test_func()
            self.passed += 1
            print(f"✓ {name}")
        except AssertionError as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"✗ {name}: {e}")
        except Exception as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"✗ {name}: ERROR - {e}")
        finally:
            self.teardown()
    
    def register_user(self):
        response = self.client.post("/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        })
        return response.json()["access_token"]
    
    def print_summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"Test Results: {self.passed}/{total} passed")
        print(f"{'='*70}")
        if self.errors:
            print("\nFailed Tests:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")

runner = TestRunner()

# P0 Critical Tests

print("Running P0 Critical Tests...")
print("="*70)

# Authentication Tests
print("\n[Authentication Tests]")

def test_register_valid():
    response = runner.client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

runner.run_test("T001: Register with valid credentials", test_register_valid)

def test_register_duplicate():
    runner.client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    response = runner.client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 409

runner.run_test("T002: Register with duplicate email", test_register_duplicate)

def test_register_invalid_email():
    response = runner.client.post("/auth/register", json={
        "username": "testuser",
        "email": "invalid-email",
        "password": "testpass123"
    })
    assert response.status_code == 422

runner.run_test("T003: Register with invalid email", test_register_invalid_email)

def test_login_valid():
    runner.client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    response = runner.client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

runner.run_test("T009: Login with valid credentials", test_login_valid)

def test_login_wrong_password():
    runner.client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    response = runner.client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

runner.run_test("T010: Login with incorrect password", test_login_wrong_password)

def test_get_me_valid():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    response = runner.client.get("/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data

runner.run_test("T015: Get current user with valid token", test_get_me_valid)

def test_get_me_no_token():
    response = runner.client.get("/auth/me")
    assert response.status_code in [401, 403]  # Either is acceptable

runner.run_test("T016: Get current user without token", test_get_me_no_token)

# Route Conflict Tests
print("\n[Route Conflict Tests]")

def test_custom_route_works():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    response = runner.client.get("/prompts/custom")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data

runner.run_test("T116: /prompts/custom returns list", test_custom_route_works)

def test_uuid_route_works():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    
    # Create system prompt
    prompt = Prompt(name="Test", prompt_text="Text")
    runner.db.add(prompt)
    runner.db.commit()
    
    response = runner.client.get(f"/prompts/{prompt.id}")
    assert response.status_code == 200

runner.run_test("T117: /prompts/{uuid} returns prompt", test_uuid_route_works)

# CRUD Tests
print("\n[Critical CRUD Tests]")

def test_create_custom_prompt():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    response = runner.client.post("/prompts/custom", json={
        "name": "Test",
        "prompt_text": "Text"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Test"

runner.run_test("T046: Create custom prompt", test_create_custom_prompt)

def test_update_custom_prompt():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = runner.client.post("/prompts/custom", json={
        "name": "Original",
        "prompt_text": "Text"
    })
    prompt_id = create_resp.json()["id"]
    
    response = runner.client.patch(f"/prompts/custom/{prompt_id}", json={
        "name": "Updated"
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Updated"

runner.run_test("T053: Update custom prompt", test_update_custom_prompt)

def test_delete_custom_prompt():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    
    create_resp = runner.client.post("/prompts/custom", json={
        "name": "ToDelete",
        "prompt_text": "Text"
    })
    prompt_id = create_resp.json()["id"]
    
    response = runner.client.delete(f"/prompts/custom/{prompt_id}")
    assert response.status_code == 204

runner.run_test("T061: Delete custom prompt", test_delete_custom_prompt)

def test_list_system_prompts():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    
    # Add prompts
    for i in range(3):
        prompt = Prompt(name=f"Prompt {i}", prompt_text=f"Text {i}")
        runner.db.add(prompt)
    runner.db.commit()
    
    response = runner.client.get("/prompts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3

runner.run_test("T020: List system prompts", test_list_system_prompts)

def test_list_chats():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    response = runner.client.get("/chats")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data

runner.run_test("T069: List user chats", test_list_chats)

# Security Tests
print("\n[Security Tests]")

def test_password_not_in_response():
    token = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token}"}
    response = runner.client.get("/auth/me")
    data = response.json()
    assert "password" not in data
    assert "password_hash" not in data

runner.run_test("T146: Password not in response", test_password_not_in_response)

def test_cannot_access_other_user_prompts():
    # User 1
    token1 = runner.register_user()
    runner.client.headers = {"Authorization": f"Bearer {token1}"}
    create_resp = runner.client.post("/prompts/custom", json={
        "name": "Private",
        "prompt_text": "Text"
    })
    prompt_id = create_resp.json()["id"]
    
    # User 2
    response2 = runner.client.post("/auth/register", json={
        "username": "user2",
        "email": "user2@example.com",
        "password": "pass123"
    })
    token2 = response2.json()["access_token"]
    runner.client.headers = {"Authorization": f"Bearer {token2}"}
    
    response = runner.client.get(f"/prompts/custom/{prompt_id}")
    assert response.status_code == 404

runner.run_test("T147: Cannot access other user's prompts", test_cannot_access_other_user_prompts)

runner.print_summary()

# Exit with error code if any tests failed
sys.exit(0 if runner.failed == 0 else 1)
