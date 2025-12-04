"""
Test API with suggestions - verify that suggestions appear in all responses
"""
import requests
import json
import time

# Wait for server to start
time.sleep(3)

BASE_URL = "http://localhost:5000"

def test_successful_prediction_with_suggestions():
    """Test that successful predictions include suggestions"""
    print("\n=== Test 1: Successful prediction with suggestions ===")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input": "apple in 3 days"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert "stock" in data
    assert data["stock"] == "AAPL"
    assert "suggestions" in data, "Suggestions should be present in successful predictions!"
    assert len(data["suggestions"]) == 3, "Should have 3 suggestions"
    
    # Check suggestion structure
    for sug in data["suggestions"]:
        assert "symbol" in sug
        assert "name" in sug
        assert "echo" in sug
        assert "in 3 days" in sug["echo"], "Echo should include duration"
    
    print("✅ PASS: Successful prediction includes suggestions")
    return True

def test_typo_correction_with_suggestions():
    """Test fuzzy matching with typos shows suggestions"""
    print("\n=== Test 2: Typo correction (appel) with suggestions ===")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input": "appel in 5 days"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert data["stock"] == "AAPL", "Should detect AAPL from 'appel' typo"
    assert "suggestions" in data
    assert len(data["suggestions"]) == 3
    
    # Check that suggestions include company names not tickers
    for sug in data["suggestions"]:
        assert "in 5 days" in sug["echo"]
        # Name should be readable (Apple, Microsoft, etc), not ticker
        assert not sug["name"].isupper() or len(sug["name"]) > 5
    
    print("✅ PASS: Typo correction with suggestions works")
    return True

def test_failed_detection_with_suggestions():
    """Test that failed detection shows suggestions"""
    print("\n=== Test 3: Failed detection (invalid) with suggestions ===")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input": "blahblahblah in 2 days"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 400
    assert "error" in data
    assert "suggestions" in data, "Failed detection should still show suggestions"
    assert len(data["suggestions"]) == 3
    
    print("✅ PASS: Failed detection shows suggestions")
    return True

def test_price_only_with_suggestions():
    """Test price-only mode (no duration) includes suggestions"""
    print("\n=== Test 4: Price-only mode with suggestions ===")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input": "microsoft"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert data["mode"] == "price_only"
    assert "suggestions" in data, "Price-only mode should include suggestions"
    assert len(data["suggestions"]) == 3
    
    print("✅ PASS: Price-only mode includes suggestions")
    return True

def test_multiple_word_company():
    """Test multi-word company name"""
    print("\n=== Test 5: Multi-word company (JP Morgan) ===")
    
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"input": "jp morgan in 1 week"}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(json.dumps(data, indent=2))
    
    assert response.status_code == 200
    assert "suggestions" in data
    assert data["duration"] == "1 weeks"
    
    print("✅ PASS: Multi-word company works with suggestions")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING API SUGGESTIONS FEATURE")
    print("=" * 60)
    
    try:
        results = []
        results.append(test_successful_prediction_with_suggestions())
        results.append(test_typo_correction_with_suggestions())
        results.append(test_failed_detection_with_suggestions())
        results.append(test_price_only_with_suggestions())
        results.append(test_multiple_word_company())
        
        print("\n" + "=" * 60)
        print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
        print("=" * 60)
        
        if all(results):
            print("🎉 ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
