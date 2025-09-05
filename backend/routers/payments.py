import hashlib
import hmac
import json
import logging
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
try:
    # Prefer absolute import when running as a top-level app
    from routers.keys import get_current_user_id  # type: ignore
except Exception:
    # Fallback when running as a package
    from .keys import get_current_user_id  # type: ignore

from database import LicenseKey as DBLicenseKey
from database import get_db

router = APIRouter(prefix="/api", tags=["payments"])


class MockPaymentRequest(BaseModel):
    tier: str
    duration_days: int


@router.post("/payments/mock-successful-payment")
async def mock_successful_payment(
    payload: MockPaymentRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
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
            secret.encode("utf-8"), payload, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False


@router.post("/webhooks/lemonsqueezy")
async def lemonsqueezy_webhook(
    request: Request,
    x_signature: str = Header(None, alias="x-signature"),
    db: Session = Depends(get_db),
):
    """
    Handle Lemon Squeezy webhook events
    """
    try:
        # Get raw body first
        body = await request.body()

        # Log webhook details (sanitized for security)
        client_ip = (
            getattr(request.client, "host", "unknown") if request.client else "unknown"
        )
        logger.info(f"Webhook received - Body length: {len(body)}, From: {client_ip}")

        # Get webhook secret from configuration
        from config import LEMONSQUEEZY_WEBHOOK_SECRET

        webhook_secret = LEMONSQUEEZY_WEBHOOK_SECRET
        if not webhook_secret:
            logger.warning(
                "LEMONSQUEEZY_WEBHOOK_SECRET not configured, skipping signature verification"
            )
        else:
            # Verify signature if secret is configured
            if x_signature and not verify_lemonsqueezy_signature(
                body, x_signature, webhook_secret
            ):
                logger.error("Invalid webhook signature")
                raise HTTPException(status_code=401, detail="Invalid signature")
            else:
                logger.info("Signature verification passed or skipped")

        # Parse webhook data with size limit
        from config import MAX_REQUEST_SIZE

        if len(body) > MAX_REQUEST_SIZE:
            raise HTTPException(status_code=413, detail="Payload too large")

        webhook_data = json.loads(body.decode("utf-8"))
        event_type = webhook_data.get("meta", {}).get("event_name")

        logger.info(f"Lemon Squeezy webhook received: {event_type}")

        # Handle different event types
        if event_type in ["subscription_created", "order_created"]:
            logger.info("Processing payment success...")
            await handle_payment_success(webhook_data, db)
        else:
            logger.info(f"Unhandled event type: {event_type}")

        return {"status": "success"}

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        # Rollback any database changes
        try:
            db.rollback()
        except:
            pass
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def handle_payment_success(webhook_data: dict, db: Session):
    """
    Handle successful payment and create license key
    """
    try:
        # Extract user and plan information from webhook data
        data = webhook_data.get("data", {})
        attributes = data.get("attributes", {})

        # Get user email from webhook data
        user_email = attributes.get("user_email") or attributes.get("customer_email")
        if not user_email:
            logger.warning("No user email found in webhook data")
            return

        # Validate email format
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, user_email):
            logger.error(f"Invalid email format: {user_email}")
            return

        # Map Lemon Squeezy product to our tier
        product_id = attributes.get("product_id")
        tier_mapping = {
            "professional": "professional",
            "teams": "teams",
            "enterprise": "enterprise",
            "elite": "elite",
        }

        # Default to professional if no mapping found
        tier = tier_mapping.get(str(product_id), "professional")

        # Calculate duration (default to 30 days for monthly, 365 for yearly)
        variant_id = attributes.get("variant_id")
        duration_days = 365 if "yearly" in str(variant_id).lower() else 30

        # Validate duration
        if duration_days not in [30, 365]:
            duration_days = 30

        # Find user by email
        from database import User

        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            logger.warning(f"User not found for email: {user_email}")
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

        logger.info(
            f"License key created for user {user_email}: {tier} tier, {duration_days} days"
        )

    except Exception as e:
        logger.error(f"Error handling payment success: {str(e)}")
        # Rollback database changes
        try:
            db.rollback()
        except:
            pass
        raise
