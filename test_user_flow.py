"""
Test the exact user flow requested:
1. Click star to save prediction → check if predictions loading
2. Go to predictions page → check if saved predictions display
3. Click logout while logged in → check if goes back to index.html (NOT intro.html)
4. Leave predictions back to index → check if queries still remain
"""
import asyncio
import json
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"

async def test_user_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        issues = []
        
        print("\n" + "="*70)
        print("USER FLOW TEST - Checking Specific Issues")
        print("="*70)
        
        # Login first
        print("\n[SETUP] Logging in...")
        await page.goto(f"{BASE_URL}/intro.html")
        await page.wait_for_load_state('networkidle')
        await page.click('#loginToggleBtn')
        await page.wait_for_selector('.modal-overlay.open')
        await page.fill('#emailInput', 'dazrini@gmail.com')
        await page.fill('#passwordInput', 'gummybear')
        await page.click('#loginBtn')
        await page.wait_for_url(f"{BASE_URL}/index.html")
        print("  ✓ Logged in successfully")
        
        # Clear old predictions for clean test
        await page.evaluate("localStorage.removeItem('twin_predictions')")
        
        # ========== TEST 1: Star Button Saves & Shows Loading ==========
        print("\n[TEST 1] Click star to save prediction - check if predictions loading")
        try:
            # Submit query
            await page.fill('#userInput', 'TSLA in 1 week')
            await page.click('button.btn-both-inside')
            
            # Wait for bot response
            await page.wait_for_selector('.bot', timeout=30000)
            await asyncio.sleep(2)  # Wait for full response
            
            # Click star button
            star_btns = await page.query_selector_all('.star-save-btn')
            if len(star_btns) > 0:
                print(f"  Found {len(star_btns)} star button(s)")
                await star_btns[0].click()
                await asyncio.sleep(1)
                
                # Check localStorage
                predictions_str = await page.evaluate("localStorage.getItem('twin_predictions')")
                if predictions_str:
                    predictions = json.loads(predictions_str)
                    if len(predictions) > 0:
                        print(f"  ✓ Prediction saved to localStorage: {predictions[0].get('stock')} {predictions[0].get('duration')}")
                    else:
                        issues.append("ISSUE 1: Star clicked but predictions array empty")
                        print("  ✗ Predictions array is empty!")
                else:
                    issues.append("ISSUE 1: Star clicked but nothing in localStorage")
                    print("  ✗ No predictions in localStorage!")
            else:
                issues.append("ISSUE 1: No star button found after query")
                print("  ✗ No star button found!")
                
        except Exception as e:
            issues.append(f"ISSUE 1 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 2: Predictions Display on Predictions Page ==========
        print("\n[TEST 2] Navigate to predictions page - check if saved predictions display")
        try:
            # Open menu
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open')
            
            # Click predictions button
            await page.click('#menuPredictions')
            await page.wait_for_url(f"{BASE_URL}/predictions.html", timeout=5000)
            await asyncio.sleep(2)
            
            # Check if predictions are displayed
            pred_items = await page.query_selector_all('.prediction-item')
            list_html = await page.inner_html('#predictionsList')
            
            if len(pred_items) > 0:
                print(f"  ✓ {len(pred_items)} prediction(s) displayed on page")
                # Get details
                for i, item in enumerate(pred_items[:2]):  # Show first 2
                    stock = await item.query_selector('.stock-symbol')
                    if stock:
                        stock_text = await stock.inner_text()
                        print(f"    - Prediction {i+1}: {stock_text}")
            else:
                if 'No predictions yet' in list_html:
                    issues.append("ISSUE 2: Predictions not loading - shows 'No predictions yet' message")
                    print("  ✗ No predictions displayed - shows empty state!")
                    print(f"    localStorage check: {await page.evaluate('localStorage.getItem(\"twin_predictions\")')}")
                else:
                    issues.append("ISSUE 2: Predictions page has unexpected state")
                    print("  ✗ Unexpected state!")
                    
        except Exception as e:
            issues.append(f"ISSUE 2 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 3: Logout Redirects to index.html (NOT intro.html) ==========
        print("\n[TEST 3] Click logout - check if it goes to index.html (not intro.html)")
        try:
            # Go back to index first
            await page.goto(f"{BASE_URL}/index.html")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)
            
            # Click menu
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open')
            
            # Click logout
            await page.click('#menuHome')
            
            # Check for confirmation modal
            try:
                await page.wait_for_selector('#confirmYes', timeout=2000)
                await page.click('#confirmYes')
            except:
                pass
            
            # Wait for navigation
            await asyncio.sleep(2)
            current_url = page.url
            
            if 'index.html' in current_url:
                print(f"  ✓ Correctly redirected to index.html")
            elif 'intro.html' in current_url:
                issues.append("ISSUE 3: Logout redirects to intro.html instead of index.html")
                print(f"  ✗ WRONG! Redirected to intro.html (should be index.html)")
            else:
                issues.append(f"ISSUE 3: Logout redirected to unexpected page: {current_url}")
                print(f"  ✗ Redirected to: {current_url}")
                
        except Exception as e:
            issues.append(f"ISSUE 3 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 4: Query Input Persists After Navigation ==========
        print("\n[TEST 4] Navigate to predictions and back - check if queries remain")
        try:
            # Login again if needed
            is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
            if is_logged_in != 'true':
                await page.goto(f"{BASE_URL}/intro.html")
                await page.click('#loginToggleBtn')
                await page.wait_for_selector('.modal-overlay.open')
                await page.fill('#emailInput', 'dazrini@gmail.com')
                await page.fill('#passwordInput', 'gummybear')
                await page.click('#loginBtn')
                await page.wait_for_url(f"{BASE_URL}/index.html")
            
            # Make sure we're on index
            await page.goto(f"{BASE_URL}/index.html")
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)
            
            # Submit a query
            await page.fill('#userInput', 'NVDA in 3 days')
            await page.click('button.btn-both-inside')
            await page.wait_for_selector('.bot', timeout=30000)
            await asyncio.sleep(2)
            
            # Get current messages HTML
            messages_before = await page.inner_html('#messages-basic')
            has_nvda_before = 'NVDA' in messages_before or 'Nvidia' in messages_before
            print(f"  Messages before navigation: {len(messages_before)} chars, has NVDA: {has_nvda_before}")
            
            # Navigate to predictions
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open')
            await page.click('#menuPredictions')
            await page.wait_for_url(f"{BASE_URL}/predictions.html")
            await asyncio.sleep(1)
            
            # Navigate back to index
            await page.click('.back-button')
            await page.wait_for_url(f"{BASE_URL}/index.html")
            await asyncio.sleep(2)
            
            # Check if messages restored
            messages_after = await page.inner_html('#messages-basic')
            has_nvda_after = 'NVDA' in messages_after or 'Nvidia' in messages_after
            print(f"  Messages after navigation: {len(messages_after)} chars, has NVDA: {has_nvda_after}")
            
            if len(messages_after) > 100 and has_nvda_after:
                print(f"  ✓ Queries persisted after navigation!")
            elif len(messages_after) < 50:
                issues.append("ISSUE 4: Messages cleared after navigation (should persist)")
                print(f"  ✗ Messages were CLEARED! (only {len(messages_after)} chars)")
            else:
                print(f"  ⚠ Partial data: {len(messages_after)} chars, NVDA present: {has_nvda_after}")
                
        except Exception as e:
            issues.append(f"ISSUE 4 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== FINAL REPORT ==========
        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)
        
        if len(issues) == 0:
            print("✓ ALL USER FLOWS WORKING CORRECTLY!")
        else:
            print(f"✗ FOUND {len(issues)} ISSUE(S):\n")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n" + "="*70)
        
        await browser.close()
        
        return issues

if __name__ == "__main__":
    issues = asyncio.run(test_user_flow())
    exit(0 if len(issues) == 0 else 1)
