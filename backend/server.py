from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import dependencies
from routers.auth import get_current_user
from dependencies import (
    check_project_creation_permissions,
    check_collaboration_permissions,
    check_subfinder_execution_permissions,
    check_amass_execution_permissions,
    check_nmap_execution_permissions,
    check_nuclei_execution_permissions,
    check_ffuf_execution_permissions,
    check_gobuster_execution_permissions
)
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json

# Import security headers middleware
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.rate_limiting import RateLimitMiddleware

# SECURITY: Safe JSON parsing function
def _safe_json_loads(json_str: str, default=None):
    """Safely parse JSON string with error handling"""
    if not json_str:
        return default or []
    try:
        # SECURITY: Limit JSON size to prevent DoS
        if len(json_str) > 10000:  # 10KB limit
            return default or []
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError, ValueError):
        return default or []

# Import utility functions
from utils.validation import sanitize_input, validate_uuid
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
import subprocess
import asyncio
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Import config and database
from config import CORS_ORIGINS
from database import init_db, get_db, Project as DBProject, User as DBUser, Target as DBTarget, Note as DBNote, Vulnerability as DBVulnerability

# Initialize database with error handling
try:
    init_db()
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")
    logger.info("This might be due to database not being ready yet. The application will retry on first request.")
    # Don't exit here, let the application start and retry on first request

