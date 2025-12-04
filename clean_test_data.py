"""
Clean up test data before running tests
Deletes all predictions for both test accounts
"""
from supabase import create_client

SUPABASE_URL = "https://tocuqnqdewhqhbhkbplm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc"

print("\n" + "="*80)
print("🧹 CLEANING TEST DATA")
print("="*80)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Login Account 1
auth1 = supabase.auth.sign_in_with_password({"email": "dazrini@gmail.com", "password": "gummybear"})
user1_id = auth1.user.id
token1 = auth1.session.access_token

print(f"\nAccount 1: {user1_id}")

# Delete Account 1's predictions
sb1 = create_client(SUPABASE_URL, SUPABASE_KEY)
sb1.postgrest.auth(token1)
result1 = sb1.table('predictions').delete().eq('user_id', user1_id).execute()
print(f"Deleted {len(result1.data) if result1.data else 0} predictions for Account 1")

# Login Account 2
auth2 = supabase.auth.sign_in_with_password({"email": "test2@gmail.com", "password": "password"})
user2_id = auth2.user.id
token2 = auth2.session.access_token

print(f"\nAccount 2: {user2_id}")

# Delete Account 2's predictions
sb2 = create_client(SUPABASE_URL, SUPABASE_KEY)
sb2.postgrest.auth(token2)
result2 = sb2.table('predictions').delete().eq('user_id', user2_id).execute()
print(f"Deleted {len(result2.data) if result2.data else 0} predictions for Account 2")

print("\n" + "="*80)
print("✅ TEST DATA CLEANED")
print("="*80)
