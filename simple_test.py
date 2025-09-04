#!/usr/bin/env python3
"""
Simple test script for the Emergent Pentest Suite Backend
"""

import requests
import time

def test_backend():
    """Test basic backend functionality"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Backend...")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Health check failed: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Root endpoint passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Root endpoint failed: {e}")
    
    # Test 3: Tools status
    print("\n3. Testing tools status...")
    try:
        response = requests.get(f"{base_url}/api/tools/status", timeout=5)
        if response.status_code == 200:
            print("   ✅ Tools status passed")
            tools = response.json()
            for tool_name, tool_info in tools.items():
                status = tool_info.get('status', 'unknown')
                print(f"      {tool_name}: {status}")
        else:
            print(f"   ❌ Tools status failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Tools status failed: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_backend()
