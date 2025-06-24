#!/bin/bash

# Fix permissions for container portability
# This script makes mounted files writable by the container user

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Fixing file permissions for container portability...${NC}"

# Make resources directory writable by container user (UID 1000)
if [ -d "resources" ]; then
    echo -e "${YELLOW}Making resources directory writable...${NC}"
    chmod -R 777 resources/
    echo -e "${GREEN}✓ Resources directory permissions fixed${NC}"
fi

# Make any JSON files writable
find . -name "*.json" -exec chmod 666 {} \; 2>/dev/null || true

echo -e "${GREEN}✓ Permissions fixed! Container can now write to mounted files.${NC}"
echo -e "${YELLOW}Note: Run this script if you get permission errors.${NC}" 