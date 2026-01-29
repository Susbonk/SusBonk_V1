#!/bin/bash
# Security Verification Script
# Checks that all critical security fixes are in place

set -e

echo "🔒 SusBonk Security Verification"
echo "================================"
echo ""

ERRORS=0
WARNINGS=0

# Check 1: .env file exists and has correct permissions
echo "✓ Checking .env file..."
if [ ! -f .env ]; then
    echo "  ❌ ERROR: .env file not found"
    echo "     Run: cp .env.example .env"
    ERRORS=$((ERRORS + 1))
else
    PERMS=$(stat -f "%OLp" .env 2>/dev/null || stat -c "%a" .env 2>/dev/null)
    if [ "$PERMS" != "600" ]; then
        echo "  ⚠️  WARNING: .env permissions are $PERMS (should be 600)"
        echo "     Run: chmod 600 .env"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check 2: No default passwords in .env
echo "✓ Checking for default passwords..."
if [ -f .env ]; then
    if grep -q "CHANGE_ME" .env; then
        echo "  ❌ ERROR: Default passwords found in .env"
        echo "     Replace all CHANGE_ME_* values with generated secrets"
        ERRORS=$((ERRORS + 1))
    fi
    
    if grep -q "susbonk_dev\|Admin123!\|admin" .env; then
        echo "  ⚠️  WARNING: Weak default passwords detected"
        echo "     Generate strong passwords with: openssl rand -base64 32"
        WARNINGS=$((WARNINGS + 1))
    fi
fi

# Check 3: Django settings - no hardcoded secret
echo "✓ Checking Django settings..."
if grep -q "^SECRET_KEY = 'django-insecure-" admin/db_admin/settings.py; then
    echo "  ❌ ERROR: Hardcoded Django secret key found"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ Django secret key is from environment"
fi

# Check 4: Django DEBUG mode
if grep -q "^DEBUG = True" admin/db_admin/settings.py; then
    echo "  ❌ ERROR: DEBUG = True found in settings.py"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ DEBUG mode is environment-controlled"
fi

# Check 5: Django ALLOWED_HOSTS
if grep -q "ALLOWED_HOSTS = \['\*'\]" admin/db_admin/settings.py; then
    echo "  ❌ ERROR: ALLOWED_HOSTS = ['*'] found"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ ALLOWED_HOSTS is environment-controlled"
fi

# Check 6: Redis authentication in docker-compose
echo "✓ Checking Redis configuration..."
if grep -q "requirepass" docker-compose.yml; then
    echo "  ✅ Redis authentication enabled"
else
    echo "  ❌ ERROR: Redis authentication not configured"
    ERRORS=$((ERRORS + 1))
fi

# Check 7: Backend reload flag
echo "✓ Checking backend configuration..."
if grep -q "reload=True" backend/main.py; then
    echo "  ❌ ERROR: reload=True found in backend/main.py"
    ERRORS=$((ERRORS + 1))
else
    echo "  ✅ Reload flag is environment-controlled"
fi

# Check 8: .env not in git
echo "✓ Checking git configuration..."
if git check-ignore .env >/dev/null 2>&1; then
    echo "  ✅ .env is in .gitignore"
else
    echo "  ⚠️  WARNING: .env is not in .gitignore"
    echo "     Run: echo '.env' >> .gitignore"
    WARNINGS=$((WARNINGS + 1))
fi

if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    echo "  ❌ ERROR: .env is tracked by git"
    echo "     Run: git rm --cached .env"
    ERRORS=$((ERRORS + 1))
fi

# Check 9: ENVIRONMENT variable
echo "✓ Checking environment configuration..."
if [ -f .env ]; then
    ENV_VAR=$(grep "^ENVIRONMENT=" .env | cut -d= -f2)
    if [ "$ENV_VAR" = "production" ]; then
        echo "  ⚠️  WARNING: ENVIRONMENT=production in .env"
        echo "     Make sure all secrets are production-ready"
        WARNINGS=$((WARNINGS + 1))
    else
        echo "  ✅ ENVIRONMENT=$ENV_VAR"
    fi
fi

# Summary
echo ""
echo "================================"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "✅ All security checks passed!"
    echo ""
    echo "Next steps:"
    echo "1. Review docs/SECURITY_SETUP.md"
    echo "2. Generate production secrets"
    echo "3. Test deployment: docker-compose up -d"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "⚠️  $WARNINGS warning(s) found"
    echo ""
    echo "Review warnings above before production deployment"
    exit 0
else
    echo "❌ $ERRORS error(s) and $WARNINGS warning(s) found"
    echo ""
    echo "Fix all errors before deployment!"
    echo "See docs/code-review-action-plan.md for fixes"
    exit 1
fi
