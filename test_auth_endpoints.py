"""
Test Supabase Auth + Predictions endpoints
Run this after logging in through the browser to test with a real token
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:5000"

# INSTRUCTIONS:
# 1. Open browser, go to http://127.0.0.1:5000/intro.html
# 2. Log in with test2@gmail.com / password
# 3. Open browser console (F12)
# 4. Type: localStorage.getItem('twin_supabase_token')
# 5. Copy the token (without quotes) and paste it below

TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual token from browser

def test_save_prediction():
    """Test saving a prediction"""
    print("\n" + "="*60)
    print("TEST 1: Save Prediction")
    print("="*60)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    prediction = {
        "stock": "AAPL",
        "duration": "1 week",
        "lastClose": 180.50,
        "predictedPrice": 190.25,
        "method": "random_forest",
        "delta": 9.75,
        "pct": 5.40,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/predictions/save",
            headers=headers,
            json=prediction
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Prediction saved successfully!")
            return True
        else:
            print("❌ Failed to save prediction")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_get_predictions():
    """Test retrieving predictions"""
    print("\n" + "="*60)
    print("TEST 2: Get User Predictions")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/predictions/user",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and 'predictions' in data:
            print(f"✅ Retrieved {len(data['predictions'])} prediction(s)")
            return True
        else:
            print("❌ Failed to retrieve predictions")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("="*60)
    print("Supabase Auth + Predictions API Test")
    print("="*60)
    
    if TOKEN == "YOUR_TOKEN_HERE":
        print("\n⚠️  ERROR: Please set a valid token!")
        print("\nSteps to get token:")
        print("1. Open browser: http://127.0.0.1:5000/intro.html")
        print("2. Log in with test2@gmail.com")
        print("3. Open console (F12)")
        print("4. Run: localStorage.getItem('twin_supabase_token')")
        print("5. Copy token and paste into this script")
        return
    
    # Run tests
    save_success = test_save_prediction()
    get_success = test_get_predictions()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Save Prediction: {'✅ PASS' if save_success else '❌ FAIL'}")
    print(f"Get Predictions: {'✅ PASS' if get_success else '❌ FAIL'}")
    print("="*60)

if __name__ == "__main__":
    main()
