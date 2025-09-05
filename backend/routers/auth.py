import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Device as DBDevice
from database import User as DBUser
from database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT settings
from config import JWT_ACCESS_TOKEN_EXPIRE_DAYS, JWT_ALGORITHM, JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    username: str
    email: str


class DeviceConnectRequest(BaseModel):
    device_fingerprint: str  # Browser fingerprint
    device_name: Optional[str] = "Web Browser"
    device_type: Optional[str] = "web"


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


def create_device_specific_jwt(
    user_id: str,
    device_id: str,
    device_secret: str,
    expires_delta: Optional[timedelta] = None,
):
    """Create JWT token using device-specific secret key"""
    to_encode = {
        "sub": user_id,
        "device_id": device_id,
        "iat": datetime.now(timezone.utc),
    }

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=JWT_ACCESS_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, device_secret, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_or_create_device_for_fingerprint(
    device_fingerprint: str,
    device_name: str,
    device_type: str,
    user_id: str,
    db: Session,
) -> DBDevice:
    """Get existing device by fingerprint or create new one"""
    print(f"Looking for device: fingerprint={device_fingerprint}, user_id={user_id}")

    # First try to find existing device by fingerprint
    existing_device = (
        db.query(DBDevice)
        .filter(
            DBDevice.device_id == device_fingerprint,
            DBDevice.user_id == user_id,
            DBDevice.is_active == True,
        )
        .first()
    )

    if existing_device:
        print(f"Found existing device: {existing_device.id}")
        # Update last used timestamp
        existing_device.last_used_at = datetime.now(timezone.utc)
        db.commit()
        return existing_device

    print("Creating new device...")
    # Create new device if not found
    device_secret = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)

    new_device = DBDevice(
        device_id=device_fingerprint,  # Use fingerprint as device_id
        device_name=device_name,
        device_type=device_type,
        jwt_secret_key=device_secret,
        user_id=user_id,
        is_active=True,
        last_used_at=now,
        created_at=now,
        updated_at=now,
    )

    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    print(f"Created new device: {new_device.id}")
    return new_device


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    device_id: Optional[str] = None,
):
    """Legacy function - use create_device_specific_jwt instead"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=JWT_ACCESS_TOKEN_EXPIRE_DAYS
        )

    # SECURITY: Add device-specific information to token
    if device_id:
        to_encode.update({"device_id": device_id})
    else:
        # Generate a device ID if not provided
        device_id = str(uuid.uuid4())
        to_encode.update({"device_id": device_id})

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_device_token(token: str, db: Session) -> dict:
    """Verify JWT token using device-specific secret"""
    try:
        print(f"Verifying token: {token[:50]}...")

        # First decode without verification to get device_id
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        device_id = unverified_payload.get("device_id")
        user_id = unverified_payload.get("sub")

        print(f"Token payload: device_id={device_id}, user_id={user_id}")

        if not device_id or not user_id:
            print("Missing device_id or user_id in token")
            raise HTTPException(status_code=401, detail="Invalid token format")

        # Get device and its secret key
        device = (
            db.query(DBDevice)
            .filter(
                DBDevice.device_id == device_id,
                DBDevice.user_id == user_id,
                DBDevice.is_active == True,
            )
            .first()
        )

        print(f"Found device: {device}")

        if not device:
            print("Device not found or inactive")
            raise HTTPException(status_code=401, detail="Device not found or inactive")

        # Verify token with device-specific secret
        payload = jwt.decode(token, device.jwt_secret_key, algorithms=[JWT_ALGORITHM])

        # Update last used timestamp
        device.last_used_at = datetime.now(timezone.utc)
        db.commit()

        print("Token verification successful")
        return payload
    except JWTError as e:
        print(f"JWT Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(status_code=401, detail="Token verification failed")


def verify_token(token: str) -> dict:
    """Legacy function - use verify_device_token instead"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    authorization: Optional[str] = Header(None), db: Session = Depends(get_db)
) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")

    token = authorization.split(" ", 1)[1]

    try:
        # Use device-specific token verification
        payload = verify_device_token(token, db)
        user_id = payload.get("sub")
        device_id = payload.get("device_id")

        if not user_id or not device_id:
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
            "updated_at": user.updated_at,
            "device_id": device_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token verification failed")


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
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
            updated_at=now,
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # SECURITY: Create device-specific access token
        device_id = str(uuid.uuid4())
        device_secret = secrets.token_urlsafe(32)  # Generate device-specific secret

        # Create device record
        device = DBDevice(
            device_id=device_id,
            device_name="Web Browser",
            device_type="web",
            jwt_secret_key=device_secret,
            user_id=user_id,
            is_active=True,
            last_used_at=now,
            created_at=now,
            updated_at=now,
        )

        db.add(device)
        db.commit()

        # Create device-specific JWT token
        access_token = create_device_specific_jwt(user_id, device_id, device_secret)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                tier=db_user.tier,
                subscription_valid_until=(
                    db_user.subscription_valid_until.isoformat()
                    if db_user.subscription_valid_until
                    else None
                ),
                created_at=db_user.created_at.isoformat(),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        import logging

        logging.error(f"Registration error: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred during registration",
        )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        # Find user by email
        user = db.query(DBUser).filter(DBUser.email == user_data.email).first()
        if not user:
            # Auto-register if user doesn't exist
            return await register(user_data, db)

        # SECURITY: Create device-specific access token
        device_id = str(uuid.uuid4())
        device_secret = secrets.token_urlsafe(32)  # Generate device-specific secret
        now = datetime.now(timezone.utc)

        # Create device record
        device = DBDevice(
            device_id=device_id,
            device_name="Web Browser",
            device_type="web",
            jwt_secret_key=device_secret,
            user_id=user.id,
            is_active=True,
            last_used_at=now,
            created_at=now,
            updated_at=now,
        )

        db.add(device)
        db.commit()

        # Create device-specific JWT token
        access_token = create_device_specific_jwt(user.id, device_id, device_secret)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                tier=user.tier,
                subscription_valid_until=(
                    user.subscription_valid_until.isoformat()
                    if user.subscription_valid_until
                    else None
                ),
                created_at=user.created_at.isoformat(),
            ),
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log error internally, don't expose details
        import logging

        logging.error(f"Login error: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500, detail="An internal server error occurred during login"
        )


