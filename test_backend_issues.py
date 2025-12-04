"""
Backend API Test Suite
Tests all endpoints to identify issues
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# Test credentials
TEST_USER_EMAIL = "test2@gmail.com"
TEST_USER_PASSWORD = "test123"

def print_separator(title):
    print("\n" + "="*60)
    print(title)
    print("="*60)

def test_login():
    """Test login and get auth token"""
    print_separator("TEST: Login")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200 and 'token' in data:
        print("✅ Login successful")
        return data['token']
    else:
        print("❌ Login failed")
        return None

def test_get_predictions(token):
    """Test getting predictions"""
    print_separator("TEST: Get Predictions")
    
    response = requests.get(
        f"{BASE_URL}/api/predictions",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Predictions count: {len(data.get('predictions', []))}")
        print("✅ Get predictions successful")
        return data.get('predictions', [])
    else:
        print(f"Response: {response.text}")
        print("❌ Get predictions failed")
        return []

def test_save_prediction(token):
    """Test saving a prediction"""
    print_separator("TEST: Save Prediction")
    
    prediction_data = {
        "stock": "AAPL",
        "duration": "5 days",
        "last_close": 150.0,
        "predicted_price": 155.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/predictions",
        headers={"Authorization": f"Bearer {token}"},
        json=prediction_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Prediction ID: {data.get('id')}")
        print("✅ Save prediction successful")
        return data.get('id')
    else:
        print("❌ Save prediction failed")
        return None

def test_clear_all_predictions(token):
    """Test clearing all predictions - THIS IS THE FAILING ENDPOINT"""
    print_separator("TEST: Clear All Predictions (DELETE /api/predictions/clear)")
    
    response = requests.delete(
        f"{BASE_URL}/api/predictions/clear",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Clear all predictions successful")
        return True
    else:
        print("❌ Clear all predictions FAILED - This is the Test 6 issue!")
        # Try to parse error
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass
        return False

def test_delete_single_prediction(token, prediction_id):
    """Test deleting a single prediction"""
    print_separator(f"TEST: Delete Single Prediction (ID: {prediction_id})")
    
    response = requests.delete(
        f"{BASE_URL}/api/predictions/{prediction_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Delete single prediction successful")
        return True
    else:
        print("❌ Delete single prediction failed")
        return False

def run_all_tests():
    """Run all backend tests"""
    print("\n" + "🔬 BACKEND API TEST SUITE" + "\n")
    
    # Test 1: Login
    token = test_login()
    if not token:
        print("\n❌ Cannot continue without auth token")
        return
    
    # Test 2: Get initial predictions
    initial_predictions = test_get_predictions(token)
    print(f"\nInitial predictions count: {len(initial_predictions)}")
    
    # Test 3: Save a test prediction
    prediction_id = test_save_prediction(token)
    
    # Test 4: Get predictions again (should have +1)
    after_save = test_get_predictions(token)
    print(f"\nPredictions after save: {len(after_save)}")
    
    # Test 5: Clear all predictions - THIS IS THE FAILING ONE
    clear_success = test_clear_all_predictions(token)
    
    # Test 6: Verify cleared
    after_clear = test_get_predictions(token)
    print(f"\nPredictions after clear: {len(after_clear)}")
    
    if clear_success and len(after_clear) == 0:
        print("\n✅ Clear all predictions working correctly!")
    elif not clear_success:
        print("\n❌ Clear all endpoint returned error (500)")
        print("This is the Test 6 issue - backend endpoint needs fixing")
    else:
        print("\n❌ Clear all endpoint succeeded but predictions not deleted")
    
    # Test 7: Try deleting single prediction (if any exist)
    if len(after_clear) > 0:
        test_delete_single_prediction(token, after_clear[0]['id'])
    
    print("\n" + "="*60)
    print("BACKEND TESTS COMPLETE")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()
