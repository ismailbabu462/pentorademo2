#!/usr/bin/env python3
"""
Production Verification Script
Verifies that the application is ready for production deployment
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class ProductionVerifier:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.results = []
    
    def log_check(self, check_name: str, success: bool, message: str = ""):
        """Log verification result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {check_name}: {message}")
        self.results.append({
            'check': check_name,
            'success': success,
            'message': message
        })
    
    def check_file_exists(self, file_path: str, description: str) -> bool:
        """Check if a file exists"""
        full_path = self.project_root / file_path
        exists = full_path.exists()
        self.log_check(f"File: {description}", exists, f"{file_path}")
        return exists
    
    def check_docker_files(self) -> bool:
        """Check Docker configuration files"""
        print("\n🐳 Checking Docker Configuration...")
        
        docker_files = [
            ("docker-compose.yml", "Development Docker Compose"),
            ("docker-compose.prod.yml", "Production Docker Compose"),
            ("backend/Dockerfile", "Backend Dockerfile"),
            ("frontend/Dockerfile", "Frontend Dockerfile"),
            ("nginx/conf.d/default.conf", "Nginx Configuration"),
        ]
        
        all_exist = True
        for file_path, description in docker_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        return all_exist
    
    def check_environment_files(self) -> bool:
        """Check environment configuration files"""
        print("\n🔧 Checking Environment Configuration...")
        
        env_files = [
            ("production.env", "Production Environment"),
            ("generate-secrets.sh", "Secret Generation Script"),
        ]
        
        all_exist = True
        for file_path, description in env_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        # Check if production.env has secure values
        prod_env_path = self.project_root / "production.env"
        if prod_env_path.exists():
            with open(prod_env_path, 'r') as f:
                content = f.read()
                if "change_me" in content:
                    self.log_check("Production Environment Security", False, "Contains 'change_me' placeholders")
                    all_exist = False
                else:
                    self.log_check("Production Environment Security", True, "No placeholder values found")
        
        return all_exist
    
    def check_ssl_configuration(self) -> bool:
        """Check SSL configuration"""
        print("\n🔒 Checking SSL Configuration...")
        
        ssl_files = [
            ("init-letsencrypt.sh", "Let's Encrypt Script"),
            ("nginx/ssl-setup.sh", "SSL Setup Script"),
            ("renew-certs.sh", "Certificate Renewal Script"),
        ]
        
        all_exist = True
        for file_path, description in ssl_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        # Check Nginx SSL configuration
        nginx_conf_path = self.project_root / "nginx/conf.d/default.conf"
        if nginx_conf_path.exists():
            with open(nginx_conf_path, 'r') as f:
                content = f.read()
                if "ssl_certificate" in content and "letsencrypt" in content:
                    self.log_check("Nginx SSL Configuration", True, "Let's Encrypt configured")
                else:
                    self.log_check("Nginx SSL Configuration", False, "SSL not properly configured")
                    all_exist = False
        
        return all_exist
    
    def check_deployment_scripts(self) -> bool:
        """Check deployment scripts"""
        print("\n🚀 Checking Deployment Scripts...")
        
        deploy_files = [
            ("deploy-production.sh", "Production Deploy Script"),
            ("deploy.sh", "Deploy Script"),
            ("test-deployment.sh", "Deployment Test Script"),
            ("test-integration.py", "Integration Test Script"),
        ]
        
        all_exist = True
        for file_path, description in deploy_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        return all_exist
    
    def check_backend_code(self) -> bool:
        """Check backend code quality"""
        print("\n🐍 Checking Backend Code...")
        
        # Check if backend has required files
        backend_files = [
            ("backend/server.py", "Main Server File"),
            ("backend/config.py", "Configuration File"),
            ("backend/database.py", "Database File"),
            ("backend/requirements.txt", "Python Dependencies"),
            ("backend/scripts/wait_for_db.py", "Database Wait Script"),
            ("backend/scripts/migrate_database.py", "Database Migration Script"),
        ]
        
        all_exist = True
        for file_path, description in backend_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        # Check if requirements.txt has production dependencies
        req_path = self.project_root / "backend/requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                content = f.read()
                required_deps = ['fastapi', 'uvicorn', 'sqlalchemy', 'pymysql', 'alembic']
                missing_deps = [dep for dep in required_deps if dep not in content]
                if missing_deps:
                    self.log_check("Backend Dependencies", False, f"Missing: {', '.join(missing_deps)}")
                    all_exist = False
                else:
                    self.log_check("Backend Dependencies", True, "All required dependencies present")
        
        return all_exist
    
    def check_frontend_code(self) -> bool:
        """Check frontend code quality"""
        print("\n⚛️ Checking Frontend Code...")
        
        # Check if frontend has required files
        frontend_files = [
            ("frontend/package.json", "Package Configuration"),
            ("frontend/Dockerfile", "Frontend Dockerfile"),
            ("frontend/nginx.conf", "Frontend Nginx Config"),
            ("frontend/src/App.js", "Main App Component"),
            ("frontend/src/lib/api.js", "API Client"),
        ]
        
        all_exist = True
        for file_path, description in frontend_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        # Check if package.json has build script
        package_path = self.project_root / "frontend/package.json"
        if package_path.exists():
            with open(package_path, 'r') as f:
                content = json.load(f)
                if 'scripts' in content and 'build' in content['scripts']:
                    self.log_check("Frontend Build Script", True, "Build script present")
                else:
                    self.log_check("Frontend Build Script", False, "Build script missing")
                    all_exist = False
        
        return all_exist
    
    def check_desktop_agent(self) -> bool:
        """Check Desktop Agent configuration"""
        print("\n🖥️ Checking Desktop Agent...")
        
        agent_files = [
            ("DesktopAgent/agent.py", "Main Agent File"),
            ("DesktopAgent/cloud-config.py", "Cloud Configuration"),
            ("DesktopAgent/requirements.txt", "Agent Dependencies"),
        ]
        
        all_exist = True
        for file_path, description in agent_files:
            if not self.check_file_exists(file_path, description):
                all_exist = False
        
        return all_exist
    
    def check_security_configuration(self) -> bool:
        """Check security configuration"""
        print("\n🔐 Checking Security Configuration...")
        
        # Check if production.env has secure values
        prod_env_path = self.project_root / "production.env"
        if prod_env_path.exists():
            with open(prod_env_path, 'r') as f:
                content = f.read()
                
                # Check for secure password patterns
                if "secure_" in content and "change_me" not in content:
                    self.log_check("Environment Security", True, "Secure passwords configured")
                else:
                    self.log_check("Environment Security", False, "Insecure or placeholder passwords")
                    return False
        
        # Check Nginx security headers
        nginx_conf_path = self.project_root / "nginx/conf.d/default.conf"
        if nginx_conf_path.exists():
            with open(nginx_conf_path, 'r') as f:
                content = f.read()
                security_headers = [
                    "Strict-Transport-Security",
                    "X-Content-Type-Options",
                    "X-Frame-Options",
                    "Content-Security-Policy"
                ]
                found_headers = [header for header in security_headers if header in content]
                if len(found_headers) >= 3:
                    self.log_check("Nginx Security Headers", True, f"Found {len(found_headers)} security headers")
                else:
                    self.log_check("Nginx Security Headers", False, f"Only {len(found_headers)} security headers found")
                    return False
        
        return True
    
    def run_all_checks(self) -> bool:
        """Run all production verification checks"""
        print("🔍 Starting Production Verification")
        print("=" * 60)
        
        checks = [
            self.check_docker_files,
            self.check_environment_files,
            self.check_ssl_configuration,
            self.check_deployment_scripts,
            self.check_backend_code,
            self.check_frontend_code,
            self.check_desktop_agent,
            self.check_security_configuration,
        ]
        
        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Verification Summary")
        print("=" * 60)
        
        passed = sum(1 for result in self.results if result['success'])
        total = len(self.results)
        
        print(f"Total Checks: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if all_passed:
            print("\n🎉 All checks passed! Application is ready for production deployment.")
            print("\n📋 Next Steps:")
            print("1. Run: ./generate-secrets.sh")
            print("2. Run: ./deploy-production.sh")
            print("3. Test: ./test-deployment.sh")
            print("4. Monitor: docker-compose -f docker-compose.prod.yml --env-file production.env logs")
        else:
            print(f"\n⚠️ {total - passed} checks failed. Please fix the issues above before deploying.")
            print("\n🔧 Common fixes:")
            print("- Run: ./generate-secrets.sh")
            print("- Check file permissions: chmod +x *.sh")
            print("- Verify all required files exist")
            print("- Update configuration files")
        
        return all_passed

def main():
    """Main verification function"""
    verifier = ProductionVerifier()
    success = verifier.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
