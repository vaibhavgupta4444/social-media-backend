"""
Quick script to test web push notification setup
Run this with: python test_push.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("WEB PUSH CONFIGURATION CHECK")
print("=" * 60)

vapid_public = os.getenv("VAPID_PUBLIC_KEY")
vapid_private = os.getenv("VAPID_PRIVATE_KEY")
vapid_subject = os.getenv("VAPID_SUBJECT")

print(f"\n✓ VAPID_PUBLIC_KEY: {'SET ✓' if vapid_public else 'MISSING ✗'}")
if vapid_public:
    print(f"  {vapid_public[:30]}...")

print(f"\n✓ VAPID_PRIVATE_KEY: {'SET ✓' if vapid_private else 'MISSING ✗'}")
if vapid_private:
    print(f"  {vapid_private[:30]}...")

print(f"\n✓ VAPID_SUBJECT: {vapid_subject if vapid_subject else 'MISSING ✗'}")

print("\n" + "=" * 60)

if not vapid_public or not vapid_private:
    print("❌ VAPID keys are missing!")
    print("\nTo fix:")
    print("1. Run: vapid --gen")
    print("2. Add keys to .env file")
    print("3. Restart the server")
else:
    print("✅ VAPID configuration looks good!")
    print("\nNow check if user has subscriptions:")
    print("  GET /vapid/debug")

print("=" * 60)
