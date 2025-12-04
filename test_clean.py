"""
Clean database and run fresh tests
"""
from supabase import create_client
import requests

SUPABASE_URL = "https://tocuqnqdewhqhbhkbplm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc"
BASE_URL = "http://127.0.0.1:5000"

ACCOUNT_1 = {"email": "dazrini@gmail.com", "password": "gummybear"}
ACCOUNT_2 = {"email": "test2@gmail.com", "password": "password"}

print("="*80)
print("CLEAN & TEST")
print("="*80)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Login both accounts
auth1 = supabase.auth.sign_in_with_password(ACCOUNT_1)
token1 = auth1.session.access_token
user1_id = auth1.user.id

auth2 = supabase.auth.sign_in_with_password(ACCOUNT_2)
token2 = auth2.session.access_token
user2_id = auth2.user.id

print(f"\nAccount 1: {user1_id}")
print(f"Account 2: {user2_id}")

# Clean all predictions for both accounts
print("\nCleaning database...")
try:
    supabase.table('predictions').delete().eq('user_id', user1_id).execute()
    supabase.table('predictions').delete().eq('user_id', user2_id).execute()
    print("✅ Database cleaned")
except Exception as e:
    print(f"Clean error: {e}")

# TEST 1: Save for Account 1
print("\n[TEST 1] Save AAPL for Account 1")
headers1 = {"Authorization": f"Bearer {token1}", "Content-Type": "application/json"}
pred1 = {"stock": "AAPL", "duration": "5 days", "lastClose": 280.00, "predictedPrice": 285.00, "method": "LSTM", "delta": 5.00, "pct": 1.79}
r = requests.post(f"{BASE_URL}/api/predictions/save", json=pred1, headers=headers1)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("✅ Saved")

# TEST 2: Save for Account 2
print("\n[TEST 2] Save TSLA for Account 2")
headers2 = {"Authorization": f"Bearer {token2}", "Content-Type": "application/json"}
pred2 = {"stock": "TSLA", "duration": "3 days", "lastClose": 250.00, "predictedPrice": 260.00, "method": "EMA", "delta": 10.00, "pct": 4.00}
r = requests.post(f"{BASE_URL}/api/predictions/save", json=pred2, headers=headers2)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print("✅ Saved")

# TEST 3: Get Account 1 - should ONLY see AAPL
print("\n[TEST 3] Get predictions for Account 1")
r = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers1)
data = r.json()
if data.get('success'):
    stocks = [p['stock'] for p in data['predictions']]
    print(f"Stocks: {stocks}")
    if 'TSLA' in stocks:
        print("❌ ISOLATION FAILURE: Account 1 sees TSLA!")
    else:
        print("✅ Isolation OK")

# TEST 4: Get Account 2 - should ONLY see TSLA
print("\n[TEST 4] Get predictions for Account 2")
r = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers2)
data = r.json()
if data.get('success'):
    stocks = [p['stock'] for p in data['predictions']]
    print(f"Stocks: {stocks}")
    if 'AAPL' in stocks:
        print("❌ ISOLATION FAILURE: Account 2 sees AAPL!")
    else:
        print("✅ Isolation OK")

print("\n" + "="*80)
print("TESTS COMPLETE")
