"""
Check what tables and columns exist in Supabase
"""
from supabase import create_client, Client

# Supabase credentials (same as app.py)
url = 'https://tocuqnqdewhqhbhkbplm.supabase.co'
key = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc'

supabase: Client = create_client(url, key)

print("✓ Connected to Supabase\n")

# Try to query predictions table
print("=" * 60)
print("Checking 'predictions' table:")
print("=" * 60)
try:
    result = supabase.table('predictions').select('*').limit(1).execute()
    if result.data:
        print(f"✓ Table exists with {len(result.data)} row(s)")
        print(f"Columns: {list(result.data[0].keys())}")
        print(f"Sample: {result.data[0]}")
    else:
        print("✓ Table exists but is empty")
        # Try to get schema by doing a select with limit 0
        result = supabase.table('predictions').select('*').limit(0).execute()
        print(f"Table structure: {result}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Checking 'user_predictions' table:")
print("=" * 60)
try:
    result = supabase.table('user_predictions').select('*').limit(1).execute()
    if result.data:
        print(f"✓ Table exists with {len(result.data)} row(s)")
        print(f"Columns: {list(result.data[0].keys())}")
        print(f"Sample: {result.data[0]}")
    else:
        print("✓ Table exists but is empty")
except Exception as e:
    print(f"✗ Table does not exist or error: {e}")

print("\n" + "=" * 60)
print("Testing direct table list (if possible):")
print("=" * 60)
# Supabase client doesn't have a direct list_tables method,
# but we can try PostgREST's root endpoint
try:
    # This won't work with the Python client, but let's try
    print("(Not available through Python client)")
except Exception as e:
    print(f"Error: {e}")
