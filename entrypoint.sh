#!/bin/bash
set -e

# If PODMAN_SOCKET_PATH is not set, try to detect it based on mounted sockets
if [ -z "$PODMAN_SOCKET_PATH" ]; then
    if [ -S "/run/user/$(id -u)/podman/podman.sock" ]; then
        export PODMAN_SOCKET_PATH="/run/user/$(id -u)/podman/podman.sock"
    elif [ -S "/run/podman/podman.sock" ]; then
        export PODMAN_SOCKET_PATH="/run/podman/podman.sock"
    elif [ -S "/var/run/podman/podman.sock" ]; then
        export PODMAN_SOCKET_PATH="/var/run/podman/podman.sock"
    fi
fi

# Print for debugging
>&2 echo "Using PODMAN_SOCKET_PATH: $PODMAN_SOCKET_PATH"

# Exec the main command as the current user
exec "$@" 