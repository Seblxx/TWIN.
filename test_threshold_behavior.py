# Test script: Verify 82% threshold behavior
import requests
import json

API_URL = "http://localhost:5000/predict"

tests = [
    ("apple in 3 days", "100% - Should work ✅"),
    ("appel in 3 days", "80% - Below 82% → Should show suggestions ⚠️"),
    ("apppple in 3 days", "83% - Above 82% → Should auto-detect ✅"),
    ("applelflk in 3 days", "71% - Below 82% → Should show suggestions ⚠️"),
    ("micrsf in 1 week", "80% - Below 82% → Should show suggestions ⚠️"),
    ("microsoft in 1 week", "100% - Should work ✅"),
    ("teslaaa in 2 days", "83% - Above 82% → Should auto-detect ✅"),
    ("amzon in 5 days", "91% - Above 82% → Should auto-detect ✅"),
]

print("=== Testing 82% Threshold ===\n")
for input_text, expected in tests:
    try:
        response = requests.post(API_URL, json={"input": input_text}, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and "stock" in data:
            print(f"✅ AUTO-DETECTED: '{input_text}' → {data['stock']}")
            print(f"   Expected: {expected}")
        elif response.status_code == 400 or "error" in data:
            print(f"⚠️  SUGGESTIONS: '{input_text}' → Error with suggestions")
            print(f"   Expected: {expected}")
            if "suggestions" in data:
                print(f"   Top suggestion: {data['suggestions'][0]['name']}")
        else:
            print(f"❓ UNEXPECTED: '{input_text}' → {data}")
        print()
    except Exception as e:
        print(f"❌ ERROR: '{input_text}' → {e}\n")
