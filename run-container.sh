#!/bin/bash

# Script to run the ADAS Dashboard in a Podman container

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}ADAS Dashboard Container Runner${NC}"
echo "=================================="

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo -e "${RED}Error: Podman is not installed. Please install Podman first.${NC}"
    exit 1
fi

# Check if X11 is available
if [ -z "$DISPLAY" ]; then
    echo -e "${RED}Error: DISPLAY environment variable is not set.${NC}"
    echo "Make sure you're running this in a graphical environment."
    exit 1
fi

# Get current user ID for dynamic socket path detection
CURRENT_UID=$(id -u)
echo -e "${BLUE}Current user ID: $CURRENT_UID${NC}"

# Detect Podman socket path for maximum portability
PODMAN_SOCKET=""
if [ -S "/run/podman/podman.sock" ]; then
    PODMAN_SOCKET="/run/podman/podman.sock"
    CONTAINER_SOCKET="/run/podman/podman.sock"
    echo -e "${GREEN}Using system-wide Podman socket: $PODMAN_SOCKET${NC}"
elif [ -S "/var/run/podman/podman.sock" ]; then
    PODMAN_SOCKET="/var/run/podman/podman.sock"
    CONTAINER_SOCKET="/run/podman/podman.sock"
    echo -e "${GREEN}Using alternative system Podman socket: $PODMAN_SOCKET${NC}"
elif [ -S "/run/user/$CURRENT_UID/podman/podman.sock" ]; then
    PODMAN_SOCKET="/run/user/$CURRENT_UID/podman/podman.sock"
    CONTAINER_SOCKET="/run/user/$CURRENT_UID/podman/podman.sock"
    echo -e "${YELLOW}Using user Podman socket: $PODMAN_SOCKET${NC}"
else
    echo -e "${RED}Error: No Podman socket found. Please ensure Podman service is running.${NC}"
    echo "Available options:"
    echo "  - Start system-wide Podman service: sudo systemctl start podman.socket"
    echo "  - Start user Podman service: systemctl --user start podman.socket"
    echo "  - Run setup script: ./setup_podman.sh"
    exit 1
fi

# Allow X11 connections from localhost
echo -e "${YELLOW}Setting up X11 permissions...${NC}"
xhost +local:docker 2>/dev/null || xhost +local: 2>/dev/null

# Build the container image (only if not exists or code changed)
echo -e "${YELLOW}Building container image...${NC}"
podman build -t adas-dashboard .

# Run the container with UID mapping for secure socket and file access
# Mount only code files, not resources (JSON files will be container-local)
echo -e "${YELLOW}Starting ADAS Dashboard...${NC}"
podman run --rm \
    --name adas-dashboard \
    --userns=keep-id \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --env PODMAN_SOCKET_PATH=$CONTAINER_SOCKET \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume ./main.py:/app/main.py:ro \
    --volume ./models:/app/models:ro \
    --volume ./services:/app/services:ro \
    --volume ./ui:/app/ui:ro \
    --volume ./utils:/app/utils:ro \
    --volume ./requirements.txt:/app/requirements.txt:ro \
    --volume "$PODMAN_SOCKET:$CONTAINER_SOCKET:rw" \
    --network host \
    --interactive \
    --tty \
    adas-dashboard

echo -e "${GREEN}Container stopped.${NC}" 

echo $PODMAN_SOCKET_PATH 