#!/bin/bash
# Curl commands to test all three IP information API endpoints
# This allows direct testing of APIs without the integration

echo "🚀 ISP Health Monitor API Curl Test Tool"
echo "=========================================="
echo "⏰ Started at: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 Testing ip-api.com (Free - No API key required)${NC}"
echo "Command: curl -s 'http://ip-api.com/json'"
echo "Response:"
curl -s 'http://ip-api.com/json' | jq '.' 2>/dev/null || curl -s 'http://ip-api.com/json'
echo ""
echo "----------------------------------------"
echo ""

echo -e "${BLUE}🔍 Testing ipinfo.io (Free - No API key required)${NC}"
echo "Command: curl -s 'https://ipinfo.io/json'"
echo "Response:"
curl -s 'https://ipinfo.io/json' | jq '.' 2>/dev/null || curl -s 'https://ipinfo.io/json'
echo ""
echo "----------------------------------------"
echo ""

echo -e "${BLUE}💎 Testing ipgeolocation.io (Premium - API key required)${NC}"
echo "Command: curl -s 'https://api.ipgeolocation.io/ipgeo?apiKey=YOUR_API_KEY'"
echo "Note: Replace YOUR_API_KEY with your actual API key"
echo "Response: (Skipped - No API key provided)"
echo ""
echo "----------------------------------------"
echo ""

echo -e "${GREEN}🎯 Key Fields to Check:${NC}"
echo "- hostname: Should show your ISP's hostname (e.g., syn-xxx-xxx-xxx-xxx.res.spectrum.com)"
echo "- ip: Your public IP address"
echo "- city: Your city"
echo "- region: Your state/province"
echo "- country: Your country"
echo "- org: Your ISP organization"
echo ""

echo -e "${YELLOW}📊 Expected Results:${NC}"
echo "- ip-api.com: May show null hostname (normal for this provider)"
echo "- ipinfo.io: Should show hostname (e.g., syn-xxx-xxx-xxx-xxx.res.spectrum.com)"
echo "- ipgeolocation.io: Requires API key"
echo ""

echo -e "${GREEN}✅ Test complete!${NC}"
echo "Compare the hostname values with what you see in Home Assistant."
