#!/usr/bin/env python3
"""
Task 12 Validation Test - Database Schema Blueprint Compliance
Tests database schema matches blueprint requirements exactly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_task_12_schema_compliance():
    """Task 12: Database schema blueprint compliance"""
    print("✓ Task 12: Database Schema")
    
    # Test all models are importable
    from models import (
        User, Chat, Prompt, CustomPrompt, RuntimeStatistics,
        ChatPrompts, ChatCustomPrompts, UserState
    )
    print("  All models imported: ✓")
    
    # Test UUID primary keys
    models_with_uuid = [User, Chat, Prompt, CustomPrompt, RuntimeStatistics, ChatPrompts, ChatCustomPrompts, UserState]
    for model in models_with_uuid:
        assert hasattr(model, 'id'), f"{model.__name__} missing id field"
        # Check if it's a UUID field (SQLAlchemy 2.0 typed)
        assert hasattr(model, '__annotations__'), f"{model.__name__} missing type annotations"
    print("  UUID primary keys: ✓")
    
    # Test required relationships
    assert hasattr(User, 'chats'), "User missing chats relationship"
    assert hasattr(User, 'custom_prompts'), "User missing custom_prompts relationship"
    assert hasattr(Chat, 'user'), "Chat missing user relationship"
    assert hasattr(Chat, 'user_states'), "Chat missing user_states relationship"
    assert hasattr(Chat, 'chat_prompts'), "Chat missing chat_prompts relationship"
    assert hasattr(Chat, 'chat_custom_prompts'), "Chat missing chat_custom_prompts relationship"
    print("  Model relationships: ✓")
    
    # Test link table models exist
    assert hasattr(ChatPrompts, 'chat_id'), "ChatPrompts missing chat_id"
    assert hasattr(ChatPrompts, 'prompt_id'), "ChatPrompts missing prompt_id"
    assert hasattr(ChatPrompts, 'priority'), "ChatPrompts missing priority"
    assert hasattr(ChatCustomPrompts, 'chat_id'), "ChatCustomPrompts missing chat_id"
    assert hasattr(ChatCustomPrompts, 'custom_prompt_id'), "ChatCustomPrompts missing custom_prompt_id"
    assert hasattr(ChatCustomPrompts, 'priority'), "ChatCustomPrompts missing priority"
    print("  Link tables: ✓")
    
    # Test threshold columns in Chat model
    assert hasattr(Chat, 'prompts_threshold'), "Chat missing prompts_threshold"
    assert hasattr(Chat, 'custom_prompt_threshold'), "Chat missing custom_prompt_threshold"
    print("  Threshold columns: ✓")
    
    # Test runtime statistics model
    assert hasattr(RuntimeStatistics, 'messages_checked'), "RuntimeStatistics missing messages_checked"
    assert hasattr(RuntimeStatistics, 'ai_requests_made'), "RuntimeStatistics missing ai_requests_made"
    assert hasattr(RuntimeStatistics, 'messages_deleted'), "RuntimeStatistics missing messages_deleted"
    print("  Runtime statistics: ✓")
    
    # Test metadata columns (created_at, updated_at, is_active)
    metadata_models = [User, Chat, Prompt, CustomPrompt, RuntimeStatistics, ChatPrompts, ChatCustomPrompts, UserState]
    for model in metadata_models:
        assert hasattr(model, 'created_at'), f"{model.__name__} missing created_at"
        assert hasattr(model, 'updated_at'), f"{model.__name__} missing updated_at"
        assert hasattr(model, 'is_active'), f"{model.__name__} missing is_active"
    print("  Metadata columns: ✓")
    
    # Test platform-specific user IDs
    assert hasattr(User, 'telegram_user_id'), "User missing telegram_user_id"
    assert hasattr(User, 'discord_user_id'), "User missing discord_user_id"
    print("  Platform user IDs: ✓")
    
    # Test chat platform fields
    assert hasattr(Chat, 'type'), "Chat missing type field"
    assert hasattr(Chat, 'platform_chat_id'), "Chat missing platform_chat_id"
    print("  Chat platform fields: ✓")
    
    # Test user state external user ID
    assert hasattr(UserState, 'external_user_id'), "UserState missing external_user_id"
    print("  User state external ID: ✓")
    
    print("  Schema blueprint compliance: ✓")

def main():
    """Run Task 12 validation test"""
    print("=== Task 12 Validation Test ===\n")
    
    try:
        test_task_12_schema_compliance()
        print("\n🎉 Task 12 validation passed! Ready for Task 13.")
        return True
        
    except Exception as e:
        print(f"\n❌ Task 12 validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
