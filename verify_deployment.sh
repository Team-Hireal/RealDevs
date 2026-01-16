#!/bin/bash

# Deployment Verification Script for RealDevs
# This script helps verify that your Vercel deployment is working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Your deployment URL
DEPLOYMENT_URL="${1:-https://www.realdevs.pro}"

echo "🔍 Verifying RealDevs deployment at: $DEPLOYMENT_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local method=${3:-GET}
    local expected_status=${4:-200}
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" "$url")
    fi
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $response, expected $expected_status)"
        return 1
    fi
}

# Function to test endpoint with JSON response
test_json_endpoint() {
    local name=$1
    local url=$2
    local expected_field=$3
    
    echo -n "Testing $name... "
    
    response=$(curl -s "$url")
    
    if echo "$response" | grep -q "$expected_field"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        echo "   Response: $(echo "$response" | head -c 100)..."
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "   Response: $response"
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Testing Core API Endpoints"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Health Check" "$DEPLOYMENT_URL/api/health"
test_json_endpoint "Auth Status" "$DEPLOYMENT_URL/api/auth/status" "ok"
test_json_endpoint "Team Members" "$DEPLOYMENT_URL/api/team-members" "members"
test_json_endpoint "External Contributors" "$DEPLOYMENT_URL/api/external-contributors" "contributors"
test_json_endpoint "Internal Orgs" "$DEPLOYMENT_URL/api/internal-orgs" "organizations"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Testing Database Connectivity"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test if we can read from database endpoints
auth_status=$(curl -s "$DEPLOYMENT_URL/api/auth/status")
echo "Auth Status Response:"
echo "$auth_status" | python3 -m json.tool 2>/dev/null || echo "$auth_status"
echo ""

if echo "$auth_status" | grep -q '"ok": true'; then
    echo -e "${GREEN}✓ API endpoints are responding${NC}"
    
    if echo "$auth_status" | grep -q '"configured": true'; then
        echo -e "${GREEN}✓ Database is connected and configured${NC}"
    else
        echo -e "${YELLOW}⚠ Database connected but not yet configured${NC}"
        echo "   → Visit $DEPLOYMENT_URL/credentials to configure"
    fi
else
    echo -e "${RED}✗ API endpoints may have issues${NC}"
    echo "   Check Vercel logs for details"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Testing Frontend Pages"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_endpoint "Homepage" "$DEPLOYMENT_URL/"
test_endpoint "Credentials Page" "$DEPLOYMENT_URL/credentials"
test_endpoint "Settings Page" "$DEPLOYMENT_URL/settings"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if auth endpoints are responding properly
if echo "$auth_status" | grep -q '"ok": true'; then
    echo -e "${GREEN}✅ API endpoints are functional!${NC}"
    echo ""
    
    if echo "$auth_status" | grep -q '"configured": true'; then
        echo "Your application is ready to use!"
        echo ""
        echo "Next steps:"
        echo "  1. Visit: $DEPLOYMENT_URL"
        echo "  2. View your dashboard and metrics"
        echo "  3. Manage team members and repositories"
    else
        echo "Database is connected. Ready for initial setup!"
        echo ""
        echo "Next steps:"
        echo "  1. Visit: $DEPLOYMENT_URL/credentials"
        echo "  2. Add your GitHub PAT or username"
        echo "  3. Configure team members"
        echo "  4. Select repositories to track"
    fi
else
    echo -e "${YELLOW}⚠️  API may need database setup${NC}"
    echo ""
    echo "Database setup required:"
    echo "  → See: DATABASE_FIX_SUMMARY.md"
    echo "  → See: VERCEL_DATABASE_SETUP.md"
fi

echo ""
echo "📚 Documentation:"
echo "   - DATABASE_FIX_SUMMARY.md - What was fixed and next steps"
echo "   - VERCEL_DATABASE_SETUP.md - Detailed database setup guide"
echo ""

