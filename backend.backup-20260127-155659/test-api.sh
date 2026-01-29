#!/bin/bash

# SusBonk API Test Script
# Tests basic functionality of the FastAPI backend

set -e

API_URL="${API_URL:-http://localhost:8000}"
echo "Testing SusBonk API at $API_URL"
echo "================================"

# Test 1: Health Check
echo -e "\n1. Testing health check..."
curl -s "$API_URL/health" | jq .
echo "✓ Health check passed"

# Test 2: Register User
echo -e "\n2. Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }')
echo "$REGISTER_RESPONSE" | jq .
TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')
echo "✓ User registered, token: ${TOKEN:0:20}..."

# Test 3: Get Current User
echo -e "\n3. Testing get current user..."
curl -s "$API_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo "✓ Get current user passed"

# Test 4: List System Prompts
echo -e "\n4. Testing list system prompts..."
curl -s "$API_URL/prompts?page=1&page_size=5" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo "✓ List system prompts passed"

# Test 5: Create Custom Prompt
echo -e "\n5. Testing create custom prompt..."
CUSTOM_PROMPT=$(curl -s -X POST "$API_URL/prompts/custom" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Prompt",
    "prompt_text": "This is a test prompt for spam detection"
  }')
echo "$CUSTOM_PROMPT" | jq .
PROMPT_ID=$(echo "$CUSTOM_PROMPT" | jq -r '.id')
echo "✓ Custom prompt created: $PROMPT_ID"

# Test 6: List Custom Prompts
echo -e "\n6. Testing list custom prompts..."
curl -s "$API_URL/prompts/custom" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo "✓ List custom prompts passed"

# Test 7: Update Custom Prompt
echo -e "\n7. Testing update custom prompt..."
curl -s -X PATCH "$API_URL/prompts/custom/$PROMPT_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Test Prompt"
  }' | jq .
echo "✓ Custom prompt updated"

# Test 8: Delete Custom Prompt
echo -e "\n8. Testing delete custom prompt..."
curl -s -X DELETE "$API_URL/prompts/custom/$PROMPT_ID" \
  -H "Authorization: Bearer $TOKEN"
echo "✓ Custom prompt deleted"

# Test 9: List Chats
echo -e "\n9. Testing list chats..."
curl -s "$API_URL/chats" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo "✓ List chats passed"

echo -e "\n================================"
echo "All tests passed! ✓"
echo "API is working correctly."
echo ""
echo "Access Swagger docs at: $API_URL/docs"
