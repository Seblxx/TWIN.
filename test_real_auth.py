"""
Test with REAL Supabase authentication
1. Login via Supabase to get real JWT token
2. Test backend save/load with real token
3. Verify database persistence
"""
import requests
from supabase import create_client
import json
import os

# Supabase config (from app.py)
SUPABASE_URL = "https://tocuqnqdewhqhbhkbplm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRvY3VxbnFkZXdocWhiaGticGxtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMDE2MzgsImV4cCI6MjA3OTU3NzYzOH0.vWfItFkQpHA7Is-KX4eQalI-wxUAJcejPAvy7NDQHvc"

BASE_URL = "http://127.0.0.1:5000"

print("="*80)
print("🔐 REAL AUTH TEST")
print("="*80)

# Step 1: Login with Supabase to get real token
print("\n[1/5] Authenticating with Supabase...")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    auth_response = supabase.auth.sign_in_with_password({
        "email": "dazrini@gmail.com",
        "password": "gummybear"
    })
    
    token = auth_response.session.access_token
    user_id = auth_response.user.id
    
    print(f"✅ Logged in successfully")
    print(f"   User ID: {user_id}")
    print(f"   Token (first 50 chars): {token[:50]}...")
    
except Exception as e:
    print(f"❌ Login failed: {e}")
    exit(1)

# Step 2: Test save prediction with real token
print("\n[2/5] Testing save prediction with REAL token...")
prediction_data = {
    "stock": "AAPL",
    "duration": "5 days",
    "lastClose": 278.85,
    "predictedPrice": 285.47,
    "method": "LSTM",
    "delta": 6.62,
    "pct": 2.37
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.post(
    f"{BASE_URL}/api/predictions/save",
    json=prediction_data,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200 and response.json().get('success'):
    print("✅ Prediction saved successfully!")
    prediction_id = response.json().get('prediction_id')
else:
    print(f"❌ Save failed!")
    print("\nCheck Flask server logs for detailed error!")
    exit(1)

# Step 3: Test get predictions with real token
print("\n[3/5] Testing get predictions with REAL token...")
response = requests.get(
    f"{BASE_URL}/api/predictions/user",
    headers=headers
)

print(f"Status: {response.status_code}")
predictions = response.json()
print(f"Predictions count: {len(predictions)}")

if len(predictions) > 0:
    print("✅ Predictions loaded successfully!")
    print(f"   Latest: {predictions[-1]['stock']} - ${predictions[-1]['predicted_price']}")
else:
    print("⚠️  No predictions found")

# Step 4: Test feedback save
if len(predictions) > 0:
    print("\n[4/5] Testing feedback save...")
    pred_id = predictions[-1]['id']
    
    feedback_data = {
        "predictionId": pred_id,
        "feedback": "accurate"
    }
    
    response = requests.post(
        f"{BASE_URL}/save_feedback",
        json=feedback_data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Feedback saved!")
    else:
        print("❌ Feedback save failed")

# Step 5: Verify in database directly
print("\n[5/5] Verifying in Supabase database...")
try:
    # Query directly from Supabase
    db_predictions = supabase.table('predictions').select('*').eq('user_id', user_id).execute()
    
    print(f"✅ Database query successful")
    print(f"   Total predictions in DB: {len(db_predictions.data)}")
    
    if len(db_predictions.data) > 0:
        latest = db_predictions.data[-1]
        print(f"   Latest: {latest['stock']} - ${latest['predicted_price']}")
        print(f"   Feedback: {latest.get('feedback', 'None')}")
    
except Exception as e:
    print(f"❌ Database query failed: {e}")

print("\n" + "="*80)
print("✅ REAL AUTH TEST COMPLETED")
print("="*80)
print("\nIf all steps passed, the backend is working correctly!")
print("If predictions button is still disabled, the issue is in the frontend.")
