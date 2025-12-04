"""
Comprehensive API tests using requests (equivalent to curl)
Tests all endpoints with fuzzy matching
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_health():
    """Test health endpoint"""
    print_section("TEST 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_exact_match():
    """Test exact company name"""
    print_section("TEST 2: Exact Match - 'apple in 4 days'")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"input": "apple in 4 days"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("stock") == "AAPL":
            print("✅ PASSED: Detected AAPL correctly")
            return True
        else:
            print("❌ FAILED: Did not detect AAPL")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_typo_fuzzy_match():
    """Test fuzzy matching with typo"""
    print_section("TEST 3: Fuzzy Match - 'aple in 4 days' (typo)")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"input": "aple in 4 days"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("stock") == "AAPL":
            print("✅ PASSED: Fuzzy matched typo 'aple' to AAPL")
            return True
        else:
            print("❌ FAILED: Did not fuzzy match to AAPL")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_another_typo():
    """Test another fuzzy match"""
    print_section("TEST 4: Fuzzy Match - 'microsft in 3 days' (typo)")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"input": "microsft in 3 days"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("stock") == "MSFT":
            print("✅ PASSED: Fuzzy matched typo 'microsft' to MSFT")
            return True
        else:
            print("❌ FAILED: Did not fuzzy match to MSFT")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_suggestions_always_appear():
    """Test that suggestions always appear for unclear input"""
    print_section("TEST 5: Suggestions - 'blahblah in 2 days'")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"input": "blahblah in 2 days"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if "suggestions" in data and len(data["suggestions"]) >= 3:
            print(f"✅ PASSED: Got {len(data['suggestions'])} suggestions")
            for sug in data["suggestions"]:
                print(f"  - {sug['symbol']} ({sug['name']})")
            return True
        else:
            print("❌ FAILED: No suggestions provided")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_explicit_ticker():
    """Test explicit ticker input"""
    print_section("TEST 6: Explicit Ticker - '$TSLA in 5 days'")
    try:
        response = requests.post(
            f"{BASE_URL}/predict",
            json={"input": "$TSLA in 5 days"},
            timeout=15
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("stock") == "TSLA":
            print("✅ PASSED: Detected explicit ticker $TSLA")
            return True
        else:
            print("❌ FAILED: Did not detect TSLA")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_twin_plus():
    """Test TWIN+ endpoint"""
    print_section("TEST 7: TWIN+ Diagnostics - 'tesla in 10 days'")
    try:
        response = requests.post(
            f"{BASE_URL}/predict_plus",
            json={"input": "tesla in 10 days"},
            timeout=20
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and "diagnostics" in data:
            print("✅ PASSED: TWIN+ diagnostics returned")
            return True
        else:
            print("❌ FAILED: No diagnostics in response")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def test_twin_star():
    """Test TWIN* endpoint"""
    print_section("TEST 8: TWIN* Ensemble - 'microsoft in 7 days'")
    try:
        response = requests.post(
            f"{BASE_URL}/predict_star",
            json={"input": "microsoft in 7 days"},
            timeout=20
        )
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200 and data.get("mode") == "twin_star":
            print("✅ PASSED: TWIN* ensemble returned")
            return True
        else:
            print("❌ FAILED: TWIN* did not work")
            return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

def main():
    print("\n" + "█"*70)
    print("  TWIN FUZZY MATCHING API TEST SUITE")
    print("█"*70)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("\n✅ Server is running at", BASE_URL)
    except:
        print("\n❌ ERROR: Server not running!")
        print("Start it with: python app.py")
        return
    
    # Run all tests
    tests = [
        test_health,
        test_exact_match,
        test_typo_fuzzy_match,
        test_another_typo,
        test_suggestions_always_appear,
        test_explicit_ticker,
        test_twin_plus,
        test_twin_star
    ]
    
    results = []
    for test in tests:
        try:
            passed = test()
            results.append(passed)
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "="*70)
    print("  TEST SUMMARY")
    print("="*70)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Fuzzy matching is working perfectly!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review output above.")

if __name__ == "__main__":
    main()
