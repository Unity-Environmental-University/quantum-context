#!/bin/bash
# Publish quantum-context to PyPI
#
# Usage:
#   1. Get API token from https://pypi.org/manage/account/token/
#   2. Set environment variable:
#      export TWINE_PASSWORD="pypi-YOUR_TOKEN_HERE"
#   3. Run this script:
#      ./publish.sh

set -e  # Exit on error

echo "Publishing quantum-context to PyPI..."
echo ""

# Check if token is set
if [ -z "$TWINE_PASSWORD" ]; then
    echo "ERROR: TWINE_PASSWORD environment variable not set"
    echo ""
    echo "Steps to publish:"
    echo "1. Go to https://pypi.org/manage/account/token/"
    echo "2. Create an API token (scope: entire account or just quantum-context)"
    echo "3. Copy the token"
    echo "4. Run:"
    echo "   export TWINE_PASSWORD='pypi-YOUR_TOKEN_HERE'"
    echo "   ./publish.sh"
    exit 1
fi

# Use __token__ as username with API token
export TWINE_USERNAME="__token__"

# Check package validity
echo "Checking package..."
twine check dist/*

echo ""
echo "Uploading to PyPI..."
twine upload dist/*

echo ""
echo "✓ Published! quantum-context v0.2.0 is now available on PyPI"
echo ""
echo "Users can install with:"
echo "  pip install quantum-context"
