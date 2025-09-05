#!/usr/bin/env python3
"""
Fix Frontend Production Mode
This script ensures frontend runs in production mode on the domain
"""

import subprocess
import time
import os
import sys
from pathlib import Path

def run_command(cmd, description, cwd=None):
    """Run a command and return success status"""
    try:
        print(f"🔧 {description}...")
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def get_external_ip():
    """Get external IP address"""
    try:
        result = subprocess.run(['curl', '-s', 'https://api.ipify.org'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    try:
        result = subprocess.run(['curl', '-s', 'https://ipinfo.io/ip'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return "YOUR_VM_IP"

def main():
    print("🔧 FIXING FRONTEND PRODUCTION MODE")
    print("==================================")
    
    # Get external IP
    external_ip = get_external_ip()
    domain = "pentorasecbeta.mywire.org"
    
    print(f"🌐 External IP: {external_ip}")
    print(f"🌐 Domain: {domain}")
    
    # Stop all services
    print("\n🛑 Stopping all services...")
    run_command("docker compose -f docker-compose.prod.yml --env-file production.env down --remove-orphans", 
                "Stopping services")
    
    # Remove frontend container and image to force rebuild
    print("\n🗑️ Removing frontend container and image...")
    run_command("docker rm -f pentest_frontend", "Removing frontend container")
    run_command("docker rmi pentest_frontend", "Removing frontend image")
    
    # Clean up Docker
    print("\n🧹 Cleaning up Docker...")
    run_command("docker system prune -f", "Cleaning Docker")
    
    # Generate self-signed SSL certificate if not exists
    print("\n🔒 Ensuring SSL certificate exists...")
    os.makedirs("nginx/ssl", exist_ok=True)
    
    if not Path("nginx/ssl/nginx-selfsigned.crt").exists():
        run_command("""openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/nginx-selfsigned.key \
            -out nginx/ssl/nginx-selfsigned.crt \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=pentorasecbeta.mywire.org" """, 
            "Generating SSL certificate")
    else:
        print("✅ Self-signed certificate already exists")
    
    # Start services
    print("\n🚀 Starting production services...")
    if not run_command("docker compose -f docker-compose.prod.yml --env-file production.env up -d", 
                       "Starting services"):
        print("❌ Failed to start services")
        return False
    
    # Wait for services
    print("\n⏳ Waiting for services to start...")
    time.sleep(30)
    
    # Check status
    print("\n📊 Service Status:")
    run_command("docker compose -f docker-compose.prod.yml --env-file production.env ps", 
                "Checking service status")
    
    # Show access URLs
    print("\n🎉 FRONTEND PRODUCTION MODE FIXED!")
    print("==================================")
    print("")
    print("📋 Access URLs:")
    print(f"  🌐 Frontend: https://{domain}")
    print(f"  🔧 API: https://{domain}/api")
    print(f"  ❤️ Health: https://{domain}/health")
    print(f"  🗄️ phpMyAdmin: https://{domain}/phpmyadmin")
    print(f"  🖥️ Backend Direct: http://{external_ip}:8001")
    print("")
    print("🔧 Useful Commands:")
    print("  View logs: docker compose -f docker-compose.prod.yml --env-file production.env logs")
    print("  Stop all: docker compose -f docker-compose.prod.yml --env-file production.env down")
    print("  Restart: python fix-frontend-production.py")
    print("")
    print("⚠️ Important:")
    print("  - Frontend is now running in PRODUCTION mode")
    print("  - Make sure ports 80, 443 are open in your firewall")
    print("  - Check DNS is pointing to your server IP")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
