#!/usr/bin/env python3
"""
Test script to verify user ID detection and Podman socket path resolution.
This helps debug issues with different user IDs on different machines.
"""

import os
import sys

def test_user_detection():
    """Test and display current user information and Podman socket detection."""
    print("=== User ID Detection Test ===")
    print(f"Current user ID: {os.getuid()}")
    print(f"Current username: {os.getenv('USER', 'Unknown')}")
    print(f"Current home directory: {os.path.expanduser('~')}")
    
    print("\n=== Podman Socket Detection ===")
    
    # Test environment variable
    env_path = os.environ.get('PODMAN_SOCKET_PATH')
    if env_path:
        print(f"PODMAN_SOCKET_PATH environment variable: {env_path}")
        print(f"  Exists: {os.path.exists(env_path)}")
    else:
        print("PODMAN_SOCKET_PATH environment variable: Not set")
    
    # Test user-specific socket
    current_uid = os.getuid()
    user_sock = f'/run/user/{current_uid}/podman/podman.sock'
    print(f"\nUser-specific socket: {user_sock}")
    print(f"  Exists: {os.path.exists(user_sock)}")
    
    # Test system-wide sockets
    system_sockets = [
        '/run/podman/podman.sock',
        '/var/run/podman/podman.sock'
    ]
    
    print("\nSystem-wide sockets:")
    for sock in system_sockets:
        exists = os.path.exists(sock)
        print(f"  {sock}: {'✓' if exists else '✗'}")
    
    # Test the actual detection function
    print("\n=== Testing Podman Service Detection ===")
    try:
        from services.podman_service import get_podman_socket_path
        socket_path = get_podman_socket_path()
        if socket_path:
            print(f"Detected socket path: {socket_path}")
            print("✓ Podman service detection working correctly")
        else:
            print("✗ No Podman socket detected")
            print("\nTroubleshooting steps:")
            print("1. For user-level Podman: systemctl --user start podman.socket")
            print("2. For system-wide Podman: sudo systemctl start podman.socket")
            print("3. Run setup script: ./setup_podman.sh")
    except ImportError as e:
        print(f"✗ Could not import podman_service: {e}")
    except Exception as e:
        print(f"✗ Error testing Podman service: {e}")

if __name__ == "__main__":
    test_user_detection() 