#!/usr/bin/env python3
"""
Task Validation Test - Tasks 2-8
Tests runtime upgrade, directory structure, settings, db_helper, models, schemas, and auth
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_task_2_runtime():
    """Task 2: Python 3.13 + uv runtime"""
    print("✓ Task 2: Python version check")
    assert sys.version_info >= (3, 13), f"Python 3.13+ required, got {sys.version_info}"
    print(f"  Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def test_task_3_imports():
    """Task 3: Directory structure and imports"""
    print("✓ Task 3: Import structure")
    
    # Test core imports
    from core import settings, db_helper
    print("  Core imports: ✓")
    
    # Test model imports
    from models import User, Chat, Prompt, CustomPrompt, RuntimeStatistics, ChatPrompts, ChatCustomPrompts, UserState
    print("  Model imports: ✓")
    
    # Test schema imports
    from schemas import UserRegister, UserLogin, Token, UserResponse
    print("  Schema imports: ✓")

def test_task_4_settings():
    """Task 4: Settings standardization"""
    print("✓ Task 4: Settings")
    
    from core.settings import settings
    
    # Check UPPERCASE fields
    assert hasattr(settings, 'POSTGRES_HOST'), "Missing POSTGRES_HOST"
    assert hasattr(settings, 'JWT_SECRET'), "Missing JWT_SECRET"
    assert hasattr(settings, 'DATABASE_URL'), "Missing DATABASE_URL property"
    
    # Check computed DATABASE_URL
    db_url = settings.DATABASE_URL
    assert db_url.startswith('postgresql+asyncpg://'), f"Invalid DATABASE_URL: {db_url}"
    print(f"  DATABASE_URL: {db_url[:50]}...")

def test_task_5_db_helper():
    """Task 5: db_helper pattern"""
    print("✓ Task 5: Database helper")
    
    from core.db_helper import db_helper
    
    # Check session_getter method exists
    assert hasattr(db_helper, 'session_getter'), "Missing session_getter method"
    assert hasattr(db_helper, 'dispose'), "Missing dispose method"
    print("  db_helper methods: ✓")

def test_task_6_models():
    """Task 6: Typed SQLAlchemy 2.0 models"""
    print("✓ Task 6: ORM Models")
    
    from models import User, Chat, Prompt, CustomPrompt, ChatPrompts, ChatCustomPrompts
    
    # Check typed annotations exist
    assert hasattr(User, '__annotations__'), "User model missing type annotations"
    assert hasattr(Chat, '__annotations__'), "Chat model missing type annotations"
    
    # Check relationships
    assert hasattr(User, 'chats'), "User missing chats relationship"
    assert hasattr(Chat, 'user'), "Chat missing user relationship"
    print("  Model relationships: ✓")

def test_task_7_schemas():
    """Task 7: Pydantic v2 schemas"""
    print("✓ Task 7: Pydantic schemas")
    
    from schemas.auth import UserResponse
    from schemas.chat import ChatResponse
    
    # Check ConfigDict usage
    assert hasattr(UserResponse, 'model_config'), "UserResponse missing model_config"
    assert hasattr(ChatResponse, 'model_config'), "ChatResponse missing model_config"
    print("  Schema ConfigDict: ✓")

def test_task_8_auth():
    """Task 8: Argon2 + pyjwt auth"""
    print("✓ Task 8: Authentication")
    
    from core.security import hash_password, verify_password, create_access_token
    
    # Test password hashing
    password = "test123"
    hashed = hash_password(password)
    assert hashed != password, "Password not hashed"
    assert verify_password(password, hashed), "Password verification failed"
    
    # Test JWT creation
    token = create_access_token({"sub": "test-user-id"})
    assert isinstance(token, str), "Token not string"
    assert len(token) > 50, "Token too short"
    print("  Argon2 + JWT: ✓")

def main():
    """Run all validation tests"""
    print("=== Task Validation Tests (Tasks 2-8) ===\n")
    
    try:
        test_task_2_runtime()
        test_task_3_imports()
        test_task_4_settings()
        test_task_5_db_helper()
        test_task_6_models()
        test_task_7_schemas()
        test_task_8_auth()
        
        print("\n🎉 All tests passed! Ready for Task 9.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
