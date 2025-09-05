#!/usr/bin/env python3
"""
Backend Startup Test Script
Tests if backend can start without JWT_SECRET_KEY errors
"""

import os
import sys
import subprocess
import time

def test_backend_startup():
    """Test backend startup"""
    print("🧪 Testing Backend Startup...")
    
    # Set environment variables
    os.environ['ENVIRONMENT'] = 'development'
    os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
    
    # Test config import
    try:
        print("📋 Testing config import...")
        sys.path.insert(0, 'backend')
        from config import JWT_SECRET_KEY, ENVIRONMENT
        print(f"✅ Config imported successfully")
        print(f"   JWT_SECRET_KEY: {JWT_SECRET_KEY[:10]}...")
        print(f"   ENVIRONMENT: {ENVIRONMENT}")
        return True
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False

def test_production_config():
    """Test production config"""
    print("\n🏭 Testing Production Config...")
    
    # Set production environment
    os.environ['ENVIRONMENT'] = 'production'
    os.environ['JWT_SECRET_KEY'] = 'test-production-secret-key'
    
    try:
        # Reload config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import JWT_SECRET_KEY, ENVIRONMENT
        print(f"✅ Production config loaded")
        print(f"   JWT_SECRET_KEY: {JWT_SECRET_KEY[:10]}...")
        print(f"   ENVIRONMENT: {ENVIRONMENT}")
        return True
    except Exception as e:
        print(f"❌ Production config failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Backend Startup Test")
    print("=" * 40)
    
    # Test development config
    dev_success = test_backend_startup()
    
    # Test production config
    prod_success = test_production_config()
    
    print("\n" + "=" * 40)
    print("📊 Test Results")
    print("=" * 40)
    print(f"Development Config: {'✅ PASS' if dev_success else '❌ FAIL'}")
    print(f"Production Config: {'✅ PASS' if prod_success else '❌ FAIL'}")
    
    if dev_success and prod_success:
        print("\n🎉 All tests passed! Backend should start successfully.")
        return True
    else:
        print("\n⚠️ Some tests failed. Check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
