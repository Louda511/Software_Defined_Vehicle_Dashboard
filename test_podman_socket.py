#!/usr/bin/env python3
"""
Test script to verify Podman socket connection
"""
import os
import sys
from podman import PodmanClient

def test_podman_socket():
    """Test Podman socket connection"""
    
    # Check environment variable
    socket_path = os.environ.get('PODMAN_SOCKET_PATH', '/run/podman/podman.sock')
    print(f"🔍 Using socket path: {socket_path}")
    
    # Check if socket file exists
    if os.path.exists(socket_path):
        print(f"✅ Socket file exists: {socket_path}")
        stat = os.stat(socket_path)
        print(f"   Owner: {stat.st_uid}, Permissions: {oct(stat.st_mode)}")
    else:
        print(f"❌ Socket file NOT found: {socket_path}")
        return False
    
    # Test connection
    try:
        print(f"🔌 Attempting to connect to Podman...")
        client = PodmanClient(base_url=f'unix://{socket_path}')
        
        # Test ping
        response = client.ping()
        print(f"✅ Podman connection successful!")
        print(f"   API Version: {response.get('APIVersion', 'Unknown')}")
        
        # Test basic operations
        info = client.info()
        print(f"   Podman Version: {info.get('version', {}).get('Version', 'Unknown')}")
        print(f"   Containers: {info.get('containers', 0)}")
        print(f"   Images: {info.get('images', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Podman connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Podman Socket Test")
    print("=" * 30)
    
    success = test_podman_socket()
    
    if success:
        print("\n🎉 All tests passed! Podman socket is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed! Check socket mounting and permissions.")
        sys.exit(1) 