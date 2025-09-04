from fastapi import APIRouter, HTTPException, Depends, Request, Header
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy.orm import Session
import hmac
import hashlib
import json
import os
try:
    # Prefer absolute import when running as a top-level app
    from routers.keys import get_current_user_id  # type: ignore
except Exception:
    # Fallback when running as a package
    from .keys import get_current_user_id  # type: ignore

from database import get_db, LicenseKey as DBLicenseKey

router = APIRouter(prefix="/api", tags=["payments"])


class MockPaymentRequest(BaseModel):
    tier: str
    duration_days: int


@router.post("/payments/mock-successful-payment")
async def mock_successful_payment(payload: MockPaymentRequest, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    if payload.tier not in {"professional", "teams", "enterprise", "elite"}:
        raise HTTPException(status_code=400, detail="Invalid tier")
    if payload.duration_days not in {30, 365}:
        raise HTTPException(status_code=400, detail="Invalid duration")

    try:
        from ..scripts.generate_keys import create_license_key
    except Exception:
        from scripts.generate_keys import create_license_key  # type: ignore

    raw_key = await create_license_key(
        db,
        tier=payload.tier,
        duration_days=payload.duration_days,
        created_for_user_id=user_id,
        store_raw=True,
    )

    # Update the license key with mock payment info
    license_key = db.query(DBLicenseKey).filter(DBLicenseKey.raw_key == raw_key).first()
    if license_key:
        license_key.created_at = datetime.now(timezone.utc)
        db.commit()

    return {"success": True, "message": "Mock payment successful, key generated."}


def verify_lemonsqueezy_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify Lemon Squeezy webhook signature"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False


@router.post("/webhooks/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None, alias="x-signature"),
    db: Session = Depends(get_db)
):
    """
    Handle Lemon Squeezy webhook events
    """
    try:
        # Get raw body first
        body = await request.body()
        print(f"Webhook received - Body length: {len(body)}")
        print(f"Webhook received - Headers: {dict(request.headers)}")
        print(f"Webhook received from: {request.client.host if hasattr(request.client, 'host') else 'unknown'}")
        
        # Get webhook secret from environment
        webhook_secret = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET")
        if not webhook_secret:
            print("WARNING: LEMONSQUEEZY_WEBHOOK_SECRET not configured, skipping signature verification")
        else:
            # Verify signature if secret is configured
            if x_signature and not verify_lemonsqueezy_signature(body, x_signature, webhook_secret):
                print(f"Invalid signature: {x_signature}")
                raise HTTPException(status_code=401, detail="Invalid signature")
            else:
                print("Signature verification passed or skipped")
        
        # Parse webhook data
        webhook_data = json.loads(body.decode('utf-8'))
        print(f"Webhook data: {json.dumps(webhook_data, indent=2)}")
        
        event_type = webhook_data.get('meta', {}).get('event_name')
        
        print(f"Lemon Squeezy webhook received: {event_type}")
        
        # Handle different event types
        if event_type in ['subscription_created', 'order_created']:
            print("Processing payment success...")
            await handle_payment_success(webhook_data, db)
        else:
            print(f"Unhandled event type: {event_type}")
        
        return {"status": "success"}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_payment_success(webhook_data: dict, db: Session):
    """
    Handle successful payment and create license key
    """
    try:
        # Extract user and plan information from webhook data
        data = webhook_data.get('data', {})
        attributes = data.get('attributes', {})
        
        # Get user email from webhook data
        user_email = attributes.get('user_email') or attributes.get('customer_email')
        if not user_email:
            print("No user email found in webhook data")
            return
        
        # Map Lemon Squeezy product to our tier
        product_id = attributes.get('product_id')
        tier_mapping = {
            'professional': 'professional',
            'teams': 'teams', 
            'enterprise': 'enterprise',
            'elite': 'elite'
        }
        
        # Default to professional if no mapping found
        tier = tier_mapping.get(str(product_id), 'professional')
        
        # Calculate duration (default to 30 days for monthly, 365 for yearly)
        variant_id = attributes.get('variant_id')
        duration_days = 365 if 'yearly' in str(variant_id).lower() else 30
        
        # Find user by email
        from database import User
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            print(f"User not found for email: {user_email}")
            return
        
        # Create license key
        try:
            from ..scripts.generate_keys import create_license_key
        except Exception:
            from scripts.generate_keys import create_license_key
        
        raw_key = await create_license_key(
            db,
            tier=tier,
            duration_days=duration_days,
            created_for_user_id=user.id,
            store_raw=True,
        )
        
        print(f"License key created for user {user_email}: {tier} tier, {duration_days} days")
        
    except Exception as e:
        print(f"Error handling payment success: {str(e)}")
        raise


