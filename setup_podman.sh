#!/bin/bash

# Script to enable user-level Podman service and socket for ADAS Dashboard
# This script sets up Podman for user-level access only (no root required)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}User Podman Service Setup Script${NC}"
echo "====================================="

# Function to check if running as root (and warn against it)
check_not_root() {
    if [ "$EUID" -eq 0 ]; then
        echo -e "${RED}Error: This script should NOT be run as root!${NC}"
        echo "Please run this script as a regular user for user-level Podman setup."
        echo "User-level Podman is more secure and doesn't require root privileges."
        exit 1
    fi
    echo -e "${GREEN}✓ Running as regular user - setting up user-level Podman service${NC}"
}

# Function to check if Podman is installed
check_podman_installed() {
    if ! command -v podman &> /dev/null; then
        echo -e "${RED}Error: Podman is not installed.${NC}"
        echo "Please install Podman first:"
        echo "  Ubuntu/Debian: sudo apt install podman"
        echo "  Fedora: sudo dnf install podman"
        echo "  CentOS/RHEL: sudo yum install podman"
        exit 1
    fi
    
    PODMAN_VERSION=$(podman --version)
    echo -e "${GREEN}✓ Podman is installed: $PODMAN_VERSION${NC}"
}

# Function to enable user-level Podman service
enable_user_podman() {
    echo -e "${YELLOW}Setting up user-level Podman service...${NC}"
    
    # Enable and start user podman.socket
    if systemctl --user enable podman.socket; then
        echo -e "${GREEN}✓ User Podman socket enabled${NC}"
    else
        echo -e "${RED}✗ Failed to enable user Podman socket${NC}"
        return 1
    fi
    
    if systemctl --user start podman.socket; then
        echo -e "${GREEN}✓ User Podman socket started${NC}"
    else
        echo -e "${RED}✗ Failed to start user Podman socket${NC}"
        return 1
    fi
    
    # Enable and start user podman service
    if systemctl --user enable podman; then
        echo -e "${GREEN}✓ User Podman service enabled${NC}"
    else
        echo -e "${RED}✗ Failed to enable user Podman service${NC}"
        return 1
    fi
    
    if systemctl --user start podman; then
        echo -e "${GREEN}✓ User Podman service started${NC}"
    else
        echo -e "${RED}✗ Failed to start user Podman service${NC}"
        return 1
    fi
}

# Function to verify user socket is working
verify_socket() {
    echo -e "${YELLOW}Verifying user Podman socket...${NC}"
    
    # Wait a moment for socket to be ready
    sleep 2
    
    USER_SOCKET="/run/user/$(id -u)/podman/podman.sock"
    
    if [ -S "$USER_SOCKET" ]; then
        echo -e "${GREEN}✓ User socket found: $USER_SOCKET${NC}"
    else
        echo -e "${RED}✗ User Podman socket not found at $USER_SOCKET${NC}"
        return 1
    fi
    
    # Test socket connectivity
    if podman --url "unix://$USER_SOCKET" version &>/dev/null; then
        echo -e "${GREEN}✓ User socket connectivity verified${NC}"
    else
        echo -e "${RED}✗ User socket connectivity test failed${NC}"
        return 1
    fi
}

# Function to show user service status
show_status() {
    echo -e "${BLUE}User Podman Service Status:${NC}"
    echo "================================"
    
    echo -e "${YELLOW}User services:${NC}"
    systemctl --user status podman.socket --no-pager -l || true
    echo
    systemctl --user status podman --no-pager -l || true
    
    echo -e "${YELLOW}User socket:${NC}"
    USER_SOCKET="/run/user/$(id -u)/podman/podman.sock"
    if [ -S "$USER_SOCKET" ]; then
        echo -e "${GREEN}  $USER_SOCKET${NC}"
    else
        echo -e "${RED}  Socket not found${NC}"
    fi
}

# Main execution
main() {
    check_not_root
    check_podman_installed
    enable_user_podman
    verify_socket
    show_status
    
    echo -e "${GREEN}✓ User Podman setup completed successfully!${NC}"
    echo
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Run your ADAS Dashboard: ./run-container.sh"
    echo "2. For troubleshooting, check: journalctl --user -u podman"
    echo "3. User socket location: /run/user/$(id -u)/podman/podman.sock"
}

# Run main function
main "$@" 