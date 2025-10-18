#!/bin/bash
# Simple script to run the API debug tool

echo "🚀 Running ISP Health Monitor API Debug Tool"
echo "============================================="
echo ""

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found"
    python3 debug_api_test.py
elif command -v python &> /dev/null; then
    echo "✅ Python found"
    python debug_api_test.py
else
    echo "❌ Python not found. Please install Python 3"
    exit 1
fi

echo ""
echo "🎯 Debug complete! Check the results above."
echo "📁 Results are also saved to a JSON file for detailed analysis."
