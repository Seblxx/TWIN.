"""
Test API endpoints using requests (Python equivalent of curl/Postman)
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_config_endpoint():
    """Test /api/config endpoint"""
    print("\n[TEST] GET /api/config")
    try:
        response = requests.get(f"{BASE_URL}/api/config")
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Response: {json.dumps(data, indent=2)}")
        assert response.status_code == 200
        assert 'supabaseUrl' in data
        print("  ✓ Config endpoint works")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_predict_endpoint():
    """Test /predict endpoint"""
    print("\n[TEST] POST /predict")
    payload = {
        "input": "Apple in 5 days"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Response keys: {list(data.keys())}")
        if 'result' in data:
            print(f"  Predicted price: ${data['result']:.2f}")
            print(f"  Stock: {data.get('stock', 'N/A')}")
        assert response.status_code == 200
        assert 'result' in data or 'error' in data
        print("  ✓ Predict endpoint works")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_predict_plus_endpoint():
    """Test /predict_plus endpoint"""
    print("\n[TEST] POST /predict_plus")
    payload = {
        "input": "AAPL"
    }
    try:
        response = requests.post(
            f"{BASE_URL}/predict_plus",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        print(f"  Status: {response.status_code}")
        data = response.json()
        print(f"  Response keys: {list(data.keys())}")
        if response.status_code == 200:
            print("  ✓ Predict Plus endpoint works")
            return True
        else:
            print(f"  ✗ Error: {data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("API ENDPOINT TESTS")
    print("="*60)
    
    results = []
    results.append(("Config", test_config_endpoint()))
    results.append(("Predict", test_predict_endpoint()))
    results.append(("Predict Plus", test_predict_plus_endpoint()))
    
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("\n✓ All API tests passed!")
    else:
        print("\n✗ Some API tests failed")
