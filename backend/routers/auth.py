from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from database import get_db, User as DBUser

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT settings
from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    username: str
    email: str


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    tier: str
    subscription_valid_until: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = authorization.split(" ", 1)[1]
    payload = verify_token(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "tier": user.tier,
        "subscription_valid_until": user.subscription_valid_until,
        "last_tool_run_at": user.last_tool_run_at,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    
    db_user = DBUser(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        tier="essential",
        subscription_valid_until=None,
        last_tool_run_at=None,
        created_at=now,
        updated_at=now
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user_id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            tier=db_user.tier,
            subscription_valid_until=db_user.subscription_valid_until.isoformat() if db_user.subscription_valid_until else None,
            created_at=db_user.created_at.isoformat()
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserCreate, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
    if not user:
        # Auto-register if user doesn't exist
        return await register(user_data, db)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            tier=user.tier,
            subscription_valid_until=user.subscription_valid_until.isoformat() if user.subscription_valid_until else None,
            created_at=user.created_at.isoformat()
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    # Ensure datetime fields are properly serialized
    user_data = current_user.copy()
    if 'created_at' in user_data and user_data['created_at']:
        if hasattr(user_data['created_at'], 'isoformat'):
            user_data['created_at'] = user_data['created_at'].isoformat()
    if 'subscription_valid_until' in user_data and user_data['subscription_valid_until']:
        if hasattr(user_data['subscription_valid_until'], 'isoformat'):
            user_data['subscription_valid_until'] = user_data['subscription_valid_until'].isoformat()
    
    return UserResponse(**user_data)


@router.post("/auto-login", response_model=TokenResponse)
async def auto_login(db: Session = Depends(get_db)):
    """Auto-login endpoint for development - creates a user if none exists"""
    # Check if any user exists
    existing_user = db.query(DBUser).first()
    
    if existing_user:
        # Use existing user
        access_token = create_access_token(data={"sub": existing_user.id})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=existing_user.id,
                username=existing_user.username,
                email=existing_user.email,
                tier=existing_user.tier,
                subscription_valid_until=existing_user.subscription_valid_until.isoformat() if existing_user.subscription_valid_until else None,
                created_at=existing_user.created_at.isoformat()
            )
        )
    else:
        # Create a default user
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        db_user = DBUser(
            id=user_id,
            username="Demo User",
            email="demo@example.com",
            tier="essential",
            subscription_valid_until=None,
            last_tool_run_at=None,
            created_at=now,
            updated_at=now
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        access_token = create_access_token(data={"sub": user_id})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                tier=db_user.tier,
                subscription_valid_until=db_user.subscription_valid_until.isoformat() if db_user.subscription_valid_until else None,
                created_at=db_user.created_at.isoformat()
            )
        )
