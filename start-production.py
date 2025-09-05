#!/usr/bin/env python3
"""
Google Cloud VM Production Startup Script
Starts all services in the correct order with health checks and monitoring
"""

import asyncio
import subprocess
import time
import json
import logging
import os
import sys
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProductionManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.processes = {}
        self.health_checks = {}
        self.startup_order = [
            'mysql',
            'redis', 
            'ollama',
            'backend',
            'celery-worker',
            'frontend',
            'nginx',
            'desktop-agent'
        ]
        self.required_ports = {
            'mysql': 3306,
            'redis': 6379,
            'backend': 8001,
            'frontend': 80,
            'nginx': 80,
            'desktop-agent': 13337
        }
        # Get external IP or use domain
        self.external_ip = os.getenv('EXTERNAL_IP') or self.get_external_ip()
        self.domain = os.getenv('DOMAIN', 'pentorasecbeta.mywire.org')
        self.use_https = os.getenv('USE_HTTPS', 'true').lower() == 'true'
        
        protocol = 'https' if self.use_https else 'http'
        self.health_endpoints = {
            'backend': f'http://{self.external_ip}:8001/health',
            'frontend': f'{protocol}://{self.domain}/health',
            'desktop-agent': f'http://{self.external_ip}:13338/health'
        }
        
        # Service URLs for display
        self.service_urls = {
            'frontend': f'{protocol}://{self.domain}',
            'api': f'{protocol}://{self.domain}/api',
            'health': f'{protocol}://{self.domain}/health',
            'phpmyadmin': f'{protocol}://{self.domain}/phpmyadmin',
            'desktop_agent': f'ws://{self.external_ip}:13337',
            'desktop_agent_health': f'http://{self.external_ip}:13338/health'
        }
        
    def get_external_ip(self) -> str:
        """Get external IP address of the VM"""
        try:
            import requests
            # Try multiple services to get external IP
            services = [
                'https://api.ipify.org',
                'https://ipinfo.io/ip',
                'https://ifconfig.me/ip',
                'https://checkip.amazonaws.com'
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        if self.is_valid_ip(ip):
                            logger.info(f"External IP detected: {ip}")
                            return ip
                except Exception:
                    continue
            
            # Fallback to localhost if can't get external IP
            logger.warning("Could not detect external IP, using localhost")
            return "localhost"
            
        except Exception as e:
            logger.warning(f"Error getting external IP: {e}, using localhost")
            return "localhost"
    
    def is_valid_ip(self, ip: str) -> bool:
        """Check if IP address is valid"""
        import re
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        parts = ip.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    
    def log_status(self, service: str, status: str, message: str = ""):
        """Log service status with emoji"""
        emoji_map = {
            'starting': '🚀',
            'running': '✅',
            'stopped': '❌',
            'error': '💥',
            'waiting': '⏳',
            'healthy': '💚',
            'unhealthy': '💔'
        }
        emoji = emoji_map.get(status, '📋')
        logger.info(f"{emoji} {service.upper()}: {message}")
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port:
                    return False
            return True
        except Exception:
            return True
    
    def kill_process_on_port(self, port: int):
        """Kill process running on specific port"""
        try:
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.pid:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info(f"Killed process {conn.pid} on port {port}")
        except Exception as e:
            logger.warning(f"Could not kill process on port {port}: {e}")
    
    def wait_for_port(self, port: int, timeout: int = 30) -> bool:
        """Wait for a port to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.check_port_available(port):
                return True
            time.sleep(1)
        return False
    
    def check_health_endpoint(self, url: str, timeout: int = 10) -> bool:
        """Check if a health endpoint is responding"""
        try:
            import requests
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_docker_services(self) -> bool:
        """Start Docker services using docker-compose"""
        try:
            self.log_status('docker', 'starting', 'Starting Docker services...')
            
            # Stop any existing services
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.prod.yml', 
                '--env-file', 'production.env', 'down', '--remove-orphans'
            ], cwd=self.project_root, check=False)
            
            # Start services
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.prod.yml',
                '--env-file', 'production.env', 'up', '-d'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_status('docker', 'running', 'Docker services started successfully')
                return True
            else:
                self.log_status('docker', 'error', f'Failed to start Docker services: {result.stderr}')
                return False
                
        except Exception as e:
            self.log_status('docker', 'error', f'Docker startup failed: {e}')
            return False
    
    def start_desktop_agent(self) -> bool:
        """Start Desktop Agent as a separate process"""
        try:
            self.log_status('desktop-agent', 'starting', 'Starting Desktop Agent...')
            
            # Check if port is available
            if not self.check_port_available(13337):
                self.kill_process_on_port(13337)
                time.sleep(2)
            
            # Start Desktop Agent
            agent_script = self.project_root / 'DesktopAgent' / 'agent.py'
            if not agent_script.exists():
                self.log_status('desktop-agent', 'error', 'Desktop Agent script not found')
                return False
            
            # Install Desktop Agent dependencies
            requirements = self.project_root / 'DesktopAgent' / 'requirements.txt'
            if requirements.exists():
                subprocess.run([
                    'pip', 'install', '-r', str(requirements)
                ], check=False)
            
            # Start the agent
            process = subprocess.Popen([
                'python', str(agent_script)
            ], cwd=self.project_root / 'DesktopAgent')
            
            self.processes['desktop-agent'] = process
            
            # Wait for port to be available
            if self.wait_for_port(13337, 30):
                self.log_status('desktop-agent', 'running', 'Desktop Agent started successfully')
                return True
            else:
                self.log_status('desktop-agent', 'error', 'Desktop Agent failed to start')
                return False
                
        except Exception as e:
            self.log_status('desktop-agent', 'error', f'Desktop Agent startup failed: {e}')
            return False
    
    def wait_for_service_health(self, service: str, max_wait: int = 60) -> bool:
        """Wait for a service to become healthy"""
        if service not in self.health_endpoints:
            return True
        
        self.log_status(service, 'waiting', f'Waiting for health check...')
        
        start_time = time.time()
        while time.time() - start_time < max_wait:
            if self.check_health_endpoint(self.health_endpoints[service]):
                self.log_status(service, 'healthy', 'Service is healthy')
                return True
            time.sleep(5)
        
        self.log_status(service, 'unhealthy', 'Service health check failed')
        return False
    
    def start_services_sequentially(self) -> bool:
        """Start services in the correct order"""
        self.log_status('system', 'starting', 'Starting production services...')
        
        # Step 1: Start Docker services
        if not self.start_docker_services():
            return False
        
        # Step 2: Wait for core services
        core_services = ['mysql', 'redis', 'backend']
        for service in core_services:
            if not self.wait_for_service_health(service, 120):
                self.log_status(service, 'error', f'{service} failed to start properly')
                return False
        
        # Step 3: Start Desktop Agent
        if not self.start_desktop_agent():
            self.log_status('desktop-agent', 'error', 'Desktop Agent failed to start')
            # Don't fail the entire startup for Desktop Agent
        
        # Step 4: Final health checks
        self.log_status('system', 'waiting', 'Performing final health checks...')
        time.sleep(10)
        
        return True
    
    def monitor_services(self):
        """Monitor running services and restart if needed"""
        self.log_status('monitor', 'starting', 'Starting service monitoring...')
        
        while True:
            try:
                # Check Docker services
                result = subprocess.run([
                    'docker-compose', '-f', 'docker-compose.prod.yml',
                    '--env-file', 'production.env', 'ps', '--format', 'json'
                ], cwd=self.project_root, capture_output=True, text=True)
                
                if result.returncode == 0:
                    services = json.loads(result.stdout)
                    for service in services:
                        if service['State'] != 'running':
                            self.log_status('monitor', 'error', f'Service {service["Name"]} is not running')
                
                # Check Desktop Agent
                if 'desktop-agent' in self.processes:
                    process = self.processes['desktop-agent']
                    if process.poll() is not None:
                        self.log_status('desktop-agent', 'error', 'Desktop Agent process died, restarting...')
                        self.start_desktop_agent()
                
                # Health check all services
                for service, endpoint in self.health_endpoints.items():
                    if not self.check_health_endpoint(endpoint, 5):
                        self.log_status(service, 'unhealthy', f'Health check failed: {endpoint}')
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.log_status('monitor', 'stopped', 'Monitoring stopped by user')
                break
            except Exception as e:
                self.log_status('monitor', 'error', f'Monitoring error: {e}')
                time.sleep(30)
    
    def stop_all_services(self):
        """Stop all running services"""
        self.log_status('system', 'stopping', 'Stopping all services...')
        
        # Stop Docker services
        try:
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.prod.yml',
                '--env-file', 'production.env', 'down', '--remove-orphans'
            ], cwd=self.project_root, check=False)
            self.log_status('docker', 'stopped', 'Docker services stopped')
        except Exception as e:
            self.log_status('docker', 'error', f'Error stopping Docker services: {e}')
        
        # Stop Desktop Agent
        if 'desktop-agent' in self.processes:
            try:
                process = self.processes['desktop-agent']
                process.terminate()
                process.wait(timeout=10)
                self.log_status('desktop-agent', 'stopped', 'Desktop Agent stopped')
            except Exception as e:
                self.log_status('desktop-agent', 'error', f'Error stopping Desktop Agent: {e}')
        
        self.log_status('system', 'stopped', 'All services stopped')
    
    def show_status(self):
        """Show current status of all services"""
        print("\n" + "="*60)
        print("📊 PRODUCTION SERVICES STATUS")
        print("="*60)
        
        # Docker services status
        try:
            result = subprocess.run([
                'docker-compose', '-f', 'docker-compose.prod.yml',
                '--env-file', 'production.env', 'ps'
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("\n🐳 DOCKER SERVICES:")
                print(result.stdout)
        except Exception as e:
            print(f"\n❌ Docker status error: {e}")
        
        # Desktop Agent status
        if 'desktop-agent' in self.processes:
            process = self.processes['desktop-agent']
            if process.poll() is None:
                print(f"\n🖥️ DESKTOP AGENT: Running (PID: {process.pid})")
            else:
                print(f"\n❌ DESKTOP AGENT: Stopped")
        else:
            print(f"\n❌ DESKTOP AGENT: Not started")
        
        # Health checks
        print(f"\n💚 HEALTH CHECKS:")
        for service, endpoint in self.health_endpoints.items():
            status = "✅ Healthy" if self.check_health_endpoint(endpoint, 5) else "❌ Unhealthy"
            print(f"  {service}: {status} ({endpoint})")
        
        # Port status
        print(f"\n🔌 PORT STATUS:")
        for service, port in self.required_ports.items():
            status = "✅ Open" if not self.check_port_available(port) else "❌ Closed"
            print(f"  {service} (port {port}): {status}")
        
        # Service URLs
        print(f"\n🌐 SERVICE URLs:")
        for service, url in self.service_urls.items():
            print(f"  {service}: {url}")
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            self.log_status('system', 'stopping', f'Received signal {signum}, shutting down...')
            self.stop_all_services()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """Main run method"""
        print("🚀 GOOGLE CLOUD VM PRODUCTION STARTUP")
        print("="*60)
        print(f"📅 Started at: {datetime.now(timezone.utc).isoformat()}")
        print(f"📁 Project root: {self.project_root}")
        print(f"🌐 External IP: {self.external_ip}")
        print(f"🌍 Domain: {self.domain}")
        print(f"🐍 Python version: {sys.version}")
        print("="*60)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        try:
            # Start services
            if not self.start_services_sequentially():
                self.log_status('system', 'error', 'Failed to start services')
                return False
            
            # Show initial status
            self.show_status()
            
            # Start monitoring
            self.monitor_services()
            
        except KeyboardInterrupt:
            self.log_status('system', 'stopping', 'Shutdown requested by user')
        except Exception as e:
            self.log_status('system', 'error', f'Unexpected error: {e}')
        finally:
            self.stop_all_services()
        
        return True

def main():
    """Main entry point"""
    # Check if running as root
    if os.geteuid() == 0:
        print("❌ Please do not run this script as root")
        sys.exit(1)
    
    # Check if in correct directory
    if not Path('docker-compose.prod.yml').exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check if production.env exists
    if not Path('production.env').exists():
        print("❌ production.env not found. Please run ./generate-secrets.sh first")
        sys.exit(1)
    
    # Start production manager
    manager = ProductionManager()
    success = manager.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
