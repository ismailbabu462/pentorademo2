#!/usr/bin/env python3
"""
Quick Start Script for Google Cloud VM
Simple script to start all services with minimal configuration
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"✅ {description} found")
        return True
    else:
        print(f"❌ {description} not found")
        return False

def main():
    """Main quick start function"""
    print("🚀 QUICK START - GOOGLE CLOUD VM")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    required_files = [
        ("docker-compose.prod.yml", "Production Docker Compose"),
        ("production.env", "Production Environment"),
        ("backend/Dockerfile", "Backend Dockerfile"),
        ("frontend/Dockerfile", "Frontend Dockerfile"),
    ]
    
    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Missing required files. Please check your setup.")
        return False
    
    # Check if Docker is running
    if not run_command("docker --version", "Checking Docker"):
        print("❌ Docker is not installed or not running")
        return False
    
    if not run_command("docker-compose --version", "Checking Docker Compose"):
        print("❌ Docker Compose is not installed")
        return False
    
    print("\n✅ All prerequisites met!")
    
    # Generate secrets if needed
    if not Path("production.env").exists() or "change_me" in open("production.env").read():
        print("\n🔐 Generating secure secrets...")
        if not run_command("./generate-secrets.sh", "Generating secrets"):
            print("❌ Failed to generate secrets")
            return False
    
    # Stop any existing services
    print("\n🛑 Stopping existing services...")
    run_command("docker compose -f docker-compose.prod.yml --env-file production.env down --remove-orphans", 
                "Stopping existing services")
    
    # Clean up Docker
    print("\n🧹 Cleaning up Docker...")
    run_command("docker system prune -f", "Cleaning Docker system")
    
    # Start services
    print("\n🚀 Starting production services...")
    if not run_command("docker compose -f docker-compose.prod.yml --env-file production.env up -d", 
                       "Starting Docker services"):
        print("❌ Failed to start Docker services")
        return False
    
    # Wait for services to be ready
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(30)
    
    # Check service status
    print("\n📊 Checking service status...")
    run_command("docker compose -f docker-compose.prod.yml --env-file production.env ps", 
                "Service status")
    
    # Start Desktop Agent
    print("\n🖥️ Starting Desktop Agent...")
    if Path("DesktopAgent/agent.py").exists():
        if not run_command("python DesktopAgent/agent.py &", "Starting Desktop Agent", cwd="DesktopAgent"):
            print("⚠️ Desktop Agent failed to start (optional)")
    else:
        print("⚠️ Desktop Agent not found (optional)")
    
    # Final status
    print("\n" + "=" * 50)
    print("🎉 PRODUCTION STARTUP COMPLETE!")
    print("=" * 50)
    
    # Get external IP
    try:
        import requests
        external_ip = requests.get('https://api.ipify.org', timeout=5).text.strip()
    except:
        external_ip = "YOUR_VM_IP"
    
    domain = os.getenv('DOMAIN', 'pentorasecbeta.mywire.org')
    
    print("\n📋 Service URLs:")
    print(f"  🌐 Frontend: https://{domain}")
    print(f"  🔧 API: https://{domain}/api")
    print(f"  ❤️ Health: https://{domain}/health")
    print(f"  🗄️ phpMyAdmin: https://{domain}/phpmyadmin")
    print(f"  🖥️ Desktop Agent: ws://{external_ip}:13337")
    print(f"  🖥️ Desktop Agent Health: http://{external_ip}:13338/health")
    print(f"  🔧 Backend Direct: http://{external_ip}:8001")
    
    print("\n🔧 Useful Commands:")
    print("  View logs: docker compose -f docker-compose.prod.yml --env-file production.env logs")
    print("  Stop all: docker compose -f docker-compose.prod.yml --env-file production.env down")
    print("  Restart: python quick-start.py")
    
    print("\n⚠️ Important:")
    print("  - Make sure ports 80, 443, and 13337 are open in your firewall")
    print("  - Check DNS is pointing to your server IP")
    print("  - Monitor logs for any issues")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
