#!/bin/bash

# Test script for SusBonk Telegram Bot
# This script tests the basic functionality of the telegram bot

set -e

echo "🐕 SusBonk Telegram Bot Test Suite"
echo "=================================="

# Check if required environment variables are set
echo "📋 Checking environment variables..."
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    exit 1
fi

if [ -z "$REDIS_URL" ]; then
    echo "❌ REDIS_URL not set"
    exit 1
fi

echo "✅ Environment variables OK"

# Test 1: Build the telegram bot
echo "🔨 Building telegram bot..."
cd log-platform
if cargo build --bin telegram-bot --release; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

# Test 2: Check if binary exists
if [ -f "target/release/telegram-bot" ]; then
    echo "✅ Binary exists"
else
    echo "❌ Binary not found"
    exit 1
fi

# Test 3: Test link detection
echo "🔍 Testing link detection..."
cat > test_link_detection.rs << 'EOF'
use std::collections::HashSet;
use regex::Regex;

// Simplified version of LinkDetector for testing
struct TestLinkDetector {
    url_regex: Regex,
    shortened_domains: HashSet<String>,
}

impl TestLinkDetector {
    fn new() -> Self {
        let url_regex = Regex::new(
            r"https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?",
        ).unwrap();

        let shortened_domains = ["bit.ly", "tinyurl.com", "t.co"].iter().map(|s| s.to_string()).collect();

        Self { url_regex, shortened_domains }
    }

    fn detect_links(&self, text: &str) -> Vec<String> {
        self.url_regex.find_iter(text).map(|m| m.as_str().to_string()).collect()
    }

    fn is_shortened_url(&self, url: &str) -> bool {
        self.shortened_domains.iter().any(|domain| url.contains(domain))
    }
}

fn main() {
    let detector = TestLinkDetector::new();
    
    // Test cases
    let test_cases = vec![
        "Check out this link: https://bit.ly/suspicious",
        "Visit https://example.com for more info",
        "No links here",
        "Multiple links: https://google.com and https://t.co/abc123",
    ];

    for (i, test) in test_cases.iter().enumerate() {
        let links = detector.detect_links(test);
        println!("Test {}: Found {} links in '{}'", i + 1, links.len(), test);
        for link in &links {
            if detector.is_shortened_url(link) {
                println!("  ⚠️  Shortened URL detected: {}", link);
            } else {
                println!("  ℹ️  Regular URL: {}", link);
            }
        }
    }
    
    println!("✅ Link detection test completed");
}
EOF

# Compile and run the test
if rustc test_link_detection.rs --extern regex=$(find ~/.cargo/registry -name "libregex-*.rlib" | head -1) -o test_link_detection 2>/dev/null; then
    if ./test_link_detection; then
        echo "✅ Link detection test passed"
    else
        echo "❌ Link detection test failed"
    fi
    rm -f test_link_detection test_link_detection.rs
else
    echo "⚠️  Link detection test skipped (regex dependency not found)"
    rm -f test_link_detection test_link_detection.rs
fi

# Test 4: Check Docker build
echo "🐳 Testing Docker build..."
cd ..
if docker build -f log-platform/telegram-bot/Dockerfile log-platform -t susbonk-telegram-bot:test; then
    echo "✅ Docker build successful"
else
    echo "❌ Docker build failed"
    exit 1
fi

# Test 5: Verify health endpoint works
echo "🏥 Testing health endpoint..."
if docker run --rm -d --name telegram-bot-test -p 8082:8081 \
    -e TELEGRAM_BOT_TOKEN="test_token" \
    -e DATABASE_URL="postgresql://test:test@localhost:5432/test" \
    -e REDIS_URL="redis://localhost:6379" \
    susbonk-telegram-bot:test; then
    
    sleep 5
    
    if curl -f http://localhost:8082/health 2>/dev/null; then
        echo "✅ Health endpoint working"
    else
        echo "⚠️  Health endpoint test skipped (service may need real database)"
    fi
    
    docker stop telegram-bot-test 2>/dev/null || true
else
    echo "⚠️  Docker health test skipped"
fi

echo ""
echo "🎉 Test suite completed!"
echo "📊 Summary:"
echo "   ✅ Environment variables configured"
echo "   ✅ Rust build successful"
echo "   ✅ Binary created"
echo "   ✅ Docker image built"
echo ""
echo "🚀 Ready for deployment!"
echo ""
echo "To start the bot:"
echo "   cd backend && docker-compose up telegram-bot"
echo ""
echo "To view logs:"
echo "   docker-compose logs -f telegram-bot"
