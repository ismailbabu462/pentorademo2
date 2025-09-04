from fastapi import Depends, HTTPException, Path, Header
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import os
from typing import Optional
import asyncio
import json

from database import get_db

# User model for type hints
class User:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.username = data.get('username')
        self.email = data.get('email')
        self.tier = data.get('tier', 'essential')
        self.subscription_valid_until = data.get('subscription_valid_until')
        self.last_tool_run_at = data.get('last_tool_run_at')

# Tier limits configuration
TIER_LIMITS = {
    'essential': {
        'max_projects': 3,
        'tool_delay_seconds': 5,
        'allowed_tools': {'subfinder', 'nmap', 'gobuster'}
    },
    'professional': {
        'max_projects': 10,
        'tool_delay_seconds': 3,
        'allowed_tools': 'all'  # All tools allowed
    },
    'teams': {
        'max_projects': None,  # Unlimited
        'tool_delay_seconds': 0,
        'allowed_tools': 'all'
    },
    'enterprise': {
        'max_projects': None,  # Unlimited
        'tool_delay_seconds': 0,
        'allowed_tools': 'all'
    },
    'elite': {
        'max_projects': None,  # Unlimited
        'tool_delay_seconds': 0,
        'allowed_tools': 'all'
    }
}

async def get_current_active_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current active user from JWT token and database
    """
    # SECURITY: Remove debug logging in production
    if os.getenv("DEBUG", "false").lower() == "true":
        print(f"🔐 Auth Debug: Authorization header present: {bool(authorization)}")
    
    if not authorization or not authorization.startswith("Bearer "):
        if os.getenv("DEBUG", "false").lower() == "true":
            print("❌ Auth Debug: No valid authorization header")
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = authorization.split(" ", 1)[1]
    if os.getenv("DEBUG", "false").lower() == "true":
        print(f"🔐 Auth Debug: Token length: {len(token)}")
    
    try:
        from jose import JWTError, jwt
        from config import JWT_SECRET_KEY, JWT_ALGORITHM
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            if os.getenv("DEBUG", "false").lower() == "true":
                print("❌ Auth Debug: No user ID in token")
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user from database
        from database import User as DBUser
        user_data = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user_data:
            if os.getenv("DEBUG", "false").lower() == "true":
                print(f"❌ Auth Debug: User not found in database")
            raise HTTPException(status_code=401, detail="User not found")
        
        if os.getenv("DEBUG", "false").lower() == "true":
            safe_username = str(user_data.username)[:20] + "..." if len(str(user_data.username)) > 20 else str(user_data.username)
            print(f"✅ Auth Debug: User authenticated successfully: {safe_username}")
        return User({
            'id': user_data.id,
            'username': user_data.username,
            'email': user_data.email,
            'tier': user_data.tier,
            'subscription_valid_until': user_data.subscription_valid_until,
            'last_tool_run_at': user_data.last_tool_run_at
        })
        
    except JWTError as e:
        if os.getenv("DEBUG", "false").lower() == "true":
            print(f"❌ Auth Debug: JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def check_project_limit(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Check if user has reached their project limit based on tier
    """
    tier = current_user.tier
    limits = TIER_LIMITS.get(tier, TIER_LIMITS['essential'])
    max_projects = limits['max_projects']
    
    # Unlimited projects for teams and above
    if max_projects is None:
        return {"user": current_user, "db": db}
    
    # Count user's projects
    from database import Project as DBProject
    project_count = db.query(DBProject).filter(DBProject.user_id == current_user.id).count()
    
    if project_count >= max_projects:
        raise HTTPException(
            status_code=403, 
            detail=f"Proje limitinize ulaştınız. Lütfen planınızı yükseltin. (Mevcut: {project_count}/{max_projects})"
        )
    
    return {"user": current_user, "db": db}

