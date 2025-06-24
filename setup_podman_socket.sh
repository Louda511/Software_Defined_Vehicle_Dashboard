#!/bin/bash

# Setup script for Podman system-wide socket (for maximum portability)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Podman System Socket Setup${NC}"
echo "=============================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}Note: This script needs root privileges to set up system-wide Podman socket${NC}"
    echo -e "${YELLOW}You can also run: systemctl --user start podman.socket (for user-only setup)${NC}"
    echo ""
fi

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo -e "${RED}Error: Podman is not installed. Please install Podman first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Podman is installed${NC}"

# Check current socket status
echo -e "\n${BLUE}Checking current Podman socket status...${NC}"

if [ -S "/run/podman/podman.sock" ]; then
    echo -e "${GREEN}✓ System-wide Podman socket is already active${NC}"
    echo -e "   Socket: /run/podman/podman.sock"
elif [ -S "/var/run/podman/podman.sock" ]; then
    echo -e "${GREEN}✓ Alternative system Podman socket is active${NC}"
    echo -e "   Socket: /var/run/podman/podman.sock"
elif [ -S "/run/user/$(id -u)/podman/podman.sock" ]; then
    echo -e "${YELLOW}⚠ User Podman socket is active${NC}"
    echo -e "   Socket: /run/user/$(id -u)/podman/podman.sock"
    echo -e "   ${YELLOW}For maximum portability, consider enabling system-wide socket${NC}"
else
    echo -e "${RED}✗ No Podman socket found${NC}"
fi

# Try to enable system-wide socket if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "\n${BLUE}Setting up system-wide Podman socket...${NC}"
    
    # Enable and start the socket
    if systemctl enable podman.socket 2>/dev/null; then
        echo -e "${GREEN}✓ Podman socket service enabled${NC}"
    else
        echo -e "${YELLOW}⚠ Could not enable podman.socket service${NC}"
    fi
    
    if systemctl start podman.socket 2>/dev/null; then
        echo -e "${GREEN}✓ Podman socket service started${NC}"
    else
        echo -e "${YELLOW}⚠ Could not start podman.socket service${NC}"
    fi
    
    # Check if it's now active
    if [ -S "/run/podman/podman.sock" ]; then
        echo -e "${GREEN}✓ System-wide Podman socket is now active!${NC}"
        echo -e "   Socket: /run/podman/podman.sock"
    else
        echo -e "${YELLOW}⚠ System-wide socket not available, using user socket${NC}"
    fi
else
    echo -e "\n${YELLOW}To enable system-wide Podman socket, run:${NC}"
    echo -e "   sudo systemctl enable podman.socket"
    echo -e "   sudo systemctl start podman.socket"
    echo -e "\n${YELLOW}Or use user socket (already available):${NC}"
    echo -e "   systemctl --user start podman.socket"
fi

echo -e "\n${GREEN}Setup complete! Your container should now work on any machine.${NC}"
echo -e "${BLUE}Run: bash run-container.sh${NC}" 