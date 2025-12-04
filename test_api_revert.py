"""Integration test for the reverted fuzzy matching API"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_predict_endpoint():
    """Test the /predict endpoint with various inputs"""
    
    test_cases = [
        {
            "input": "apple in 4 days",
            "expected_ticker": "AAPL",
            "description": "Exact match"
        },
        {
            "input": "aple in 4 days",
            "expected_ticker": "AAPL",
            "description": "Typo - should fuzzy match to Apple"
        },
        {
            "input": "microsft in 3 days",
            "expected_ticker": "MSFT",
            "description": "Typo - should fuzzy match to Microsoft"
        },
        {
            "input": "invalid company name in 2 days",
            "expected_ticker": None,
            "description": "Invalid input - should get suggestions (never error)"
        }
    ]
    
    print("Testing /predict endpoint:")
    print("=" * 70)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/", timeout=2)
        print("✓ Server is running\n")
    except Exception as e:
        print(f"✗ Server not running. Start it with: python app.py")
        print(f"  Error: {e}\n")
        return
    
    for test in test_cases:
        print(f"Test: {test['description']}")
        print(f"Input: '{test['input']}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/predict",
                json={"input": test['input']},
                timeout=10
            )
            
            data = response.json()
            
            if response.status_code == 200 and "predictions" in data:
                ticker = data.get("ticker")
                print(f"✓ Success: Detected ticker {ticker}")
                print(f"  Models: {', '.join(data['predictions'].keys())}")
            elif "suggestions" in data:
                print(f"✓ Got suggestions (as expected for unclear input):")
                for sug in data["suggestions"]:
                    print(f"  - {sug['symbol']} ({sug['name']})")
            else:
                print(f"✗ Unexpected response: {data}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("-" * 70)

if __name__ == "__main__":
    print("Make sure the Flask app is running first!")
    print("Start it with: python app.py\n")
    test_predict_endpoint()
