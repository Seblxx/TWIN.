"""
Clean up test predictions before running tests
"""
import os
from supabase import create_client

# Supabase credentials
SUPABASE_URL = "https://tocuqnqdewhqhbhkbplm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc"

# Test accounts (match test_backend_comprehensive.py)
ACCOUNT1_EMAIL = "dazrini@gmail.com"
ACCOUNT1_PASSWORD = "gummybear"
ACCOUNT2_EMAIL = "test2@gmail.com"
ACCOUNT2_PASSWORD = "password"

def main():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 80)
    print("🧹 CLEANING TEST DATA")
    print("=" * 80)
    
    # Login Account 1
    print("\n[1] Login Account 1...")
    try:
        auth1 = supabase.auth.sign_in_with_password({
            "email": ACCOUNT1_EMAIL,
            "password": ACCOUNT1_PASSWORD
        })
        user_id_1 = auth1.user.id
        print(f"✅ Account 1 user_id: {user_id_1}")
        
        # Delete all predictions for Account 1
        resp = supabase.table('predictions').delete().eq('user_id', user_id_1).execute()
        print(f"✅ Deleted {len(resp.data)} predictions for Account 1")
    except Exception as e:
        print(f"❌ Error cleaning Account 1: {e}")
    
    # Login Account 2
    print("\n[2] Login Account 2...")
    try:
        auth2 = supabase.auth.sign_in_with_password({
            "email": ACCOUNT2_EMAIL,
            "password": ACCOUNT2_PASSWORD
        })
        user_id_2 = auth2.user.id
        print(f"✅ Account 2 user_id: {user_id_2}")
        
        # Delete all predictions for Account 2
        resp = supabase.table('predictions').delete().eq('user_id', user_id_2).execute()
        print(f"✅ Deleted {len(resp.data)} predictions for Account 2")
    except Exception as e:
        print(f"❌ Error cleaning Account 2: {e}")
    
    print("\n✅ CLEANUP COMPLETE")

if __name__ == "__main__":
    main()
