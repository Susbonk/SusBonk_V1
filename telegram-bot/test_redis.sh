#!/bin/bash

# Simple test script to verify Redis functionality
echo "Testing Redis deleted messages functionality..."

# Start Redis if not running (optional)
# redis-server --daemonize yes

# Set environment variable
export REDIS_URL="redis://localhost:6379"

# Test storing and retrieving a deleted message
echo "Building the project..."
cargo build --bin get_deleted_messages

echo "Testing with a sample chat ID..."
cargo run --bin get_deleted_messages test_chat_123

echo "Test completed!"
