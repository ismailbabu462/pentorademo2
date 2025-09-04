#!/usr/bin/env python3
"""
Test script for the Emergent Pentest Suite Backend
Tests all security tool endpoints
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:8001"
API_BASE = f"{BASE_URL}/api"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_tools_status():
    """Test the tools status endpoint"""
    print("\n🔍 Testing tools status...")
    try:
        response = requests.get(f"{API_BASE}/tools/status", timeout=10)
        if response.status_code == 200:
            print("✅ Tools status endpoint working")
            tools = response.json()
            for tool_name, tool_info in tools.items():
                status = tool_info.get('status', 'unknown')
                print(f"   {tool_name}: {status}")
            return True
        else:
            print(f"❌ Tools status failed with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Tools status failed: {e}")
        return False

def test_tool_endpoint(tool_name, target="example.com"):
    """Test a specific tool endpoint"""
    print(f"\n🔍 Testing {tool_name}...")
    try:
        payload = {"target": target}
        response = requests.post(f"{API_BASE}/tools/{tool_name}", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {tool_name} scan completed successfully")
                print(f"   Results: {result.get('results', {})}")
                return True
            else:
                print(f"❌ {tool_name} scan failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ {tool_name} failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {tool_name} request failed: {e}")
        return False

def test_all_tools():
    """Test all security tools"""
    print("\n🚀 Testing all security tools...")
    
    tools = [
        "subfinder",
        "amass", 
        "nmap",
        "nuclei",
        "ffuf",
        "gobuster"
    ]
    
    results = {}
    for tool in tools:
        results[tool] = test_tool_endpoint(tool)
        time.sleep(1)  # Small delay between tests
    
    return results

def main():
    """Main test function"""
    print("🧪 Emergent Pentest Suite Backend Test")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("\n❌ Backend is not accessible. Please make sure it's running.")
        return
    
    # Test tools status
    test_tools_status()
    
    # Test all tools
    results = test_all_tools()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for tool, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{tool:12}: {status}")
    
    print(f"\nOverall: {passed}/{total} tools working")
    
    if passed == total:
        print("🎉 All tools are working correctly!")
    elif passed > 0:
        print("⚠️  Some tools are working, some are not")
    else:
        print("❌ No tools are working")

if __name__ == "__main__":
    main()