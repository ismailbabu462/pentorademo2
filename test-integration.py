#!/usr/bin/env python3
"""
Integration Test Script for Pentest Suite
Tests backend-frontend integration and API endpoints
"""

import asyncio
import aiohttp
import json
import time
import sys
import os
from typing import Dict, Any, List

class IntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.session = None
        self.test_results = []
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            'test': test_name,
            'success': success,
            'message': message
        })
    
    async def test_health_endpoint(self):
        """Test health endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Health Endpoint", True, f"Status: {data.get('status')}")
                    return True
                else:
                    self.log_test("Health Endpoint", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Health Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            async with self.session.get(f"{self.base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Root Endpoint", True, f"Message: {data.get('message')}")
                    return True
                else:
                    self.log_test("Root Endpoint", False, f"Status: {response.status}")
                    return False
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_cors_headers(self):
        """Test CORS headers"""
        try:
            headers = {
                'Origin': 'https://pentorasecbeta.mywire.org',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            async with self.session.options(f"{self.api_url}/auth/auto-connect", headers=headers) as response:
                cors_headers = {
                    'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                    'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                    'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
                }
                
                if cors_headers['Access-Control-Allow-Origin']:
                    self.log_test("CORS Headers", True, f"Origin: {cors_headers['Access-Control-Allow-Origin']}")
                    return True
                else:
                    self.log_test("CORS Headers", False, "No CORS headers found")
                    return False
        except Exception as e:
            self.log_test("CORS Headers", False, f"Error: {str(e)}")
            return False
    
    async def test_auto_connect_endpoint(self):
        """Test auto-connect endpoint"""
        try:
            device_data = {
                "device_fingerprint": "test-fingerprint-123",
                "device_name": "Test Device",
                "device_type": "web"
            }
            
            async with self.session.post(
                f"{self.api_url}/auth/auto-connect",
                json=device_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'access_token' in data and 'user' in data:
                        self.log_test("Auto-Connect Endpoint", True, f"Token received, User: {data['user']['username']}")
                        return data['access_token']
                    else:
                        self.log_test("Auto-Connect Endpoint", False, "Invalid response format")
                        return None
                else:
                    error_text = await response.text()
                    self.log_test("Auto-Connect Endpoint", False, f"Status: {response.status}, Error: {error_text}")
                    return None
        except Exception as e:
            self.log_test("Auto-Connect Endpoint", False, f"Error: {str(e)}")
            return None
    
    async def test_authenticated_endpoint(self, token: str):
        """Test authenticated endpoint"""
        if not token:
            self.log_test("Authenticated Endpoint", False, "No token provided")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            
            async with self.session.get(f"{self.api_url}/auth/me", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Authenticated Endpoint", True, f"User: {data.get('username')}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Authenticated Endpoint", False, f"Status: {response.status}, Error: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Authenticated Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_projects_endpoint(self, token: str):
        """Test projects endpoint"""
        if not token:
            self.log_test("Projects Endpoint", False, "No token provided")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            
            async with self.session.get(f"{self.api_url}/projects", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Projects Endpoint", True, f"Projects count: {len(data)}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Projects Endpoint", False, f"Status: {response.status}, Error: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Projects Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_tools_endpoint(self, token: str):
        """Test tools endpoint"""
        if not token:
            self.log_test("Tools Endpoint", False, "No token provided")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            
            async with self.session.get(f"{self.api_url}/tools", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("Tools Endpoint", True, f"Tools available: {len(data)}")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("Tools Endpoint", False, f"Status: {response.status}, Error: {error_text}")
                    return False
        except Exception as e:
            self.log_test("Tools Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def test_ai_endpoint(self, token: str):
        """Test AI endpoint"""
        if not token:
            self.log_test("AI Endpoint", False, "No token provided")
            return False
        
        try:
            headers = {'Authorization': f'Bearer {token}'}
            ai_data = {
                "message": "Hello, this is a test message",
                "context": "test"
            }
            
            async with self.session.post(
                f"{self.api_url}/ai/chat",
                json=ai_data,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_test("AI Endpoint", True, f"Response received: {len(data.get('response', ''))} chars")
                    return True
                else:
                    error_text = await response.text()
                    self.log_test("AI Endpoint", False, f"Status: {response.status}, Error: {error_text}")
                    return False
        except Exception as e:
            self.log_test("AI Endpoint", False, f"Error: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🧪 Starting Integration Tests")
        print("=" * 50)
        
        # Test basic endpoints
        await self.test_health_endpoint()
        await self.test_root_endpoint()
        await self.test_cors_headers()
        
        # Test authentication
        token = await self.test_auto_connect_endpoint()
        
        # Test authenticated endpoints
        if token:
            await self.test_authenticated_endpoint(token)
            await self.test_projects_endpoint(token)
            await self.test_tools_endpoint(token)
            await self.test_ai_endpoint(token)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results if result['success'])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n🎉 All tests passed! Integration is working correctly.")
            return True
        else:
            print(f"\n⚠️ {total - passed} tests failed. Please check the issues above.")
            return False

async def main():
    """Main test function"""
    # Check if backend is running
    base_url = os.getenv('BACKEND_URL', 'http://localhost:8001')
    
    print(f"🔗 Testing backend at: {base_url}")
    print("Make sure the backend is running before starting tests.")
    print()
    
    async with IntegrationTester(base_url) as tester:
        success = await tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
