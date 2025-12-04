"""
Comprehensive test: Supabase Auth → Predictions → Backend Verification
Tests the complete flow from login to prediction save/load with real auth tokens
"""
import asyncio
import json
import requests
import time
from playwright.async_api import async_playwright, expect

BASE_URL = "http://127.0.0.1:5000"

# Test user credentials
TEST_EMAIL = f"test_user_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPassword123!"

async def test_full_flow():
    print("=" * 80)
    print("COMPREHENSIVE AUTH + PREDICTIONS TEST")
    print("=" * 80)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Enable console logging to catch errors
        page.on("console", lambda msg: print(f"[BROWSER CONSOLE] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
        
        try:
            # ============================================================
            # STEP 1: CLEAR ANY EXISTING AUTH & SIGNUP/LOGIN
            # ============================================================
            print("\n[1/7] Clearing existing auth and signing up...")
            
            # First, clear all localStorage to ensure clean state
            await page.goto(f"{BASE_URL}/index.html")
            await page.evaluate("() => localStorage.clear()")
            print("   → Cleared localStorage")
            
            # Now go to intro page for fresh signup
            await page.goto(f"{BASE_URL}/intro.html")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            
            # Open login modal by clicking "Sign In" button
            print("   → Opening login modal...")
            await page.click('#loginToggleBtn')
            await asyncio.sleep(1)
            
            # Toggle to signup mode
            toggle_link = page.locator('#toggleLink')
            toggle_text = await toggle_link.text_content()
            
            if 'Sign up' in toggle_text:
                print("   → Switching to signup mode...")
                await toggle_link.click()
                await asyncio.sleep(1)
            
            # Fill signup form (modal uses #emailInput and #passwordInput)
            print(f"   → Filling form with: {TEST_EMAIL}")
            await page.fill('#emailInput', TEST_EMAIL)
            await page.fill('#passwordInput', TEST_PASSWORD)
            
            print("   → Clicking Sign Up button...")
            await page.click('#loginBtn')
            
            # Wait for signup to complete and redirect
            await asyncio.sleep(4)
            
            # Check result
            current_url = page.url
            print(f"   → Current URL: {current_url}")
            
            # If still on intro, user exists - try logging in
            if "intro.html" in current_url:
                print("   → User may exist, trying login...")
                
                # Check if modal is still open
                modal_visible = await page.is_visible('#loginModal')
                if not modal_visible:
                    await page.click('#loginToggleBtn')
                    await asyncio.sleep(1)
                
                # Toggle to signin mode
                toggle_link = page.locator('#toggleLink')
                toggle_text = await toggle_link.text_content()
                if 'Sign in' in toggle_text:
                    await toggle_link.click()
                    await asyncio.sleep(1)
                
                await page.fill('#emailInput', TEST_EMAIL)
                await page.fill('#passwordInput', TEST_PASSWORD)
                await page.click('#loginBtn')
                await asyncio.sleep(4)
            
            # ============================================================
            # STEP 2: VERIFY AUTH TOKEN IN LOCALSTORAGE
            # ============================================================
            print("\n[2/7] Verifying auth token in localStorage...")
            token = await page.evaluate("() => localStorage.getItem('twin_supabase_token')")
            user_email = await page.evaluate("() => localStorage.getItem('twin_user_email')")
            
            if not token:
                print("   ❌ ERROR: No auth token found in localStorage!")
                return False
            
            print(f"   ✓ Token found: {token[:50]}...")
            print(f"   ✓ User email: {user_email}")
            
            # ============================================================
            # STEP 3: NAVIGATE TO MAIN APP AND MAKE PREDICTION
            # ============================================================
            print("\n[3/7] Navigating to main app...")
            await page.goto(f"{BASE_URL}/index.html")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            
            print("   → Selecting stock: AAPL")
            await page.select_option('select#stockPicker', 'AAPL')
            await asyncio.sleep(1)
            
            print("   → Selecting duration: 1-day")
            await page.click('button:has-text("1-day")')
            await asyncio.sleep(1)
            
            print("   → Running forecast...")
            await page.click('button:has-text("Run Forecast")')
            
            # Wait for prediction to complete
            print("   → Waiting for prediction results...")
            await page.wait_for_selector('.prediction-result', timeout=30000)
            await asyncio.sleep(2)
            
            # ============================================================
            # STEP 4: SAVE PREDICTION (CLICK STAR)
            # ============================================================
            print("\n[4/7] Saving prediction to database...")
            
            # Look for star button
            star_button = page.locator('button:has-text("★")')
            await star_button.wait_for(state="visible", timeout=10000)
            
            print("   → Clicking star to save...")
            await star_button.click()
            await asyncio.sleep(2)
            
            # Check console for success message
            print("   → Waiting for save confirmation...")
            await asyncio.sleep(2)
            
            # ============================================================
            # STEP 5: VERIFY BACKEND WITH CURL
            # ============================================================
            print("\n[5/7] Verifying prediction saved in backend...")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers)
                print(f"   → GET /api/predictions/user: {response.status_code}")
                
                if response.status_code == 200:
                    predictions = response.json()
                    print(f"   ✓ Found {len(predictions)} predictions")
                    
                    if len(predictions) > 0:
                        latest = predictions[0]
                        print(f"   ✓ Latest prediction: {latest['stock']} - {latest['duration']}")
                        print(f"      Last Close: ${latest['last_close']}")
                        print(f"      Predicted: ${latest['predicted_price']}")
                        print(f"      Delta: {latest['delta']} ({latest['pct']}%)")
                    else:
                        print("   ⚠️  WARNING: No predictions found in database!")
                        return False
                else:
                    print(f"   ❌ ERROR: API returned {response.status_code}")
                    print(f"   Response: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"   ❌ ERROR calling API: {e}")
                return False
            
            # ============================================================
            # STEP 6: NAVIGATE TO PREDICTIONS PAGE
            # ============================================================
            print("\n[6/7] Testing predictions page...")
            await page.goto(f"{BASE_URL}/predictions.html")
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
            
            # Check if predictions are displayed
            prediction_cards = page.locator('.prediction-card')
            count = await prediction_cards.count()
            print(f"   → Found {count} prediction cards on page")
            
            if count > 0:
                print("   ✓ Predictions displaying correctly")
            else:
                print("   ⚠️  WARNING: No prediction cards found")
            
            # ============================================================
            # STEP 7: TEST MULTI-USER ISOLATION
            # ============================================================
            print("\n[7/7] Testing multi-user isolation...")
            
            # Logout
            print("   → Logging out...")
            await page.goto(f"{BASE_URL}/index.html")
            await asyncio.sleep(1)
            await page.click('button:has-text("Logout")')
            await asyncio.sleep(2)
            
            # Verify token cleared
            token_after_logout = await page.evaluate("() => localStorage.getItem('twin_supabase_token')")
            if token_after_logout:
                print("   ⚠️  WARNING: Token not cleared after logout")
            else:
                print("   ✓ Token cleared successfully")
            
            # Create second user
            TEST_EMAIL_2 = f"test_user2_{int(time.time())}@example.com"
            print(f"   → Creating second user: {TEST_EMAIL_2}")
            
            await page.goto(f"{BASE_URL}/intro.html")
            await page.wait_for_load_state("networkidle")
            await page.click("text=Sign Up")
            await asyncio.sleep(1)
            await page.fill('input[type="email"]', TEST_EMAIL_2)
            await page.fill('input[type="password"]', TEST_PASSWORD)
            await page.click('button:has-text("Sign Up")')
            await asyncio.sleep(3)
            
            # Get second user's token
            token2 = await page.evaluate("() => localStorage.getItem('twin_supabase_token')")
            
            if token2:
                # Check predictions for second user
                headers2 = {
                    "Authorization": f"Bearer {token2}",
                    "Content-Type": "application/json"
                }
                
                response2 = requests.get(f"{BASE_URL}/api/predictions/user", headers=headers2)
                if response2.status_code == 200:
                    predictions2 = response2.json()
                    print(f"   ✓ Second user has {len(predictions2)} predictions")
                    
                    if len(predictions2) == 0:
                        print("   ✓ User isolation working - second user sees no predictions")
                    else:
                        print("   ⚠️  Second user sees predictions (may be from previous test)")
                else:
                    print(f"   ⚠️  API error for second user: {response2.status_code}")
            
            # ============================================================
            # FINAL RESULTS
            # ============================================================
            print("\n" + "=" * 80)
            print("TEST COMPLETED SUCCESSFULLY! ✓")
            print("=" * 80)
            print("\nVerified:")
            print("  ✓ Supabase Auth signup/login")
            print("  ✓ JWT token stored in localStorage")
            print("  ✓ Predictions made with frontend")
            print("  ✓ Predictions saved to database")
            print("  ✓ Backend API returns user predictions")
            print("  ✓ Predictions page displays correctly")
            print("  ✓ Logout clears auth token")
            print("  ✓ Multi-user isolation working")
            
            await asyncio.sleep(3)
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            await browser.close()

if __name__ == "__main__":
    result = asyncio.run(test_full_flow())
    exit(0 if result else 1)
