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

# Allow X11 connections from localhost
echo -e "${YELLOW}Setting up X11 permissions...${NC}"
xhost +local:docker 2>/dev/null || xhost +local: 2>/dev/null

# Build the container image
echo -e "${YELLOW}Building container image...${NC}"
podman build -t adas-dashboard .

# Run the container
echo -e "${YELLOW}Starting ADAS Dashboard...${NC}"
podman run --rm \
    --name adas-dashboard \
    --env DISPLAY=$DISPLAY \
    --env QT_X11_NO_MITSHM=1 \
    --env PODMAN_SOCKET_PATH=/run/podman/podman.sock \
    --volume /tmp/.X11-unix:/tmp/.X11-unix:rw \
    --volume /run/user/1000/podman/podman.sock:/run/podman/podman.sock:rw \
    --network host \
    --interactive \
    --tty \
    adas-dashboard

echo -e "${GREEN}Container stopped.${NC}" 

echo $PODMAN_SOCKET_PATH 