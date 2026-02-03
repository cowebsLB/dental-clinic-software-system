"""Test script to verify .env file loading."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get project root
PROJECT_ROOT = Path(__file__).parent
env_path = PROJECT_ROOT / '.env'

print(f"Project root: {PROJECT_ROOT.absolute()}")
print(f".env file path: {env_path.absolute()}")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    print(f"\n.env file size: {env_path.stat().st_size} bytes")
    print("\nFirst 20 lines of .env file:")
    with open(env_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 20:
                print(f"  {i+1}: {line.rstrip()}")
            else:
                break

print("\nLoading .env file...")
load_dotenv(dotenv_path=env_path)

print("\nEnvironment variables:")
supabase_url = os.getenv('SUPABASE_URL', '')
supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '')

print(f"SUPABASE_URL: {supabase_url[:50]}..." if len(supabase_url) > 50 else f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_ANON_KEY: {supabase_anon_key[:30]}..." if len(supabase_anon_key) > 30 else f"SUPABASE_ANON_KEY: {supabase_anon_key}")

if not supabase_url:
    print("\nERROR: SUPABASE_URL is empty!")
if not supabase_anon_key:
    print("ERROR: SUPABASE_ANON_KEY is empty!")

if supabase_url and supabase_anon_key:
    print("\n[SUCCESS] Environment variables loaded successfully!")
else:
    print("\n[FAILED] Some environment variables are missing!")

