"""
seed_officers.py — Seed test officers into the users table
Run:  python seed_officers.py   (from the backend/ directory)
"""

import os
import sys
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("[ERROR] Set SUPABASE_URL and SUPABASE_KEY in .env first.")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
print("✅ Connected to Supabase\n")

OFFICERS = [
    {"name": "Sharma Vijay", "email": "sharma.vijay@gov.in", "ward": "Ward 1", "specialization": "water|sanitation"},
    {"name": "Priya Nair", "email": "priya.nair@gov.in", "ward": "Ward 2", "specialization": "roads|electricity"},
    {"name": "Rajesh Kumar", "email": "rajesh.kumar@gov.in", "ward": "Ward 3", "specialization": "water|health"},
    {"name": "Anita Das", "email": "anita.das@gov.in", "ward": "Ward 4", "specialization": "sanitation|general"},
    {"name": "Suresh Pillai", "email": "suresh.pillai@gov.in", "ward": "Ward 5", "specialization": "roads|water"},
    {"name": "Meera Krishnan", "email": "meera.krishnan@gov.in", "ward": "Ward 6", "specialization": "electricity|roads"},
    {"name": "Avinash Menon", "email": "avinash.menon@gov.in", "ward": "Ward 7", "specialization": "general|health"},
    {"name": "Deepa Mohan", "email": "deepa.mohan@gov.in", "ward": "Ward 8", "specialization": "water|roads"},
]

print("=" * 70)
print(f"Seeding {len(OFFICERS)} officers into 'users' table")
print("=" * 70 + "\n")

for i, officer in enumerate(OFFICERS, 1):
    try:
        # Hash password
        password_hash = hashlib.sha256(b"password123").hexdigest()
        
        # Insert officer
        result = supabase.table("users").insert({
            "email": officer["email"],
            "password_hash": password_hash,
            "role": "officer",
            "full_name": officer["name"],
            "phone": f"98765{4321:05d}",
            "ward": officer["ward"],
            "is_active": True
        }).execute()
        
        print(f"[{i}/{len(OFFICERS)}] ✅ {officer['name']:20} | {officer['ward']:15} | {officer['specialization']}")
        
    except Exception as e:
        print(f"[{i}/{len(OFFICERS)}] ❌ {officer['name']} - Error: {str(e)[:50]}")

print("\n" + "=" * 70)
print("✅ Officer seeding completed!")
print("=" * 70)
