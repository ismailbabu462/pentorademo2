#!/usr/bin/env python3
"""
Google Cloud Configuration for Desktop Agent
This module handles Google Cloud specific configurations and optimizations.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CloudConfig:
    """Google Cloud configuration manager for Desktop Agent"""
    
    def __init__(self):
        self.config = self.load_cloud_config()
    
    def load_cloud_config(self) -> Dict[str, Any]:
        """Load Google Cloud specific configuration"""
        config = {
            # Network configuration
            'host': '0.0.0.0',  # Allow external connections
            'port': int(os.getenv('DESKTOP_AGENT_PORT', 13337)),
            
            # Google Cloud specific settings
            'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', ''),
            'zone': os.getenv('GOOGLE_CLOUD_ZONE', ''),
            'instance_name': os.getenv('GOOGLE_CLOUD_INSTANCE', ''),
            
            # Security settings for cloud deployment
            'max_connections': int(os.getenv('MAX_CONNECTIONS', 50)),
            'rate_limit_per_minute': int(os.getenv('RATE_LIMIT_PER_MINUTE', 30)),
            'enable_ssl': os.getenv('ENABLE_SSL', 'false').lower() == 'true',
            'ssl_cert_path': os.getenv('SSL_CERT_PATH', ''),
            'ssl_key_path': os.getenv('SSL_KEY_PATH', ''),
            
            # Tool execution settings
            'max_concurrent_tools': int(os.getenv('MAX_CONCURRENT_TOOLS', 5)),
            'tool_timeout': int(os.getenv('TOOL_TIMEOUT', 300)),
            'max_output_size': int(os.getenv('MAX_OUTPUT_SIZE', 50 * 1024 * 1024)),  # 50MB
            
            # Logging configuration
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'enable_cloud_logging': os.getenv('ENABLE_CLOUD_LOGGING', 'false').lower() == 'true',
            
            # Health check settings
            'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 30)),
            'enable_health_endpoint': os.getenv('ENABLE_HEALTH_ENDPOINT', 'true').lower() == 'true',
        }
        
        # Validate required settings
        if not config['project_id']:
            logger.warning("GOOGLE_CLOUD_PROJECT not set, some features may not work")
        
        return config
    
    def get_network_config(self) -> Dict[str, Any]:
        """Get network configuration for Google Cloud"""
        return {
            'host': self.config['host'],
            'port': self.config['port'],
            'max_connections': self.config['max_connections'],
            'enable_ssl': self.config['enable_ssl'],
            'ssl_cert_path': self.config['ssl_cert_path'],
            'ssl_key_path': self.config['ssl_key_path'],
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration for Google Cloud"""
        return {
            'rate_limit_per_minute': self.config['rate_limit_per_minute'],
            'max_concurrent_tools': self.config['max_concurrent_tools'],
            'tool_timeout': self.config['tool_timeout'],
            'max_output_size': self.config['max_output_size'],
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration for Google Cloud"""
        return {
            'log_level': self.config['log_level'],
            'enable_cloud_logging': self.config['enable_cloud_logging'],
        }
    
    def is_cloud_environment(self) -> bool:
        """Check if running in Google Cloud environment"""
        return bool(
            self.config['project_id'] or 
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS') or
            os.getenv('GCLOUD_PROJECT')
        )
    
    def get_cloud_metadata(self) -> Dict[str, Any]:
        """Get Google Cloud instance metadata"""
        metadata = {}
        
        try:
            # Try to get instance metadata from Google Cloud metadata server
            import requests
            
            # Get instance metadata
            metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/"
            headers = {"Metadata-Flavor": "Google"}
            
            # Get basic instance info
            instance_info = requests.get(
                f"{metadata_url}?recursive=true",
                headers=headers,
                timeout=5
            )
            
            if instance_info.status_code == 200:
                metadata = instance_info.json()
                
        except Exception as e:
            logger.debug(f"Could not fetch cloud metadata: {e}")
        
        return metadata
    
    def setup_cloud_logging(self):
        """Setup Google Cloud Logging if enabled"""
        if not self.config['enable_cloud_logging']:
            return
        
        try:
            from google.cloud import logging as cloud_logging
            
            # Initialize Cloud Logging client
            client = cloud_logging.Client(project=self.config['project_id'])
            client.setup_logging()
            
            logger.info("Google Cloud Logging enabled")
            
        except ImportError:
            logger.warning("google-cloud-logging not installed, using standard logging")
        except Exception as e:
            logger.warning(f"Failed to setup cloud logging: {e}")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status for Google Cloud health checks"""
        return {
            'status': 'healthy',
            'project_id': self.config['project_id'],
            'zone': self.config['zone'],
            'instance_name': self.config['instance_name'],
            'is_cloud_environment': self.is_cloud_environment(),
            'config_loaded': bool(self.config),
        }