# Create the main app without a prefix
app = FastAPI(title="Emergent Pentest Suite API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    PLANNING = "planning"

class TargetType(str, Enum):
    DOMAIN = "domain"
    IP = "ip" 
    CIDR = "cidr"
    URL = "url"

class VulnerabilitySeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ToolStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"

# Models
class Target(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    target_type: TargetType
    value: str
    description: Optional[str] = None
    is_in_scope: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TargetCreate(BaseModel):
    target_type: TargetType
    value: str
    description: Optional[str] = None
    is_in_scope: bool = True

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_members: List[str] = []
    targets: List[Target] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_members: List[str] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    team_members: Optional[List[str]] = None

class Note(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    title: str
    content: str
    tags: List[str] = []
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NoteCreate(BaseModel):
    project_id: str
    title: str
    content: str
    tags: List[str] = []

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

# Collaboration Models
class ProjectInviteCreate(BaseModel):
    email: str
    role: str = "member"  # member, admin, viewer

# Vulnerability Models
class VulnerabilityCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Vulnerability title")
    payload: str = Field(..., min_length=1, max_length=5000, description="Exploit payload")
    how_it_works: str = Field(..., min_length=1, max_length=10000, description="Vulnerability explanation")
    severity: str = Field(..., description="Severity level")
    
    @validator('title')
    def validate_title(cls, v):
        """Validate and sanitize vulnerability title"""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        
        # Use helper function for sanitization
        sanitized = sanitize_input(v, 200)
        if len(sanitized) > 200:
            raise ValueError('Title too long (max 200 characters)')
        
        # Check for XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',     # JavaScript protocol
            r'on\w+\s*=',      # Event handlers
            r'data:text/html', # Data URLs
            r'vbscript:',      # VBScript
            r'expression\s*\(', # CSS expressions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError('Title contains potentially dangerous content')
        
        return sanitized
    
    @validator('payload')
    def validate_payload(cls, v):
        """Validate and sanitize payload"""
        if not v or not v.strip():
            raise ValueError('Payload cannot be empty')
        
        payload = v.strip()
        if len(payload) > 5000:
            raise ValueError('Payload too long (max 5000 characters)')
        
        # Allow payload content but sanitize for display
        # Note: We keep the original payload for security research purposes
        # but we'll sanitize it when displaying
        return payload
    
    @validator('how_it_works')
    def validate_how_it_works(cls, v):
        """Validate and sanitize how it works description"""
        if not v or not v.strip():
            raise ValueError('How it works cannot be empty')
        
        # Use helper function for sanitization
        sanitized = sanitize_input(v, 10000)
        if len(sanitized) > 10000:
            raise ValueError('Description too long (max 10000 characters)')
        
        # Check for XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',     # JavaScript protocol
            r'on\w+\s*=',      # Event handlers
            r'data:text/html', # Data URLs
            r'vbscript:',      # VBScript
            r'expression\s*\(', # CSS expressions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError('Description contains potentially dangerous content')
        
        return sanitized
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate severity level"""
        valid_severities = ['critical', 'high', 'medium', 'low']
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {valid_severities}')
        return v

class VulnerabilityUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Vulnerability title")
    payload: Optional[str] = Field(None, min_length=1, max_length=5000, description="Exploit payload")
    how_it_works: Optional[str] = Field(None, min_length=1, max_length=10000, description="Vulnerability explanation")
    severity: Optional[str] = Field(None, description="Severity level")
    
    @validator('title')
    def validate_title(cls, v):
        """Validate and sanitize vulnerability title"""
        if v is None:
            return v
        
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        
        # Use helper function for sanitization
        sanitized = sanitize_input(v, 200)
        if len(sanitized) > 200:
            raise ValueError('Title too long (max 200 characters)')
        
        # Check for XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',     # JavaScript protocol
            r'on\w+\s*=',      # Event handlers
            r'data:text/html', # Data URLs
            r'vbscript:',      # VBScript
            r'expression\s*\(', # CSS expressions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError('Title contains potentially dangerous content')
        
        return sanitized
    
    @validator('payload')
    def validate_payload(cls, v):
        """Validate and sanitize payload"""
        if v is None:
            return v
        
        if not v or not v.strip():
            raise ValueError('Payload cannot be empty')
        
        payload = v.strip()
        if len(payload) > 5000:
            raise ValueError('Payload too long (max 5000 characters)')
        
        return payload
    
    @validator('how_it_works')
    def validate_how_it_works(cls, v):
        """Validate and sanitize how it works description"""
        if v is None:
            return v
        
        if not v or not v.strip():
            raise ValueError('How it works cannot be empty')
        
        # Use helper function for sanitization
        sanitized = sanitize_input(v, 10000)
        if len(sanitized) > 10000:
            raise ValueError('Description too long (max 10000 characters)')
        
        # Check for XSS patterns
        dangerous_patterns = [
            r'<script[^>]*>',  # Script tags
            r'javascript:',     # JavaScript protocol
            r'on\w+\s*=',      # Event handlers
            r'data:text/html', # Data URLs
            r'vbscript:',      # VBScript
            r'expression\s*\(', # CSS expressions
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError('Description contains potentially dangerous content')
        
        return sanitized
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validate severity level"""
        if v is None:
            return v
        
        valid_severities = ['critical', 'high', 'medium', 'low']
        if v not in valid_severities:
            raise ValueError(f'Severity must be one of: {valid_severities}')
        return v

class Vulnerability(BaseModel):
    id: str
    title: str
    payload: str
    how_it_works: str
    severity: str
    project_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

# Tool Models
class ToolScan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool_name: str
    target: str
    status: ToolStatus = ToolStatus.PENDING
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ToolScanCreate(BaseModel):
    target: str

class ToolScanResponse(BaseModel):
    success: bool
    message: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Helper functions (no longer needed with SQLite)

# Import mock tool functions
from tools_mock import run_subfinder, run_amass, run_nmap, run_nuclei, run_ffuf, run_gobuster

# Tool execution functions (now using mock implementations)
async def run_subfinder_old(target: str) -> Dict[str, Any]:
    """Run Subfinder tool for subdomain discovery"""
    try:
        # Clean target (remove protocol and www)
        clean_target = re.sub(r'^https?://', '', target)
        clean_target = re.sub(r'^www\.', '', clean_target)
        
        # Simulate real subdomain discovery
        import time
        time.sleep(2)  # Simulate scan time
        
        # Return mock results for now
        subdomains = [
            f"www.{clean_target}",
            f"mail.{clean_target}",
            f"admin.{clean_target}",
            f"api.{clean_target}",
            f"dev.{clean_target}"
        ]
        
        return {
            "subdomains": subdomains,
            "count": len(subdomains),
            "tool_version": "subfinder_mock",
            "execution_time": "2s"
        }
        
    except Exception as e:
        raise Exception(f"Subdomain discovery failed: {str(e)}")

async def run_amass(target: str) -> Dict[str, Any]:
    """Run Amass tool for attack surface mapping"""
    try:
        # Clean target
        clean_target = re.sub(r'^https?://', '', target)
        clean_target = re.sub(r'^www\.', '', clean_target)
        
        # Simulate real attack surface mapping
        import time
        time.sleep(3)  # Simulate scan time
        
        # Return mock results for now
        subdomains = [
            f"https://{clean_target}/admin",
            f"https://{clean_target}/api",
            f"https://{clean_target}/backup",
            f"https://{clean_target}/config",
            f"https://{clean_target}/test"
        ]
        
        return {
            "subdomains": subdomains,
            "count": len(subdomains),
            "tool_version": "amass_mock",
            "execution_time": "3s"
        }
        
    except Exception as e:
        raise Exception(f"Attack surface mapping failed: {str(e)}")

async def run_nmap(target: str) -> Dict[str, Any]:
    """Run Nmap tool for port scanning"""
    try:
        # Clean target
        clean_target = re.sub(r'^https?://', '', target)
        clean_target = re.sub(r'^www\.', '', clean_target)
        
        # Run nmap from tools container
        result = subprocess.run(
            ['nmap', '-sS', '-sV', '-O', '-p', '21,22,23,25,53,80,110,143,443,993,995,3306,3389,5432,8080,8443', clean_target],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse nmap output
            open_ports = []
            services = {}
            
            for line in result.stdout.strip().split('\n'):
                if 'open' in line and 'tcp' in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        port = int(parts[0].split('/')[0])
                        service = parts[2] if len(parts) > 2 else 'Unknown'
                        open_ports.append(port)
                        services[port] = service
            
            return {
                "open_ports": open_ports,
                "services": services,
                "total_ports_scanned": 17,
                "tool_version": "nmap",
                "execution_time": "real"
            }
        else:
            # If nmap fails, return empty results
            return {
                "open_ports": [],
                "services": {},
                "total_ports_scanned": 17,
                "tool_version": "nmap",
                "execution_time": "real",
                "error": result.stderr if result.stderr else "No open ports found"
            }
        
    except FileNotFoundError:
        raise Exception("Nmap tool not found. Please ensure tools container is running.")
    except subprocess.TimeoutExpired:
        raise Exception("Nmap scan timed out after 5 minutes.")
    except Exception as e:
        raise Exception(f"Nmap execution failed: {str(e)}")

async def run_nuclei(target: str) -> Dict[str, Any]:
    """Run Nuclei tool for vulnerability scanning"""
    try:
        # Clean target
        clean_target = re.sub(r'^https?://', '', target)
        if not clean_target.startswith('http'):
            clean_target = f"https://{clean_target}"
        
        # Try to use real nuclei first
        try:
            result = subprocess.run(
                ['nuclei', '-u', clean_target, '-silent', '-json', '-o', '/tmp/nuclei_output.json'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                # Read nuclei output
                try:
                    with open('/tmp/nuclei_output.json', 'r') as f:
                        vulnerabilities = []
                        for line in f:
                            if line.strip():
                                try:
                                    vuln_data = json.loads(line.strip())
                                    vulnerabilities.append({
                                        "severity": vuln_data.get('info', {}).get('severity', 'medium'),
                                        "template": vuln_data.get('template_id', 'nuclei'),
                                        "description": vuln_data.get('info', {}).get('description', 'Vulnerability found'),
                                        "cve": vuln_data.get('info', {}).get('classification', {}).get('cve_id', []),
                                        "url": vuln_data.get('matched_at', clean_target)
                                    })
                                except json.JSONDecodeError:
                                    continue
                    
                    return {
                        "vulnerabilities": vulnerabilities,
                        "count": len(vulnerabilities),
                        "tool_version": "nuclei",
                        "execution_time": "real"
                    }
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            pass
        
        # Fallback to nikto for vulnerability scanning
        result = subprocess.run(
            ['nikto', '-h', clean_target, '-Format', 'txt'],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse nikto output
            vulnerabilities = []
            for line in result.stdout.strip().split('\n'):
                if ':' in line and ('VULNERABLE' in line or 'WARNING' in line):
                    vulnerabilities.append({
                        "severity": "medium" if 'WARNING' in line else "high",
                        "template": "nikto",
                        "description": line.strip(),
                        "cve": [],
                        "url": clean_target
                    })
            
            return {
                "vulnerabilities": vulnerabilities,
                "count": len(vulnerabilities),
                "tool_version": "nikto_fallback",
                "execution_time": "real"
            }
        else:
            # If both fail, return empty results
            return {
                "vulnerabilities": [],
                "count": 0,
                "tool_version": "none",
                "execution_time": "real",
                "error": result.stderr if result.stderr else "No vulnerabilities found"
            }
        
    except FileNotFoundError:
        raise Exception("Nikto tool not found. Please ensure tools container is running.")
    except subprocess.TimeoutExpired:
        raise Exception("Nikto scan timed out after 10 minutes.")
    except Exception as e:
        raise Exception(f"Nikto execution failed: {str(e)}")

async def run_ffuf(target: str) -> Dict[str, Any]:
    """Run ffuf tool for web fuzzing"""
    try:
        # Clean target
        clean_target = re.sub(r'^https?://', '', target)
        if not clean_target.startswith('http'):
            clean_target = f"https://{clean_target}"
        
        # Try to use real ffuf first
        try:
            result = subprocess.run(
                ['ffuf', '-u', f"{clean_target}/FUZZ", '-w', '/usr/share/wordlists/common.txt', '-o', '/tmp/ffuf_output.json', '-of', 'json'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                # Read ffuf output
                try:
                    with open('/tmp/ffuf_output.json', 'r') as f:
                        ffuf_data = json.load(f)
                        directories = []
                        for result_item in ffuf_data.get('results', []):
                            if result_item.get('status') in [200, 301, 302, 403]:
                                directories.append(result_item.get('url', ''))
                    
                    return {
                        "directories": directories,
                        "count": len(directories),
                        "tool_version": "ffuf",
                        "execution_time": "real"
                    }
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
        except FileNotFoundError:
            pass
        
        # Fallback to dirb for directory fuzzing
        result = subprocess.run(
            ['dirb', clean_target, '/usr/share/wordlists/common.txt'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse dirb output
            directories = []
            for line in result.stdout.strip().split('\n'):
                if 'DIRB' in line and 'CODE:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        path = parts[1]
                        if path.startswith('/'):
                            directories.append(path)
            
            return {
                "directories": directories,
                "count": len(directories),
                "tool_version": "dirb_fallback",
                "execution_time": "real"
            }
        else:
            # If both fail, return empty results
            return {
                "directories": [],
                "count": 0,
                "tool_version": "none",
                "execution_time": "real",
                "error": result.stderr if result.stderr else "No directories found"
            }
        
    except subprocess.TimeoutExpired:
        raise Exception("Web fuzzing timed out after 5 minutes.")
    except Exception as e:
        raise Exception(f"Web fuzzing failed: {str(e)}")

async def run_gobuster(target: str) -> Dict[str, Any]:
    """Run Gobuster tool for directory brute forcing"""
    try:
        # Clean target
        clean_target = re.sub(r'^https?://', '', target)
        if not clean_target.startswith('http'):
            clean_target = f"https://{clean_target}"
        
        # Try to use real gobuster first
        try:
            result = subprocess.run(
                ['gobuster', 'dir', '-u', clean_target, '-w', '/usr/share/wordlists/common.txt', '-o', '/tmp/gobuster_output.txt'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                # Read gobuster output
                try:
                    with open('/tmp/gobuster_output.txt', 'r') as f:
                        directories = []
                        for line in f:
                            if line.strip() and 'Status:' in line:
                                parts = line.split()
                                if len(parts) >= 2:
                                    path = parts[0]
                                    if path.startswith('/'):
                                        directories.append(path)
                    
                    return {
                        "directories": directories,
                        "count": len(directories),
                        "tool_version": "gobuster",
                        "execution_time": "real"
                    }
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            pass
        
        # Fallback to dirb for directory brute forcing
        result = subprocess.run(
            ['dirb', clean_target, '/usr/share/wordlists/common.txt'],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse dirb output
            directories = []
            for line in result.stdout.strip().split('\n'):
                if 'DIRB' in line and 'CODE:' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        path = parts[1]
                        if path.startswith('/'):
                            directories.append(path)
            
            return {
                "directories": directories,
                "count": len(directories),
                "tool_version": "dirb_fallback",
                "execution_time": "real"
            }
        else:
            # If both fail, return empty results
            return {
                "directories": [],
                "count": 0,
                "tool_version": "none",
                "execution_time": "real",
                "error": result.stderr if result.stderr else "No directories found"
            }
        
    except subprocess.TimeoutExpired:
        raise Exception("Directory brute forcing timed out after 5 minutes.")
    except Exception as e:
        raise Exception(f"Directory brute forcing failed: {str(e)}")

# Project Routes
@api_router.post("/projects", response_model=Project)
async def create_project(
    project_data: ProjectCreate,
    auth_data: dict = Depends(check_project_creation_permissions),
    db: Session = Depends(get_db)
):
    # Extract user from auth_data
    current_user = auth_data["user"]
    
    # SECURITY: Safe logging - sanitize user input
    safe_user_id = str(current_user.id)[:8] + "..." if len(str(current_user.id)) > 8 else str(current_user.id)
    logger.debug(f"Create Project: User ID: {safe_user_id}")
    
    # Create project in SQLite
    db_project = DBProject(
        name=project_data.name,
        description=project_data.description,
        status=project_data.status,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        team_members=json.dumps(project_data.team_members) if project_data.team_members else None,
        user_id=current_user.id
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    logger.debug(f"Create Project: SQLite insert result: {db_project.id}")
    
    # Convert to Pydantic model for response
    project_obj = Project(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        status=db_project.status,
        start_date=db_project.start_date,
        end_date=db_project.end_date,
        team_members=json.loads(db_project.team_members) if db_project.team_members else [],
        targets=[],
        created_at=db_project.created_at,
        updated_at=db_project.updated_at
    )
    
    return project_obj

@api_router.get("/projects", response_model=List[Project])
async def get_projects(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # SECURITY: Safe logging - sanitize user input
    safe_user_id = str(current_user.id)[:8] + "..." if len(str(current_user.id)) > 8 else str(current_user.id)
    logger.debug(f"Get Projects: User ID: {safe_user_id}")
    
    # Get projects from SQLite
    db_projects = db.query(DBProject).filter(DBProject.user_id == current_user.id).all()
    logger.debug(f"Get Projects: Found {len(db_projects)} projects in SQLite")
    
    projects = []
    for db_project in db_projects:
        logger.debug(f"Get Projects: Project user_id: {db_project.user_id}")
        
        # Get targets for this project
        targets = db.query(DBTarget).filter(DBTarget.project_id == db_project.id).all()
        target_objects = [
            Target(
                id=target.id,
                target_type=target.target_type,
                value=target.value,
                description=target.description,
                is_in_scope=target.is_in_scope,
                created_at=target.created_at
            ) for target in targets
        ]
        
        project_obj = Project(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            status=db_project.status,
            start_date=db_project.start_date,
            end_date=db_project.end_date,
            team_members=_safe_json_loads(db_project.team_members, []),
            targets=target_objects,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        projects.append(project_obj)
    
    return projects

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(
    project_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get project from SQLite - SECURITY: Check ownership
        db_project = db.query(DBProject).filter(
            DBProject.id == project_id,
            DBProject.user_id == current_user.id
        ).first()
        if not db_project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get targets for this project
        targets = db.query(DBTarget).filter(DBTarget.project_id == db_project.id).all()
        target_objects = [
            Target(
                id=target.id,
                target_type=target.target_type,
                value=target.value,
                description=target.description,
                is_in_scope=target.is_in_scope,
                created_at=target.created_at
            ) for target in targets
        ]
        
        project_obj = Project(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            status=db_project.status,
            start_date=db_project.start_date,
            end_date=db_project.end_date,
            team_members=json.loads(db_project.team_members) if db_project.team_members else [],
            targets=target_objects,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        
        return project_obj
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logger.error(f"Get project error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(
    project_id: str, 
    project_update: ProjectUpdate, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get project from SQLite - SECURITY: Check ownership
    db_project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Update project fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "team_members" and value is not None:
            setattr(db_project, field, json.dumps(value))
        else:
            setattr(db_project, field, value)
    
    db_project.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_project)
    
    # Get targets for this project
    targets = db.query(DBTarget).filter(DBTarget.project_id == db_project.id).all()
    target_objects = [
        Target(
            id=target.id,
            target_type=target.target_type,
            value=target.value,
            description=target.description,
            is_in_scope=target.is_in_scope,
            created_at=target.created_at
        ) for target in targets
    ]
    
    project_obj = Project(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        status=db_project.status,
        start_date=db_project.start_date,
        end_date=db_project.end_date,
        team_members=json.loads(db_project.team_members) if db_project.team_members else [],
        targets=target_objects,
        created_at=db_project.created_at,
        updated_at=db_project.updated_at
    )
    
    return project_obj

@api_router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete project from SQLite - SECURITY: Check ownership
    db_project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete associated targets and notes first
    db.query(DBTarget).filter(DBTarget.project_id == project_id).delete()
    db.query(DBNote).filter(DBNote.project_id == project_id).delete()
    
    # Delete the project
    db.delete(db_project)
    db.commit()
    
    return {"message": "Project deleted successfully"}

@api_router.post("/projects/{project_id}/invite")
async def invite_user_to_project(
    project_id: str,
    invite_data: ProjectInviteCreate,
    auth_data: dict = Depends(check_collaboration_permissions),
    db: Session = Depends(get_db)
):
    """Invite a user to collaborate on a project (Premium feature)"""
    # Extract user from auth_data
    current_user = auth_data["user"]
    
    # Check if project exists and user owns it
    db_project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    
    if not db_project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )
    
    # For now, just return success (in real implementation, you'd send email invite)
    return {
        "message": f"Invitation sent to {invite_data.email} for role: {invite_data.role}",
        "project_id": project_id,
        "invited_email": invite_data.email,
        "role": invite_data.role
    }

# Target Routes
@api_router.post("/projects/{project_id}/targets", response_model=Target)
async def add_target_to_project(
    project_id: str, 
    target_data: TargetCreate, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # SECURITY: Check if project exists and belongs to current user
    project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Create target in SQLite
    db_target = DBTarget(
        target_type=target_data.target_type,
        value=target_data.value,
        description=target_data.description,
        is_in_scope=target_data.is_in_scope,
        project_id=project_id
    )
    
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    
    target_obj = Target(
        id=db_target.id,
        target_type=db_target.target_type,
        value=db_target.value,
        description=db_target.description,
        is_in_scope=db_target.is_in_scope,
        created_at=db_target.created_at
    )
    
    return target_obj

@api_router.get("/projects/{project_id}/targets", response_model=List[Target])
async def get_project_targets(
    project_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # SECURITY: Check if project exists and belongs to current user
    project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Get targets from SQLite
    targets = db.query(DBTarget).filter(DBTarget.project_id == project_id).all()
    target_objects = [
        Target(
            id=target.id,
            target_type=target.target_type,
            value=target.value,
            description=target.description,
            is_in_scope=target.is_in_scope,
            created_at=target.created_at
        ) for target in targets
    ]
    
    return target_objects

@api_router.delete("/projects/{project_id}/targets/{target_id}")
async def remove_target_from_project(
    project_id: str, 
    target_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # SECURITY: Check if project exists and belongs to current user
    project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Delete target from SQLite
    target = db.query(DBTarget).filter(DBTarget.id == target_id, DBTarget.project_id == project_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    
    db.delete(target)
    db.commit()
    
    return {"message": "Target removed successfully"}

# Notes Routes
@api_router.post("/notes", response_model=Note)
async def create_note(
    note_data: NoteCreate, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # SECURITY: Verify project exists and belongs to current user
        project = db.query(DBProject).filter(
            DBProject.id == note_data.project_id,
            DBProject.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Create note in SQLite
        db_note = DBNote(
            title=note_data.title,
            content=note_data.content,
            tags=json.dumps(note_data.tags) if note_data.tags else None,
            project_id=note_data.project_id,
            user_id=current_user.id
        )
        
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        
        note_obj = Note(
            id=db_note.id,
            title=db_note.title,
            content=db_note.content,
            tags=_safe_json_loads(db_note.tags, []),
            project_id=db_note.project_id,
            user_id=db_note.user_id,
            created_at=db_note.created_at,
            updated_at=db_note.updated_at
        )
        
        return note_obj
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logger.error(f"Create note error for user {current_user.id}: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )

@api_router.get("/projects/{project_id}/notes", response_model=List[Note])
async def get_project_notes(
    project_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # SECURITY: First verify project belongs to current user
        project = db.query(DBProject).filter(
            DBProject.id == project_id,
            DBProject.user_id == current_user.id
        ).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get notes from SQLite for the current user
        notes = db.query(DBNote).filter(
            DBNote.project_id == project_id,
            DBNote.user_id == current_user.id
        ).all()
        note_objects = [
            Note(
                id=note.id,
                title=note.title,
                content=note.content,
                tags=_safe_json_loads(note.tags, []),
                project_id=note.project_id,
                user_id=note.user_id,
                created_at=note.created_at,
                updated_at=note.updated_at
            ) for note in notes
        ]
        
        return note_objects
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logger.error(f"Get project notes error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )

@api_router.get("/notes/{note_id}", response_model=Note)
async def get_note(
    note_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get note from SQLite for the current user
        note = db.query(DBNote).filter(
            DBNote.id == note_id,
            DBNote.user_id == current_user.id
        ).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note_obj = Note(
            id=note.id,
            title=note.title,
            content=note.content,
            tags=json.loads(note.tags) if note.tags else [],
            project_id=note.project_id,
            user_id=note.user_id,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
        return note_obj
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logger.error(f"Get note error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )

@api_router.put("/notes/{note_id}", response_model=Note)
async def update_note(
    note_id: str, 
    note_update: NoteUpdate, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Get note from SQLite for the current user
        note = db.query(DBNote).filter(
            DBNote.id == note_id,
            DBNote.user_id == current_user.id
        ).first()
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
            
        # Update note fields
        update_data = note_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "tags" and value is not None:
                setattr(note, field, json.dumps(value))
            else:
                setattr(note, field, value)
        
        note.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(note)
        
        note_obj = Note(
            id=note.id,
            title=note.title,
            content=note.content,
            tags=json.loads(note.tags) if note.tags else [],
            project_id=note.project_id,
            user_id=note.user_id,
            created_at=note.created_at,
            updated_at=note.updated_at
        )
        
        return note_obj
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        logger.error(f"Update note error for user {current_user.id}: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred"
        )

@api_router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str, 
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Delete note from SQLite for the current user
    note = db.query(DBNote).filter(
        DBNote.id == note_id,
        DBNote.user_id == current_user.id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    
    return {"message": "Note deleted successfully"}

# Vulnerability Routes
@api_router.post("/projects/{project_id}/vulnerabilities", response_model=Vulnerability)
async def create_vulnerability(
    project_id: str,
    vuln_data: VulnerabilityCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new vulnerability for a project"""
    # SECURITY: Verify project exists and belongs to current user
    project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )
    
    # Additional security validation (redundant but extra safety)
    valid_severities = ['critical', 'high', 'medium', 'low']
    if vuln_data.severity not in valid_severities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid severity. Must be one of: {valid_severities}"
        )
    
    # SECURITY: Additional payload sanitization for storage
    # Keep original payload for security research but sanitize for display
    sanitized_payload = vuln_data.payload
    # Note: We don't sanitize payload here as it's needed for security research
    # Sanitization happens during display in frontend
    
    # Create vulnerability in database
    db_vuln = DBVulnerability(
        title=vuln_data.title,
        payload=vuln_data.payload,
        how_it_works=vuln_data.how_it_works,
        severity=vuln_data.severity,
        project_id=project_id,
        user_id=current_user.id
    )
    
    db.add(db_vuln)
    db.commit()
    db.refresh(db_vuln)
    
    # Convert to response model
    vuln_obj = Vulnerability(
        id=db_vuln.id,
        title=db_vuln.title,
        payload=db_vuln.payload,
        how_it_works=db_vuln.how_it_works,
        severity=db_vuln.severity,
        project_id=db_vuln.project_id,
        user_id=db_vuln.user_id,
        created_at=db_vuln.created_at,
        updated_at=db_vuln.updated_at
    )
    
    return vuln_obj

@api_router.get("/projects/{project_id}/vulnerabilities", response_model=List[Vulnerability])
async def get_project_vulnerabilities(
    project_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all vulnerabilities for a project"""
    # SECURITY: First verify project belongs to current user
    project = db.query(DBProject).filter(
        DBProject.id == project_id,
        DBProject.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found or access denied"
        )
    
    # Get vulnerabilities from database
    db_vulns = db.query(DBVulnerability).filter(
        DBVulnerability.project_id == project_id
    ).order_by(DBVulnerability.created_at.desc()).all()
    
    # Convert to response models
    vulnerabilities = []
    for db_vuln in db_vulns:
        vuln_obj = Vulnerability(
            id=db_vuln.id,
            title=db_vuln.title,
            payload=db_vuln.payload,
            how_it_works=db_vuln.how_it_works,
            severity=db_vuln.severity,
            project_id=db_vuln.project_id,
            user_id=db_vuln.user_id,
            created_at=db_vuln.created_at,
            updated_at=db_vuln.updated_at
        )
        vulnerabilities.append(vuln_obj)
    
    return vulnerabilities

@api_router.get("/vulnerabilities/{vuln_id}", response_model=Vulnerability)
async def get_vulnerability(
    vuln_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific vulnerability"""
    # Get vulnerability from database for the current user
    vuln = db.query(DBVulnerability).filter(
        DBVulnerability.id == vuln_id,
        DBVulnerability.user_id == current_user.id
    ).first()
    
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    # Convert to response model
    vuln_obj = Vulnerability(
        id=vuln.id,
        title=vuln.title,
        payload=vuln.payload,
        how_it_works=vuln.how_it_works,
        severity=vuln.severity,
        project_id=vuln.project_id,
        user_id=vuln.user_id,
        created_at=vuln.created_at,
        updated_at=vuln.updated_at
    )
    
    return vuln_obj

@api_router.put("/vulnerabilities/{vuln_id}", response_model=Vulnerability)
async def update_vulnerability(
    vuln_id: str,
    vuln_update: VulnerabilityUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a vulnerability"""
    # Get vulnerability from database for the current user
    vuln = db.query(DBVulnerability).filter(
        DBVulnerability.id == vuln_id,
        DBVulnerability.user_id == current_user.id
    ).first()
    
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    # Update fields if provided
    if vuln_update.title is not None:
        vuln.title = vuln_update.title
    if vuln_update.payload is not None:
        vuln.payload = vuln_update.payload
    if vuln_update.how_it_works is not None:
        vuln.how_it_works = vuln_update.how_it_works
    if vuln_update.severity is not None:
        # Validate severity
        valid_severities = ['critical', 'high', 'medium', 'low']
        if vuln_update.severity not in valid_severities:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid severity. Must be one of: {valid_severities}"
            )
        vuln.severity = vuln_update.severity
    
    vuln.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(vuln)
    
    # Convert to response model
    vuln_obj = Vulnerability(
        id=vuln.id,
        title=vuln.title,
        payload=vuln.payload,
        how_it_works=vuln.how_it_works,
        severity=vuln.severity,
        project_id=vuln.project_id,
        user_id=vuln.user_id,
        created_at=vuln.created_at,
        updated_at=vuln.updated_at
    )
    
    return vuln_obj

@api_router.delete("/vulnerabilities/{vuln_id}")
async def delete_vulnerability(
    vuln_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a vulnerability"""
    # Get vulnerability from database for the current user
    vuln = db.query(DBVulnerability).filter(
        DBVulnerability.id == vuln_id,
        DBVulnerability.user_id == current_user.id
    ).first()
    
    if not vuln:
        raise HTTPException(status_code=404, detail="Vulnerability not found")
    
    db.delete(vuln)
    db.commit()
    
    return {"message": "Vulnerability deleted successfully"}

# Tool Routes - DISABLED: Now using Desktop Agent
# @api_router.post("/tools/subfinder", response_model=ToolScanResponse)
# async def run_subfinder_tool(
#     scan_data: ToolScanCreate,
#     auth_data: dict = Depends(check_subfinder_execution_permissions)
# ):
#     """Run Subfinder tool for subdomain discovery"""
#     try:
#         print(f"🔧 Subfinder Debug: Starting scan for {scan_data.target}")
#         results = await run_subfinder(scan_data.target)
#         print(f"🔧 Subfinder Debug: Scan completed, results: {results}")
#         return ToolScanResponse(
#             success=True,
#             message="Subfinder scan completed successfully",
#             results=results
#         )
#     except Exception as e:
#         print(f"❌ Subfinder Debug: Error: {str(e)}")
#         return ToolScanResponse(
#             success=False,
#             message="Subfinder scan failed",
#             error=str(e)
#         )

# @api_router.post("/tools/amass", response_model=ToolScanResponse)
# async def run_amass_tool(
#     scan_data: ToolScanCreate,
#     auth_data: dict = Depends(check_amass_execution_permissions)
# ):
#     """Run Amass tool for attack surface mapping"""
#     try:
#         results = await run_amass(scan_data.target)
#         return ToolScanResponse(
#             success=True,
#             message="Amass scan completed successfully",
#             results=results
#         )
#     except Exception as e:
#         return ToolScanResponse(
#             success=False,
#             message="Amass scan failed",
#             error=str(e)
#         )

# @api_router.post("/tools/nmap", response_model=ToolScanResponse)
# async def run_nmap_tool(
#     scan_data: ToolScanCreate,
#     auth_data: dict = Depends(check_nmap_execution_permissions)
# ):
#     """Run Nmap tool for port scanning"""
#     try:
#         results = await run_nmap(scan_data.target)
#         return ToolScanResponse(
#             success=True,
#             message="Nmap scan completed successfully",
#             results=results
#         )
#     except Exception as e:
#         return ToolScanResponse(
#             success=False,
#             message="Nmap scan failed",
#             error=str(e)
#         )

# @api_router.post("/tools/nuclei", response_model=ToolScanResponse)
# async def run_nuclei_tool(
#     scan_data: ToolScanCreate,
#     auth_data: dict = Depends(check_nuclei_execution_permissions)
# ):
#     """Run Nuclei tool for vulnerability scanning"""
#     try:
#         results = await run_nuclei(scan_data.target)
#         return ToolScanResponse(
#             success=True,
#             message="Nuclei scan completed successfully",
#             results=results
#         )
#     except Exception as e:
#         return ToolScanResponse(
#             success=False,
#             message="Nuclei scan failed",
#             error=str(e)
#         )

# @api_router.post("/tools/ffuf", response_model=ToolScanResponse)
# async def run_ffuf_tool(
#     scan_data: ToolScanCreate,
#     auth_data: dict = Depends(check_ffuf_execution_permissions)
# ):
#     """Run ffuf tool for web fuzzing"""
#     try:
#         results = await run_ffuf(scan_data.target)
#         return ToolScanResponse(
#             success=True,
#             message="ffuf scan completed successfully",
#             results=results
#         )
#     except Exception as e:
#         return ToolScanResponse(
#             success=False,
#             message="ffuf scan failed",
#             error=str(e)
#         )

# @api_router.post("/tools/gobuster", response_model=ToolScanResponse)
# async def run_gobuster_tool(
#     scan_data: ToolScanCreate,
#     auth_data: dict = Depends(check_gobuster_execution_permissions)
# ):
#     """Run Gobuster tool for directory brute forcing"""
#     try:
#         results = await run_gobuster(scan_data.target)
#         return ToolScanResponse(
#             success=True,
#             message="Gobuster scan completed successfully",
#             results=results
#         )
#     except Exception as e:
#         return ToolScanResponse(
#             success=False,
#             message="Gobuster scan failed",
#             error=str(e)
#         )

@api_router.get("/tools/status")
async def get_tools_status():
    """Get status of all available tools"""
    tools_status = {
        "subfinder": {
            "name": "Subfinder",
            "status": "available",
            "description": "Fast passive subdomain discovery tool",
            "version": "latest"
        },
        "amass": {
            "name": "Amass",
            "status": "available",
            "description": "In-depth attack surface mapping",
            "version": "latest"
        },
        "nmap": {
            "name": "Nmap",
            "status": "available",
            "description": "Network discovery and port scanning",
            "version": "latest"
        },
        "nuclei": {
            "name": "Nuclei",
            "status": "available",
            "description": "Fast vulnerability scanner",
            "version": "latest"
        },
        "ffuf": {
            "name": "ffuf",
            "status": "available",
            "description": "Fast web fuzzer",
            "version": "latest"
        },
        "gobuster": {
            "name": "Gobuster",
            "status": "available",
            "description": "Directory and file brute-forcer",
            "version": "latest"
        }
    }
    
    # Check if tools are actually available on the system
    for tool_name in tools_status:
        try:
            if tool_name == "subfinder":
                subprocess.run(['subfinder', '-version'], capture_output=True, timeout=5)
            elif tool_name == "amass":
                subprocess.run(['amass', '-version'], capture_output=True, timeout=5)
            elif tool_name == "nmap":
                subprocess.run(['nmap', '-V'], capture_output=True, timeout=5)
            elif tool_name == "nuclei":
                subprocess.run(['nuclei', '-version'], capture_output=True, timeout=5)
            elif tool_name == "ffuf":
                subprocess.run(['ffuf', '-V'], capture_output=True, timeout=5)
            elif tool_name == "gobuster":
                subprocess.run(['gobuster', 'version'], capture_output=True, timeout=5)
            
            tools_status[tool_name]["status"] = "available"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            tools_status[tool_name]["status"] = "mock_only"
    
    return tools_status

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    # Get stats from SQLite
    total_projects = db.query(DBProject).count()
    active_projects = db.query(DBProject).filter(DBProject.status == "active").count()
    total_notes = db.query(DBNote).count()
    
    # Get recent projects
    recent_db_projects = db.query(DBProject).order_by(DBProject.updated_at.desc()).limit(5).all()
    recent_projects = []
    
    for db_project in recent_db_projects:
        # Get targets for this project
        targets = db.query(DBTarget).filter(DBTarget.project_id == db_project.id).all()
        target_objects = [
            Target(
                id=target.id,
                target_type=target.target_type,
                value=target.value,
                description=target.description,
                is_in_scope=target.is_in_scope,
                created_at=target.created_at
            ) for target in targets
        ]
        
        project_obj = Project(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            status=db_project.status,
            start_date=db_project.start_date,
            end_date=db_project.end_date,
            team_members=_safe_json_loads(db_project.team_members, []),
            targets=target_objects,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        )
        recent_projects.append(project_obj)
    
    return {
        "total_projects": total_projects,
        "active_projects": active_projects,
        "total_notes": total_notes,
        "recent_projects": recent_projects
    }

# Include the router in the main app
try:
    from .routers import keys as keys_router_module
    from .routers import payments as payments_router_module
    from .routers import auth as auth_router_module
    from .routers import ai as ai_router_module
    from .routers import tools as tools_router_module
except Exception:
    # Fallback for direct execution without package context
    import routers.keys as keys_router_module  # type: ignore
    import routers.payments as payments_router_module  # type: ignore
    import routers.auth as auth_router_module  # type: ignore
    import routers.ai as ai_router_module  # type: ignore
    import routers.tools as tools_router_module  # type: ignore
    import routers.vulnerabilities as vulnerabilities_router_module  # type: ignore

# Include routers
app.include_router(keys_router_module.router)
app.include_router(payments_router_module.router)
app.include_router(auth_router_module.router)
app.include_router(ai_router_module.router)
app.include_router(tools_router_module.router)
app.include_router(vulnerabilities_router_module.router)

app.include_router(api_router)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Emergent Pentest Suite API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

origins = os.getenv("CORS_ORIGINS", CORS_ORIGINS).split(',')

# Şimdi middleware'i bu dinamik 'origins' listesiyle yapılandır.
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=origins,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add rate limiting middleware (before security headers)
app.add_middleware(RateLimitMiddleware, default_limit=100, window_seconds=60)

# Add security headers middleware (after CORS middleware)
app.add_middleware(SecurityHeadersMiddleware)

# Mount static files for frontend
static_dir = ROOT_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Frontend routing - catch all routes for SPA
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve frontend files and handle SPA routing"""
    # Skip API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # Serve static files
    static_file_path = static_dir / full_path
    if static_file_path.exists() and static_file_path.is_file():
        return FileResponse(str(static_file_path))
    
    # For SPA, always serve index.html
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    
    # Fallback
    raise HTTPException(status_code=404, detail="File not found")

@app.on_event("shutdown")
async def shutdown_db_client():
    # SQLite doesn't need explicit connection closing
    pass