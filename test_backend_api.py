"""
Simple backend API test - No Playwright, just curl-style requests
Tests the prediction save/load endpoints directly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("="*80)
print("🔧 BACKEND API TEST - PREDICTIONS")
print("="*80)

# Step 1: Login to get auth token
print("\n[1/4] Logging in to get auth token...")
login_data = {
    "email": "dazrini@gmail.com",
    "password": "gummybear"
}

# We need to get the token from Supabase - simulate what the frontend does
# For now, we'll test with a mock token to see the error
print("⚠️  Note: Using test approach - will check API response\n")

# Step 2: Test save prediction endpoint WITHOUT token (should fail)
print("[2/4] Testing save prediction WITHOUT auth token...")
prediction_data = {
    "stock": "AAPL",
    "duration": "5 days",
    "lastClose": 278.85,
    "predictedPrice": 285.47,
    "method": "LSTM",
    "delta": 6.62,
    "pct": 2.37
}

response = requests.post(
    f"{BASE_URL}/api/predictions/save",
    json=prediction_data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 401:
    print("✅ Correctly requires authentication\n")
else:
    print(f"⚠️  Expected 401, got {response.status_code}\n")

# Step 3: Test with invalid token (should fail with specific error)
print("[3/4] Testing save prediction WITH invalid token...")
headers = {
    "Authorization": "Bearer invalid_token_12345"
}

response = requests.post(
    f"{BASE_URL}/api/predictions/save",
    json=prediction_data,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

# Step 4: Test get predictions endpoint
print("[4/4] Testing get predictions WITHOUT token...")
response = requests.get(f"{BASE_URL}/api/predictions/user")

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print()

print("="*80)
print("📊 BACKEND TEST SUMMARY")
print("="*80)
print("Check the Flask server window for detailed error logs!")
print("Look for AttributeError, 500 errors, or database connection issues")
print("="*80)
