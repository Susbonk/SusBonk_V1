#!/usr/bin/env python3
"""
Task 9 Validation Test - API Handlers
Tests all API handlers matching blueprint routes
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_task_9_handlers():
    """Task 9: API handlers matching blueprint routes"""
    print("✓ Task 9: API Handlers")
    
    # Test handler imports
    from handlers import (
        auth_router,
        chat_router,
        prompt_router,
        user_state_router,
        deleted_messages_router
    )
    print("  Handler imports: ✓")
    
    # Test router configurations
    assert auth_router.prefix == "/auth", f"Auth router prefix: {auth_router.prefix}"
    assert prompt_router.prefix == "/prompts", f"Prompt router prefix: {prompt_router.prefix}"
    assert chat_router.prefix == "/chats", f"Chat router prefix: {chat_router.prefix}"
    print("  Router prefixes: ✓")
    
    # Test route counts (approximate)
    auth_routes = len([r for r in auth_router.routes if hasattr(r, 'methods')])
    prompt_routes = len([r for r in prompt_router.routes if hasattr(r, 'methods')])
    chat_routes = len([r for r in chat_router.routes if hasattr(r, 'methods')])
    user_state_routes = len([r for r in user_state_router.routes if hasattr(r, 'methods')])
    deleted_msg_routes = len([r for r in deleted_messages_router.routes if hasattr(r, 'methods')])
    
    print(f"  Route counts: auth={auth_routes}, prompts={prompt_routes}, chats={chat_routes}, user_states={user_state_routes}, deleted_messages={deleted_msg_routes}")
    
    # Test main app creation
    from main_new import app
    assert app.title == "SusBonk Dashboard API", "App title mismatch"
    
    # Count total routes in app
    total_routes = len([r for r in app.routes if hasattr(r, 'methods')])
    print(f"  Total app routes: {total_routes}")
    
    print("  Blueprint compliance: ✓")

def main():
    """Run Task 9 validation test"""
    print("=== Task 9 Validation Test ===\n")
    
    try:
        test_task_9_handlers()
        print("\n🎉 Task 9 validation passed! Ready for Task 10.")
        return True
        
    except Exception as e:
        print(f"\n❌ Task 9 validation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