async def check_tool_permission(
    tool_name: str,
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Check if user has permission to use the specified tool based on tier
    """
    tier = current_user.tier
    limits = TIER_LIMITS.get(tier, TIER_LIMITS['essential'])
    allowed_tools = limits['allowed_tools']
    
    # All tools allowed for professional and above
    if allowed_tools == 'all':
        return {"user": current_user, "tool_name": tool_name}
    
    # Check if tool is in allowed list for essential tier
    if tool_name not in allowed_tools:
        raise HTTPException(
            status_code=403,
            detail="Bu aracı kullanmak için Professional veya üstü bir plana sahip olmalısınız."
        )
    
    return {"user": current_user, "tool_name": tool_name}

# Individual tool permission checkers
async def check_subfinder_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await check_tool_permission("subfinder", current_user)

async def check_amass_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await check_tool_permission("amass", current_user)

async def check_nmap_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await check_tool_permission("nmap", current_user)

async def check_nuclei_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await check_tool_permission("nuclei", current_user)

async def check_ffuf_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await check_tool_permission("ffuf", current_user)

async def check_gobuster_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    return await check_tool_permission("gobuster", current_user)

async def check_tool_delay(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> dict:
    """
    Check if user has waited long enough since last tool run based on tier
    """
    tier = current_user.tier
    limits = TIER_LIMITS.get(tier, TIER_LIMITS['essential'])
    required_delay = limits['tool_delay_seconds']
    
    # No delay for teams and above
    if required_delay == 0:
        return {"user": current_user, "db": db}
    
    now = datetime.now(timezone.utc)
    last_run = current_user.last_tool_run_at
    
    if last_run:
        # Handle both string and datetime objects
        if isinstance(last_run, str):
            last_run = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
        
        # Calculate time difference (ensure both are timezone-aware)
        if last_run.tzinfo is None:
            last_run = last_run.replace(tzinfo=timezone.utc)
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        
        time_diff = (now - last_run).total_seconds()
        
        if time_diff < required_delay:
            remaining_time = required_delay - time_diff
            raise HTTPException(
                status_code=429,
                detail=f"Araçları kullanmak için {remaining_time:.1f} saniye daha beklemelisiniz."
            )
    
    # Update last_tool_run_at in database
    from database import User as DBUser
    user = db.query(DBUser).filter(DBUser.id == current_user.id).first()
    if user:
        user.last_tool_run_at = now
        db.commit()
    
    return {"user": current_user, "db": db}

async def check_collaboration_permission(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Check if user has permission to use collaboration features based on tier
    """
    if current_user.tier == 'essential':
        raise HTTPException(
            status_code=403,
            detail="İşbirliği özellikleri premium bir özelliktir. Kullanıcı davet etmek için planınızı yükseltin."
        )
    
    return {"user": current_user}

async def check_subscription_active(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    Check if user's subscription is still active
    """
    if current_user.tier == 'essential':
        return {"user": current_user}
    
    # For professional and above, allow access even without subscription_valid_until
    # This is for demo purposes
    if not current_user.subscription_valid_until:
        return {"user": current_user}
    
    expiry_date = current_user.subscription_valid_until
    if isinstance(expiry_date, str):
        expiry_date = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
    
    # Ensure both datetimes are timezone-aware
    if expiry_date.tzinfo is None:
        expiry_date = expiry_date.replace(tzinfo=timezone.utc)
    
    now = datetime.now(timezone.utc)
    if expiry_date <= now:
        raise HTTPException(
            status_code=403,
            detail="Aboneliğinizin süresi dolmuş. Lütfen planınızı yenileyin."
        )
    
    return {"user": current_user}

# Combined dependencies for common use cases
async def check_project_creation_permissions(
    auth_data: dict = Depends(check_project_limit)
) -> dict:
    """Combined check for project creation (subscription + limits)"""
    return auth_data

async def check_collaboration_permissions(
    auth_data: dict = Depends(check_collaboration_permission)
) -> dict:
    """Combined check for collaboration features (permissions)"""
    return auth_data

# Combined dependencies for tool execution
async def check_subfinder_execution_permissions(
    permission_data: dict = Depends(check_subfinder_permission),
    delay_data: dict = Depends(check_tool_delay),
    subscription_data: dict = Depends(check_subscription_active)
) -> dict:
    """Combined check for subfinder execution (permissions + delay + subscription)"""
    return {
        "user": permission_data["user"],
        "tool_name": permission_data["tool_name"],
        "db": delay_data["db"]
    }

async def check_amass_execution_permissions(
    permission_data: dict = Depends(check_amass_permission),
    delay_data: dict = Depends(check_tool_delay),
    subscription_data: dict = Depends(check_subscription_active)
) -> dict:
    """Combined check for amass execution (permissions + delay + subscription)"""
    return {
        "user": permission_data["user"],
        "tool_name": permission_data["tool_name"],
        "db": delay_data["db"]
    }

async def check_nmap_execution_permissions(
    permission_data: dict = Depends(check_nmap_permission),
    delay_data: dict = Depends(check_tool_delay),
    subscription_data: dict = Depends(check_subscription_active)
) -> dict:
    """Combined check for nmap execution (permissions + delay + subscription)"""
    return {
        "user": permission_data["user"],
        "tool_name": permission_data["tool_name"],
        "db": delay_data["db"]
    }

async def check_nuclei_execution_permissions(
    permission_data: dict = Depends(check_nuclei_permission),
    delay_data: dict = Depends(check_tool_delay),
    subscription_data: dict = Depends(check_subscription_active)
) -> dict:
    """Combined check for nuclei execution (permissions + delay + subscription)"""
    return {
        "user": permission_data["user"],
        "tool_name": permission_data["tool_name"],
        "db": delay_data["db"]
    }

async def check_ffuf_execution_permissions(
    permission_data: dict = Depends(check_ffuf_permission),
    delay_data: dict = Depends(check_tool_delay),
    subscription_data: dict = Depends(check_subscription_active)
) -> dict:
    """Combined check for ffuf execution (permissions + delay + subscription)"""
    return {
        "user": permission_data["user"],
        "tool_name": permission_data["tool_name"],
        "db": delay_data["db"]
    }

async def check_gobuster_execution_permissions(
    permission_data: dict = Depends(check_gobuster_permission),
    delay_data: dict = Depends(check_tool_delay),
    subscription_data: dict = Depends(check_subscription_active)
) -> dict:
    """Combined check for gobuster execution (permissions + delay + subscription)"""
    return {
        "user": permission_data["user"],
        "tool_name": permission_data["tool_name"],
        "db": delay_data["db"]
    }
