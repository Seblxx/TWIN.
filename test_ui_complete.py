"""
Complete UI/UX test with Playwright - automatic issue detection and reporting
"""
import asyncio
import json
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"

async def run_tests():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context()
        page = await context.new_page()
        
        issues = []
        
        print("\n" + "="*70)
        print("COMPREHENSIVE UI/UX TEST SUITE")
        print("="*70)
        
        # ============ TEST 1: Login Flow ============
        print("\n[TEST 1] Login Flow")
        try:
            await page.goto(f"{BASE_URL}/intro.html", timeout=10000)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Click Sign In
            await page.click('#loginToggleBtn', timeout=5000)
            await page.wait_for_selector('.modal-overlay.open', timeout=3000)
            
            # Fill credentials
            await page.fill('#emailInput', 'dazrini@gmail.com')
            await page.fill('#passwordInput', 'gummybear')
            await page.click('#loginBtn')
            
            # Wait for redirect
            await page.wait_for_url(f"{BASE_URL}/index.html", timeout=5000)
            
            # Verify login
            is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
            if is_logged_in == 'true':
                print("  ✓ Login successful")
            else:
                issues.append("Login failed - localStorage not set")
                print("  ✗ Login failed")
        except Exception as e:
            issues.append(f"Login flow error: {str(e)}")
            print(f"  ✗ Error: {e}")
        
        # ============ TEST 2: Query Submission ============
        print("\n[TEST 2] Submit Prediction Query")
        try:
            await page.wait_for_selector('#userInput', timeout=5000)
            await page.fill('#userInput', 'Apple in 5 days')
            await page.click('button.btn-both-inside')
            
            # Wait for response with longer timeout
            await page.wait_for_selector('.bot', timeout=30000)
            
            # Check if star button appears
            await asyncio.sleep(1)
            star_btn = await page.query_selector('.star-save-btn')
            if star_btn:
                print("  ✓ Query submitted, star button visible")
            else:
                issues.append("Star button not found after query")
                print("  ✗ Star button not found")
        except Exception as e:
            issues.append(f"Query submission error: {str(e)}")
            print(f"  ✗ Error: {e}")
        
        # ============ TEST 3: Save Prediction ============
        print("\n[TEST 3] Save Prediction with Star Button")
        try:
            star_btn = await page.query_selector('.star-save-btn')
            if star_btn:
                await star_btn.click()
                await asyncio.sleep(1)
                
                # Check localStorage
                predictions_str = await page.evaluate("localStorage.getItem('twin_predictions')")
                print(f"  Debug: localStorage value = {predictions_str[:100] if predictions_str else 'null'}...")
                
                if predictions_str:
                    predictions = json.loads(predictions_str)
                    if len(predictions) > 0:
                        print(f"  ✓ Prediction saved! Count: {len(predictions)}")
                        print(f"    Stock: {predictions[0].get('stock', 'N/A')}")
                        print(f"    Duration: {predictions[0].get('duration', 'N/A')}")
                    else:
                        issues.append("Predictions array is empty")
                        print("  ✗ Predictions array empty")
                else:
                    issues.append("No predictions in localStorage after save")
                    print("  ✗ No predictions in localStorage")
            else:
                print("  ⚠ Star button not available")
        except Exception as e:
            issues.append(f"Save prediction error: {str(e)}")
            print(f"  ✗ Error: {e}")
        
        # ============ TEST 4: Menu Styling ============
        print("\n[TEST 4] Menu Styling Check")
        try:
            await page.click('#menuBtn', timeout=5000)
            await page.wait_for_selector('.menu-options.open', timeout=3000)
            
            menu_info = await page.evaluate("""
                () => {
                    const menu = document.querySelector('.menu-options');
                    const rect = menu.getBoundingClientRect();
                    const style = getComputedStyle(menu);
                    return {
                        left: rect.left,
                        top: rect.top,
                        width: rect.width,
                        height: rect.height,
                        background: style.backgroundColor,
                        borderRadius: style.borderRadius,
                        windowWidth: window.innerWidth,
                        windowHeight: window.innerHeight
                    };
                }
            """)
            
            # Check centering
            expected_left = (menu_info['windowWidth'] - menu_info['width']) / 2
            expected_top = (menu_info['windowHeight'] - menu_info['height']) / 2
            
            is_centered_h = abs(menu_info['left'] - expected_left) < 50
            is_centered_v = abs(menu_info['top'] - expected_top) < 50
            is_black = 'rgb(0, 0, 0)' in menu_info['background'] or menu_info['background'] == 'rgb(0, 0, 0)'
            
            print(f"  Position: ({menu_info['left']:.0f}, {menu_info['top']:.0f})")
            print(f"  Expected: ({expected_left:.0f}, {expected_top:.0f})")
            print(f"  Background: {menu_info['background']}")
            print(f"  Border radius: {menu_info['borderRadius']}")
            
            if is_centered_h and is_centered_v:
                print("  ✓ Menu is centered")
            else:
                issues.append(f"Menu not centered - off by ({menu_info['left']-expected_left:.0f}, {menu_info['top']-expected_top:.0f})")
                print("  ✗ Menu not centered")
            
            if is_black:
                print("  ✓ Menu has black background")
            else:
                issues.append(f"Menu background not black: {menu_info['background']}")
                print("  ✗ Menu background not black")
            
            # Check logout button text
            logout_text = await page.inner_text('#menuHome')
            if logout_text.strip().upper() == 'LOGOUT':
                print("  ✓ Button shows 'LOGOUT'")
            else:
                issues.append(f"Button shows '{logout_text}' not 'LOGOUT'")
                print(f"  ✗ Button shows '{logout_text}'")
            
        except Exception as e:
            issues.append(f"Menu styling error: {str(e)}")
            print(f"  ✗ Error: {e}")
        
        # ============ TEST 5: Navigate to Predictions ============
        print("\n[TEST 5] Navigate to Predictions Page")
        try:
            preds_btn = await page.query_selector('#menuPredictions')
            is_disabled = await preds_btn.get_attribute('disabled')
            
            if not is_disabled:
                # Save messages before navigating
                await page.evaluate("if (window.saveMessages) window.saveMessages();")
                
                await preds_btn.click()
                await page.wait_for_url(f"{BASE_URL}/predictions.html", timeout=5000)
                print("  ✓ Navigated to predictions.html")
                
                # Check theme toggle position
                await page.wait_for_selector('#themeToggle', timeout=3000)
                
                positions = await page.evaluate("""
                    () => {
                        const toggle = document.querySelector('#themeToggle');
                        const backBtn = document.querySelector('.back-button');
                        const toggleRect = toggle.getBoundingClientRect();
                        const backRect = backBtn.getBoundingClientRect();
                        return {
                            toggle: { left: toggleRect.left, right: toggleRect.right, top: toggleRect.top },
                            back: { left: backRect.left, right: backRect.right, top: backRect.top },
                            windowWidth: window.innerWidth
                        };
                    }
                """)
                
                # Check if toggle is on right side
                if positions['toggle']['left'] > positions['windowWidth'] / 2:
                    print("  ✓ Theme toggle on right side")
                else:
                    issues.append("Theme toggle not on right side")
                    print("  ✗ Theme toggle on left (should be right)")
                
                # Check for overlap
                if positions['toggle']['right'] < positions['back']['left'] or positions['toggle']['left'] > positions['back']['right']:
                    print("  ✓ No overlap with back button")
                else:
                    issues.append("Theme toggle overlaps back button")
                    print("  ✗ Theme toggle overlaps back button")
                
                # ============ TEST 6: Predictions Display ============
                print("\n[TEST 6] Check Predictions Display")
                await asyncio.sleep(1)
                
                # Get console logs
                page.on("console", lambda msg: print(f"  Console: {msg.text}"))
                
                list_html = await page.inner_html('#predictionsList')
                items = await page.query_selector_all('.prediction-item')
                
                if len(items) > 0:
                    print(f"  ✓ {len(items)} prediction(s) displayed")
                else:
                    if 'No predictions yet' in list_html:
                        issues.append("Predictions not loading - localStorage might be empty or key mismatch")
                        print("  ✗ No predictions displayed (check localStorage)")
                    else:
                        print("  ⚠ Empty state")
                
                # ============ TEST 7: Return to Index ============
                print("\n[TEST 7] Return to Index and Check Persistence")
                await page.click('.back-button')
                await page.wait_for_url(f"{BASE_URL}/index.html", timeout=5000)
                print("  ✓ Returned to index.html")
                
                await asyncio.sleep(1)
                
                # Check if messages restored
                basic_html = await page.inner_html('#messages-basic')
                if 'Apple' in basic_html or 'AAPL' in basic_html:
                    print("  ✓ Query persisted (messages restored)")
                else:
                    issues.append("Query not persisted - restoreMessages may not be working")
                    print("  ✗ Query not restored")
                    print(f"    Content length: {len(basic_html)}")
            else:
                print("  ⚠ Predictions button disabled (no predictions)")
        except Exception as e:
            issues.append(f"Predictions navigation error: {str(e)}")
            print(f"  ✗ Error: {e}")
        
        # ============ TEST 8: Logout ============
        print("\n[TEST 8] Logout and Redirect")
        try:
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open', timeout=3000)
            await page.click('#menuHome')
            
            # Wait for confirmation modal
            try:
                await page.wait_for_selector('#confirmYes', timeout=2000)
                print("  ✓ Confirmation modal appeared")
                await page.click('#confirmYes')
            except:
                print("  ⚠ No confirmation modal")
            
            # Check redirect
            await page.wait_for_url(f"{BASE_URL}/intro.html", timeout=5000)
            print("  ✓ Redirected to intro.html")
            
            # Verify logged out
            is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
            if is_logged_in != 'true':
                print("  ✓ Successfully logged out")
            else:
                issues.append("Still shows as logged in after logout")
                print("  ✗ Still logged in")
                
        except Exception as e:
            issues.append(f"Logout error: {str(e)}")
            print(f"  ✗ Error: {e}")
        
        # ============ FINAL REPORT ============
        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)
        
        if len(issues) == 0:
            print("✓ ALL TESTS PASSED - No issues detected!")
        else:
            print(f"✗ FOUND {len(issues)} ISSUE(S):\n")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n" + "="*70)
        
        await browser.close()
        
        return issues

if __name__ == "__main__":
    issues = asyncio.run(run_tests())
    exit(0 if len(issues) == 0 else 1)
