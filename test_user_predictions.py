import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

print("=" * 60)
print("TESTING USER-SPECIFIC PREDICTIONS SYSTEM")
print("=" * 60)

# Test 1: Save prediction for User A
print("\n1. Testing save prediction for user@example.com...")
prediction_data = {
    "userEmail": "user@example.com",
    "id": f"pred_{datetime.now().timestamp()}",
    "stock": "AAPL",
    "duration": "1 week",
    "lastClose": 150.25,
    "predictedPrice": 155.50,
    "method": "random_forest",
    "delta": 5.25,
    "pct": 3.49,
    "timestamp": datetime.now().isoformat()
}

try:
    response = requests.post(
        f"{BASE_URL}/api/predictions/save",
        json=prediction_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"   ✓ Prediction saved successfully!")
        print(f"   Response: {response.json()}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Get predictions for User A
print("\n2. Testing get predictions for user@example.com...")
try:
    response = requests.get(f"{BASE_URL}/api/predictions/user/user@example.com")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            predictions = data.get('predictions', [])
            print(f"   ✓ Retrieved {len(predictions)} predictions")
            if predictions:
                print(f"   Latest: {predictions[0]['stock']} - ${predictions[0]['predicted_price']}")
        else:
            print(f"   ✗ API returned error: {data}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Save prediction for User B
print("\n3. Testing save prediction for otheruser@example.com...")
prediction_data_b = {
    "userEmail": "otheruser@example.com",
    "id": f"pred_{datetime.now().timestamp()}",
    "stock": "TSLA",
    "duration": "2 weeks",
    "lastClose": 250.00,
    "predictedPrice": 275.00,
    "method": "lstm",
    "delta": 25.00,
    "pct": 10.0,
    "timestamp": datetime.now().isoformat()
}

try:
    response = requests.post(
        f"{BASE_URL}/api/predictions/save",
        json=prediction_data_b,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        print(f"   ✓ Prediction saved successfully!")
    else:
        print(f"   ✗ Failed: {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Verify User A still only sees their predictions
print("\n4. Verifying user@example.com only sees their own predictions...")
try:
    response = requests.get(f"{BASE_URL}/api/predictions/user/user@example.com")
    data = response.json()
    
    if data.get('success'):
        predictions = data.get('predictions', [])
        has_aapl = any(p['stock'] == 'AAPL' for p in predictions)
        has_tsla = any(p['stock'] == 'TSLA' for p in predictions)
        
        if has_aapl and not has_tsla:
            print(f"   ✓ Correct! User A sees AAPL but not TSLA")
        elif has_tsla:
            print(f"   ✗ FAIL: User A sees TSLA (should be User B's only)")
        else:
            print(f"   ? User A doesn't see AAPL predictions")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Verify User B only sees their predictions
print("\n5. Verifying otheruser@example.com only sees their own predictions...")
try:
    response = requests.get(f"{BASE_URL}/api/predictions/user/otheruser@example.com")
    data = response.json()
    
    if data.get('success'):
        predictions = data.get('predictions', [])
        has_aapl = any(p['stock'] == 'AAPL' for p in predictions)
        has_tsla = any(p['stock'] == 'TSLA' for p in predictions)
        
        if has_tsla and not has_aapl:
            print(f"   ✓ Correct! User B sees TSLA but not AAPL")
        elif has_aapl:
            print(f"   ✗ FAIL: User B sees AAPL (should be User A's only)")
        else:
            print(f"   ? User B doesn't see TSLA predictions")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Guest user fallback
print("\n6. Testing guest user (should return empty)...")
try:
    response = requests.get(f"{BASE_URL}/api/predictions/user/guest")
    data = response.json()
    
    predictions = data.get('predictions', [])
    if len(predictions) == 0:
        print(f"   ✓ Guest returns empty list (correct)")
    else:
        print(f"   ✗ Guest has {len(predictions)} predictions (should be 0)")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
print("\nNOTE: If you see database errors, run create_predictions_table.sql")
print("in your Supabase SQL Editor first!")
