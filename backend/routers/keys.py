from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
import logging

from database import get_db, LicenseKey as DBLicenseKey, User as DBUser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/keys", tags=["keys"])


class ActivateRequest(BaseModel):
    key: str


async def get_current_user_id(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = authorization.split(" ", 1)[1]
    
    try:
        from jose import JWTError, jwt
        from config import JWT_SECRET_KEY, JWT_ALGORITHM
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # SECURITY: Verify user exists in database
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/activate")
async def activate_key(payload: ActivateRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    try:
        incoming_key = payload.key.strip()
        logger.debug(f"License Key Activation: Received key: {incoming_key[:10]}...")
        logger.debug(f"License Key Activation: Key length: {len(incoming_key)}")
        logger.debug(f"License Key Activation: User ID: {user_id}")
        
        if not incoming_key or len(incoming_key) < 20:
            logger.debug(f"License Key Activation: Invalid key format - length: {len(incoming_key)}")
            raise HTTPException(status_code=400, detail="Invalid key format")

        # Find all unused keys
        unused_keys = db.query(DBLicenseKey).filter(DBLicenseKey.is_used == False).all()
        logger.debug(f"License Key Activation: Found {len(unused_keys)} unused keys")
        matched_key = None
        
        for key in unused_keys:
            if key.key_hash and bcrypt.verify(incoming_key, key.key_hash):
                matched_key = key
                break

        if not matched_key:
            logger.debug("License Key Activation: No matching key found")
            raise HTTPException(status_code=400, detail="Invalid or previously used key")

        tier = matched_key.tier or "professional"
        duration_days = matched_key.duration_days or 30
        now = datetime.now(timezone.utc)
        valid_until = now + timedelta(days=duration_days)

        # Mark key as used
        matched_key.is_used = True
        matched_key.used_by_user_id = user_id
        matched_key.used_at = now

        # Update user membership
        user = db.query(DBUser).filter(DBUser.id == user_id).first()
        if user:
            user.tier = tier
            user.subscription_valid_until = valid_until
        else:
            raise HTTPException(status_code=404, detail="User not found")

        db.commit()

        # Create new JWT token with updated tier information
        from jose import jwt
        from config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_ACCESS_TOKEN_EXPIRE_DAYS
        
        # SECURITY: Create device-specific token
        device_id = str(uuid.uuid4())
        token_data = {
            "sub": user_id,
            "device_id": device_id,
            "exp": datetime.now(timezone.utc) + timedelta(days=JWT_ACCESS_TOKEN_EXPIRE_DAYS)
        }
        new_token = jwt.encode(token_data, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        return {
            "message": "Activation successful", 
            "tier": tier, 
            "valid_until": valid_until.isoformat(),
            "token": new_token
        }
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        import logging
        logging.error(f"Key activation error for user {user_id}: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred during key activation"
        )


@router.post("/create-test-key")
async def create_test_key(tier: str = "professional", db: Session = Depends(get_db)):
    """Create a test license key for development"""
    from passlib.hash import bcrypt
    from datetime import datetime, timezone
    
    # Validate tier
    valid_tiers = ["professional", "teams", "enterprise", "elite"]
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"Invalid tier. Must be one of: {valid_tiers}")
    
    # Create a test key based on tier
    test_key = f"test_{tier}_12345678901234567890"  # 30+ characters
    key_hash = bcrypt.hash(test_key)
    
    # Create license key record
    license_key = DBLicenseKey(
        key_hash=key_hash,
        tier=tier,
        duration_days=30,
        is_used=False,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(license_key)
    db.commit()
    
    return {"message": "Test key created", "key": test_key, "tier": tier}

@router.get("/get-latest-key-for-user")
async def get_latest_key_for_user(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    # SECURITY: Find most recent unused key created for this specific user
    key = db.query(DBLicenseKey).filter(
        DBLicenseKey.is_used == False,
        DBLicenseKey.created_for_user_id == user_id  # SECURITY: Ensure key belongs to requesting user
    ).order_by(DBLicenseKey.created_at.desc()).first()
    
    if not key:
        raise HTTPException(status_code=404, detail="No pending license key found for user")

    # SECURITY: Only return raw key if it exists and belongs to the user
    if not key.raw_key:
        raise HTTPException(status_code=501, detail="Raw key retrieval not implemented")

    # SECURITY: Double-check that the key belongs to the requesting user
    if key.created_for_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied: Key does not belong to user")

    return {"key": key.raw_key}


