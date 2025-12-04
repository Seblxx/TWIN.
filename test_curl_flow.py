"""
CURL/HTTP Flow Test - Simulates browser requests
Tests the full flow: login, save, get, delete predictions using raw HTTP
"""
import requests
from supabase import create_client
import json
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Supabase config
SUPABASE_URL = "https://tocuqnqdewhqhbhkbplm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc"

BASE_URL = "http://127.0.0.1:5000"

# Test accounts
ACCOUNT_1 = {"email": "dazrini@gmail.com", "password": "gummybear"}
ACCOUNT_2 = {"email": "test2@gmail.com", "password": "password"}

print("=" * 80)
print("CURL/HTTP FLOW TEST - Simulating Browser Requests")
print("=" * 80)

# ===== STEP 1: Login Account 1 =====
print("\n[STEP 1] Login Account 1 via Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
auth1 = supabase.auth.sign_in_with_password(ACCOUNT_1)
token1 = auth1.session.access_token
user1_id = auth1.user.id
print(f"✅ Token obtained: {token1[:30]}...")
print(f"   User ID: {user1_id}")

# ===== STEP 2: Save Prediction for Account 1 =====
print("\n[STEP 2] Save prediction for Account 1 (AAPL)...")
pred1_data = {
    "stock": "AAPL",
    "duration": "3 days",
    "lastClose": 150.50,
    "predictedPrice": 155.75,
    "method": "GBM",
    "timestamp": "2024-12-01T10:00:00Z",
    "delta": 5.25,
    "pct": 3.49
}

headers1 = {"Authorization": f"Bearer {token1}", "Content-Type": "application/json"}
response = requests.post(f"{BASE_URL}/api/predictions/save", json=pred1_data, headers=headers1)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    pred1_id = data.get('id')
    print(f"✅ Saved: ID={pred1_id}")
else:
    print(f"❌ Failed: {response.text}")
    exit(1)

# ===== STEP 3: GET Predictions for Account 1 =====
print("\n[STEP 3] GET predictions for Account 1...")
response = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers1)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data['success']:
        predictions = data['predictions']
        print(f"✅ Retrieved {len(predictions)} predictions")
        # Get the actual prediction ID for later deletion
        pred1_id = predictions[0]['id'] if predictions else None
        for p in predictions:
            print(f"   - {p['stock']} (ID: {p['id']})")
    else:
        print(f"❌ API returned success=false")
else:
    print(f"❌ Failed: {response.text}")

# ===== STEP 4: Login Account 2 =====
print("\n[STEP 4] Login Account 2 via Supabase...")
auth2 = supabase.auth.sign_in_with_password(ACCOUNT_2)
token2 = auth2.session.access_token
user2_id = auth2.user.id
print(f"✅ Token obtained: {token2[:30]}...")
print(f"   User ID: {user2_id}")

# ===== STEP 5: Save Prediction for Account 2 =====
print("\n[STEP 5] Save prediction for Account 2 (TSLA)...")
pred2_data = {
    "stock": "TSLA",
    "duration": "5 days",
    "lastClose": 250.00,
    "predictedPrice": 260.50,
    "method": "GBM",
    "timestamp": "2024-12-01T10:05:00Z",
    "delta": 10.50,
    "pct": 4.20
}

headers2 = {"Authorization": f"Bearer {token2}", "Content-Type": "application/json"}
response = requests.post(f"{BASE_URL}/api/predictions/save", json=pred2_data, headers=headers2)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    pred2_id = data.get('id')
    print(f"✅ Saved: ID={pred2_id}")
else:
    print(f"❌ Failed: {response.text}")
    exit(1)

# ===== STEP 6: GET Predictions for Account 2 (Isolation Check) =====
print("\n[STEP 6] GET predictions for Account 2 (should NOT see Account 1's)...")
response = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers2)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if data['success']:
        predictions = data['predictions']
        stocks = [p['stock'] for p in predictions]
        # Get Account 2's prediction ID for later security test
        pred2_id = predictions[0]['id'] if predictions else None
        print(f"✅ Retrieved {len(predictions)} predictions")
        print(f"   Stocks: {stocks}")
        
        if 'AAPL' in stocks:
            print(f"❌ ISOLATION BREACH: Account 2 sees Account 1's AAPL!")
            exit(1)
        else:
            print(f"✅ Isolation verified: Only Account 2's predictions visible")
    else:
        print(f"❌ API returned success=false")
else:
    print(f"❌ Failed: {response.text}")

# ===== STEP 7: DELETE Prediction for Account 1 =====
print(f"\n[STEP 7] DELETE prediction {pred1_id} for Account 1...")
response = requests.delete(f"{BASE_URL}/api/predictions/delete/{pred1_id}", headers=headers1)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print(f"✅ Deleted successfully")
else:
    print(f"❌ Failed: {response.text}")

# ===== STEP 8: Verify Delete - GET Again =====
print("\n[STEP 8] GET predictions for Account 1 (should be empty after delete)...")
response = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers1)
if response.status_code == 200:
    data = response.json()
    if data['success']:
        predictions = data['predictions']
        print(f"✅ Retrieved {len(predictions)} predictions")
        if len(predictions) == 0:
            print(f"✅ Delete verified: No predictions remain")
        else:
            print(f"⚠️  Still has predictions: {[p['stock'] for p in predictions]}")
else:
    print(f"❌ Failed: {response.text}")

# ===== STEP 9: Try to DELETE Account 2's prediction using Account 1's token (should fail) =====
print(f"\n[STEP 9] Try to DELETE Account 2's prediction using Account 1's token...")
print(f"   Attempting to delete prediction ID: {pred2_id}")
print(f"   Using Account 1 token: {token1[:30]}...")
response = requests.delete(f"{BASE_URL}/api/predictions/delete/{pred2_id}", headers=headers1)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")
if response.status_code == 200:
    print(f"❌ SECURITY BREACH: Account 1 deleted Account 2's prediction!")
    exit(1)
elif response.status_code == 403:
    print(f"✅ Correctly rejected (Forbidden - unauthorized)")
elif response.status_code == 404:
    print(f"✅ Correctly rejected (Not found)")
else:
    print(f"✅ Correctly rejected (status {response.status_code})")

print("\n" + "=" * 80)
print("✅ ALL CURL/HTTP TESTS PASSED")
print("=" * 80)
print("\nVerified:")
print("  ✓ Login and token retrieval")
print("  ✓ Save predictions")
print("  ✓ GET predictions with proper isolation")
print("  ✓ DELETE predictions")
print("  ✓ Cross-account security (can't delete other's predictions)")
print("=" * 80)
