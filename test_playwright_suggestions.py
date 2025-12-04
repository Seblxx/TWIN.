"""
Playwright Visual Test - Shows suggestions appearing in the browser
This test opens a real browser so you can SEE the suggestions working!
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_suggestions_visual():
    """Visual test showing suggestions in the browser"""
    
    with sync_playwright() as p:
        # Launch browser in headed mode so you can see it!
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        page = context.new_page()
        
        print("\n🌐 Opening TWIN application in browser...")
        page.goto("http://localhost:5000")
        time.sleep(2)
        
        # Test 1: Type a valid company with typo
        print("\n✍️ Test 1: Typing 'appel in 3 days' (typo)...")
        input_field = page.locator('input[type="text"], input[placeholder*="stock"]').first
        input_field.fill("appel in 3 days")
        input_field.press("Enter")
        time.sleep(3)
        
        print("✅ Looking for prediction result...")
        # Should show AAPL prediction
        print("✅ Looking for suggestions...")
        # Should show 3 suggestions
        time.sleep(2)
        
        # Test 2: Type another company
        print("\n✍️ Test 2: Typing 'microsft in 1 week' (another typo)...")
        input_field.click()
        input_field.fill("microsft in 1 week")
        input_field.press("Enter")
        time.sleep(3)
        
        print("✅ Should show MSFT prediction with suggestions...")
        time.sleep(2)
        
        # Test 3: Invalid input to see suggestions only
        print("\n✍️ Test 3: Typing 'blahblah in 2 days' (invalid)...")
        input_field.click()
        input_field.fill("blahblah in 2 days")
        input_field.press("Enter")
        time.sleep(3)
        
        print("✅ Should show error with 3 suggestions...")
        time.sleep(2)
        
        # Test 4: Price-only mode
        print("\n✍️ Test 4: Typing 'tesla' (no duration)...")
        input_field.click()
        input_field.fill("tesla")
        input_field.press("Enter")
        time.sleep(3)
        
        print("✅ Should show price with suggestions...")
        time.sleep(3)
        
        print("\n🎉 Visual test complete! Check the browser window.")
        print("Press Enter to close the browser...")
        input()
        
        browser.close()

def test_api_direct():
    """Quick API test to verify backend is working"""
    print("\n🔧 Testing API directly...")
    
    import requests
    import json
    
    tests = [
        {
            "name": "Valid prediction",
            "input": "apple in 3 days",
            "expected_status": 200
        },
        {
            "name": "Typo correction",
            "input": "appel in 5 days",
            "expected_status": 200
        },
        {
            "name": "Invalid input",
            "input": "xyz123 in 2 days",
            "expected_status": 400
        },
        {
            "name": "Price only",
            "input": "microsoft",
            "expected_status": 200
        }
    ]
    
    for test in tests:
        print(f"\n📝 {test['name']}: '{test['input']}'")
        try:
            response = requests.post(
                "http://localhost:5000/predict",
                json={"input": test["input"]},
                timeout=10
            )
            
            data = response.json()
            
            print(f"   Status: {response.status_code}")
            print(f"   Stock: {data.get('stock', 'N/A')}")
            
            if "suggestions" in data:
                print(f"   ✅ Suggestions present ({len(data['suggestions'])} items)")
                for i, sug in enumerate(data['suggestions'][:3], 1):
                    print(f"      {i}. {sug['name']} ({sug['symbol']}) - {sug['echo']}")
            else:
                print(f"   ❌ NO SUGGESTIONS!")
            
            if response.status_code == test['expected_status']:
                print(f"   ✅ Status matches expected")
            else:
                print(f"   ❌ Expected {test['expected_status']}, got {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ API tests complete!")

if __name__ == "__main__":
    print("=" * 70)
    print("TWIN PREDICTIONS - VISUAL PLAYWRIGHT TEST")
    print("=" * 70)
    
    # First test API
    print("\n[1/2] Testing API endpoints...")
    test_api_direct()
    
    # Then run visual test
    print("\n[2/2] Starting visual browser test...")
    print("💡 A browser window will open - you'll see the suggestions in action!")
    time.sleep(2)
    
    try:
        test_suggestions_visual()
        print("\n✅ All tests completed!")
    except ImportError:
        print("\n⚠️  Playwright not installed. Install with:")
        print("   pip install playwright")
        print("   python -m playwright install chromium")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
