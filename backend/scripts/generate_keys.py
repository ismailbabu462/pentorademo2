#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime, timezone
from secrets import token_urlsafe
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
import asyncio


def generate_raw_key(length: int = 50) -> str:
    # token_urlsafe produces ~1.3 chars per byte; overshoot then trim
    key = token_urlsafe(length)
    return key[:length]


async def create_license_key(db: Session, tier: str, duration_days: int, *, created_for_user_id: str | None = None, store_raw: bool = False) -> str:
    from database import LicenseKey as DBLicenseKey
    
    raw_key = generate_raw_key(50)
    key_hash = bcrypt.hash(raw_key)
    
    db_key = DBLicenseKey(
        key_hash=key_hash,
        tier=tier,
        duration_days=duration_days,
        is_used=False,
        used_by_user_id=None,
        used_at=None,
        created_at=datetime.now(timezone.utc)
    )
    
    if created_for_user_id:
        db_key.created_for_user_id = created_for_user_id
    
    if store_raw:
        # Temporary raw storage to allow retrieval on success page
        db_key.raw_key = raw_key
    
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return raw_key


async def main():
    from database import SessionLocal
    
    parser = argparse.ArgumentParser(description="Generate license keys for PentoraSec")
    parser.add_argument("--tier", required=True, choices=["professional", "teams", "enterprise", "elite"], help="License tier")
    parser.add_argument("--duration", required=True, type=int, help="Duration in days")
    parser.add_argument("--count", required=True, type=int, help="Number of keys to generate")
    args = parser.parse_args()

    db = SessionLocal()

    print(f"Generating {args.count} keys for tier={args.tier}, duration={args.duration}d")
    print("Raw keys (store securely; not saved in DB):\n")
    for _ in range(args.count):
        raw_key = await create_license_key(db, args.tier, args.duration, store_raw=False)
        print(raw_key)

    db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(1)