@router.post("/auto-connect", response_model=TokenResponse)
async def auto_connect(
    device_request: DeviceConnectRequest, db: Session = Depends(get_db)
):
    """
    Otomatik bağlantı endpoint'i - siteye her girişte cihaza özel token üretir
    Login sistemi olmadığı için bu endpoint kullanılacak
    Aynı cihazdan tekrar girişte eski verileri gösterir
    """
    try:
        print(f"Auto-connect request: {device_request}")

        # Check if any user exists
        existing_user = db.query(DBUser).first()
        print(f"Existing user: {existing_user}")

        if existing_user:
            # Use existing user - get or create device for this fingerprint
            device = get_or_create_device_for_fingerprint(
                device_request.device_fingerprint,
                device_request.device_name,
                device_request.device_type,
                existing_user.id,
                db,
            )

            access_token = create_device_specific_jwt(
                existing_user.id, device.device_id, device.jwt_secret_key
            )
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=existing_user.id,
                    username=existing_user.username,
                    email=existing_user.email,
                    tier=existing_user.tier,
                    subscription_valid_until=(
                        existing_user.subscription_valid_until.isoformat()
                        if existing_user.subscription_valid_until
                        else None
                    ),
                    created_at=existing_user.created_at.isoformat(),
                ),
            )
        else:
            # Create a default user for first-time visitors
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
                updated_at=now,
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            # Create device for new user
            device = get_or_create_device_for_fingerprint(
                device_request.device_fingerprint,
                device_request.device_name,
                device_request.device_type,
                user_id,
                db,
            )

            access_token = create_device_specific_jwt(
                user_id, device.device_id, device.jwt_secret_key
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    tier=db_user.tier,
                    subscription_valid_until=(
                        db_user.subscription_valid_until.isoformat()
                        if db_user.subscription_valid_until
                        else None
                    ),
                    created_at=db_user.created_at.isoformat(),
                ),
            )
    except Exception as e:
        # Log error internally, don't expose details
        import logging

        logging.error(f"Auto-connect error: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred during auto-connect",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    try:
        # Ensure datetime fields are properly serialized
        user_data = current_user.copy()
        if "created_at" in user_data and user_data["created_at"]:
            if hasattr(user_data["created_at"], "isoformat"):
                user_data["created_at"] = user_data["created_at"].isoformat()
        if (
            "subscription_valid_until" in user_data
            and user_data["subscription_valid_until"]
        ):
            if hasattr(user_data["subscription_valid_until"], "isoformat"):
                user_data["subscription_valid_until"] = user_data[
                    "subscription_valid_until"
                ].isoformat()

        # Remove device_id from response (internal use only)
        user_data.pop("device_id", None)

        return UserResponse(**user_data)
    except Exception as e:
        # Log error internally, don't expose details
        import logging

        logging.error(f"Get user info error: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")


@router.post("/auto-login", response_model=TokenResponse)
async def auto_login(db: Session = Depends(get_db)):
    """Auto-login endpoint for development - creates a user if none exists"""
    try:
        # Check if any user exists
        existing_user = db.query(DBUser).first()

        if existing_user:
            # Use existing user - create new device
            device_id = str(uuid.uuid4())
            device_secret = secrets.token_urlsafe(32)
            now = datetime.now(timezone.utc)

            device = DBDevice(
                device_id=device_id,
                device_name="Web Browser",
                device_type="web",
                jwt_secret_key=device_secret,
                user_id=existing_user.id,
                is_active=True,
                last_used_at=now,
                created_at=now,
                updated_at=now,
            )

            db.add(device)
            db.commit()

            access_token = create_device_specific_jwt(
                existing_user.id, device_id, device_secret
            )
            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=existing_user.id,
                    username=existing_user.username,
                    email=existing_user.email,
                    tier=existing_user.tier,
                    subscription_valid_until=(
                        existing_user.subscription_valid_until.isoformat()
                        if existing_user.subscription_valid_until
                        else None
                    ),
                    created_at=existing_user.created_at.isoformat(),
                ),
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
                updated_at=now,
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            # Create device for new user
            device_id = str(uuid.uuid4())
            device_secret = secrets.token_urlsafe(32)

            device = DBDevice(
                device_id=device_id,
                device_name="Web Browser",
                device_type="web",
                jwt_secret_key=device_secret,
                user_id=user_id,
                is_active=True,
                last_used_at=now,
                created_at=now,
                updated_at=now,
            )

            db.add(device)
            db.commit()

            access_token = create_device_specific_jwt(user_id, device_id, device_secret)

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=UserResponse(
                    id=db_user.id,
                    username=db_user.username,
                    email=db_user.email,
                    tier=db_user.tier,
                    subscription_valid_until=(
                        db_user.subscription_valid_until.isoformat()
                        if db_user.subscription_valid_until
                        else None
                    ),
                    created_at=db_user.created_at.isoformat(),
                ),
            )
    except Exception as e:
        # Log error internally, don't expose details
        import logging

        logging.error(f"Auto-login error: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred during auto-login",
        )
