"""
Comprehensive Playwright test to verify all fixes:
1. Menu styling (centered, black rectangle)
2. Predictions page layout and theme toggle position
3. Star button saves predictions to localStorage
4. Predictions page loads saved predictions
5. Query persistence when returning from predictions
6. Logout redirects to intro.html
"""

import asyncio
import json
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"

async def test_all_fixes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*60)
        print("COMPREHENSIVE TEST SUITE")
        print("="*60)
        
        # ============ TEST 1: Login Flow ============
        print("\n[TEST 1] Login Flow")
        await page.goto(f"{BASE_URL}/intro.html")
        await page.wait_for_load_state('networkidle')
        
        # Click Sign In button to open modal
        await page.click('#loginToggleBtn')
        await page.wait_for_selector('.modal-overlay.open', timeout=3000)
        
        # Fill in demo credentials
        await page.fill('#emailInput', 'test@example.com')
        await page.fill('#passwordInput', 'password123')
        await page.click('#loginBtn')
        
        # Wait for redirect to index.html
        await page.wait_for_url(f"{BASE_URL}/index.html", timeout=5000)
        print("  ✓ Login successful, redirected to index.html")
        
        # Verify login status in localStorage
        is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
        assert is_logged_in == 'true', f"Expected 'true', got '{is_logged_in}'"
        print("  ✓ Login status saved to localStorage")
        
        # ============ TEST 2: Make a Prediction Query ============
        print("\n[TEST 2] Make a Prediction Query")
        await page.wait_for_selector('#queryInput', timeout=5000)
        await page.fill('#queryInput', 'Apple in 5 days')
        await page.click('#twinBtn')
        
        # Wait for response
        await page.wait_for_selector('.bot-msg', timeout=15000)
        print("  ✓ Prediction query submitted and response received")
        
        # Wait for star button to appear (should appear for logged-in users)
        await asyncio.sleep(2)
        star_btn = await page.query_selector('.star-save-btn')
        if star_btn:
            print("  ✓ Star save button is visible (user is logged in)")
            
            # ============ TEST 3: Save Prediction ============
            print("\n[TEST 3] Save Prediction with Star Button")
            await star_btn.click()
            await asyncio.sleep(1)
            
            # Check localStorage for saved prediction
            predictions = await page.evaluate("localStorage.getItem('twin_predictions')")
            print(f"  Raw predictions in localStorage: {predictions}")
            
            if predictions:
                preds_list = json.loads(predictions)
                if len(preds_list) > 0:
                    print(f"  ✓ Prediction saved! Found {len(preds_list)} prediction(s)")
                    print(f"    - Stock: {preds_list[0].get('stock', 'N/A')}")
                    print(f"    - Duration: {preds_list[0].get('duration', 'N/A')}")
                else:
                    print("  ✗ Predictions array is empty!")
            else:
                print("  ✗ No predictions in localStorage!")
        else:
            print("  ✗ Star button not found (check if user is logged in)")
        
        # ============ TEST 4: Menu Styling ============
        print("\n[TEST 4] Menu Styling (Centered Black Rectangle)")
        # Click menu button
        await page.click('#menuBtn')
        await page.wait_for_selector('.menu-options.open', timeout=3000)
        
        # Get menu position
        menu_box = await page.evaluate("""
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
                    windowWidth: window.innerWidth,
                    windowHeight: window.innerHeight
                };
            }
        """)
        
        print(f"  Menu position: left={menu_box['left']:.0f}, top={menu_box['top']:.0f}")
        print(f"  Menu size: {menu_box['width']:.0f}x{menu_box['height']:.0f}")
        print(f"  Background: {menu_box['background']}")
        
        # Check if menu is roughly centered
        expected_left = (menu_box['windowWidth'] - menu_box['width']) / 2
        expected_top = (menu_box['windowHeight'] - menu_box['height']) / 2
        
        if abs(menu_box['left'] - expected_left) < 50 and abs(menu_box['top'] - expected_top) < 50:
            print("  ✓ Menu is centered on screen")
        else:
            print(f"  ✗ Menu not centered. Expected ~({expected_left:.0f}, {expected_top:.0f})")
        
        if 'rgb(0, 0, 0)' in menu_box['background'] or menu_box['background'] == '#000000':
            print("  ✓ Menu has solid black background")
        else:
            print(f"  ✗ Menu background is not black: {menu_box['background']}")
        
        # Check LOGOUT button text
        logout_text = await page.inner_text('#menuHome')
        if logout_text.strip().upper() == 'LOGOUT':
            print("  ✓ Button shows 'LOGOUT' for logged-in user")
        else:
            print(f"  ✗ Button shows '{logout_text}' instead of 'LOGOUT'")
        
        # ============ TEST 5: Navigate to Predictions ============
        print("\n[TEST 5] Navigate to Predictions Page")
        
        # First check if predictions button is enabled
        preds_btn = await page.query_selector('#menuPredictions')
        is_disabled = await preds_btn.get_attribute('disabled')
        
        if is_disabled:
            print("  ⚠ Predictions button is disabled - no saved predictions detected")
        else:
            await preds_btn.click()
            await page.wait_for_url(f"{BASE_URL}/predictions.html", timeout=5000)
            print("  ✓ Navigated to predictions.html")
            
            # ============ TEST 6: Predictions Page Theme Toggle Position ============
            print("\n[TEST 6] Theme Toggle Position on Predictions Page")
            await page.wait_for_selector('#themeToggle', timeout=3000)
            
            toggle_pos = await page.evaluate("""
                () => {
                    const toggle = document.querySelector('#themeToggle');
                    const rect = toggle.getBoundingClientRect();
                    return { left: rect.left, right: rect.right, top: rect.top };
                }
            """)
            
            back_btn_pos = await page.evaluate("""
                () => {
                    const btn = document.querySelector('.back-button');
                    if (!btn) return null;
                    const rect = btn.getBoundingClientRect();
                    return { left: rect.left, right: rect.right, top: rect.top };
                }
            """)
            
            if back_btn_pos:
                print(f"  Theme toggle position: left={toggle_pos['left']:.0f}, right={toggle_pos['right']:.0f}")
                print(f"  Back button position: left={back_btn_pos['left']:.0f}, right={back_btn_pos['right']:.0f}")
                
                # Check if they overlap (both near left edge)
                if toggle_pos['left'] > 100:  # Toggle should be on right side now
                    print("  ✓ Theme toggle is NOT overlapping back button (positioned right)")
                else:
                    print("  ✗ Theme toggle may overlap back button (both on left)")
            
            # ============ TEST 7: Check if Predictions are Displayed ============
            print("\n[TEST 7] Predictions Display")
            await asyncio.sleep(1)
            
            # Check predictions list content
            list_html = await page.inner_html('#predictionsList')
            if 'No predictions yet' in list_html:
                print("  ✗ No predictions displayed (check localStorage)")
            else:
                items = await page.query_selector_all('.prediction-item')
                print(f"  ✓ Found {len(items)} prediction item(s) displayed")
            
            # ============ TEST 8: Return to Index and Check Query Persistence ============
            print("\n[TEST 8] Query Persistence on Return")
            await page.click('.back-button')
            await page.wait_for_url(f"{BASE_URL}/index.html", timeout=5000)
            print("  ✓ Returned to index.html")
            
            # Wait for page to load and restore messages
            await asyncio.sleep(1)
            
            # Check if messages were restored
            messages = await page.inner_html('#messages-basic')
            if 'Apple' in messages or 'AAPL' in messages:
                print("  ✓ Previous query is still visible!")
            else:
                print("  ✗ Previous query was NOT restored")
                print(f"    Messages content length: {len(messages)}")
        
        # ============ TEST 9: Logout Redirect ============
        print("\n[TEST 9] Logout Redirect to intro.html")
        
        # Open menu
        await page.click('#menuBtn')
        await page.wait_for_selector('.menu-options.open', timeout=3000)
        
        # Click logout
        await page.click('#menuHome')
        
        # Wait for confirmation modal
        try:
            await page.wait_for_selector('.confirm-modal', timeout=2000)
            print("  ✓ Confirmation modal appeared")
            
            # Click confirm
            confirm_btn = await page.query_selector('.confirm-modal .confirm-yes, .confirm-modal button:has-text("Yes")')
            if confirm_btn:
                await confirm_btn.click()
            else:
                # Try clicking any button in modal
                await page.click('.confirm-modal button >> nth=0')
            
            await page.wait_for_url(f"{BASE_URL}/intro.html", timeout=5000)
            print("  ✓ Successfully redirected to intro.html after logout!")
            
        except Exception as e:
            print(f"  ⚠ Confirmation modal issue: {e}")
            # Check if we're on intro.html anyway
            current_url = page.url
            if 'intro.html' in current_url:
                print("  ✓ Redirected to intro.html (no confirmation modal)")
            else:
                print(f"  ✗ Not redirected. Current URL: {current_url}")
        
        # Final check - verify logged out
        is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
        if is_logged_in != 'true':
            print("  ✓ User is logged out (localStorage cleared)")
        else:
            print("  ✗ User still shows as logged in")
        
        print("\n" + "="*60)
        print("TEST SUITE COMPLETE")
        print("="*60 + "\n")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_all_fixes())
