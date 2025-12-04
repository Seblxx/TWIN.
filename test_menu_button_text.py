"""
Test that menu button shows HOME when logged out, LOGOUT when logged in
"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"

async def test_menu_button_text():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        issues = []
        
        print("\n" + "="*70)
        print("MENU BUTTON TEXT TEST")
        print("="*70)
        
        # ========== TEST 1: Check button text when logged out ==========
        print("\n[TEST 1] Menu button text when NOT logged in")
        try:
            await page.goto(f"{BASE_URL}/index.html")
            await page.wait_for_load_state('networkidle')
            
            # Clear login state
            await page.evaluate("localStorage.removeItem('twin_user_logged_in')")
            await page.reload()
            await page.wait_for_load_state('networkidle')
            await asyncio.sleep(1)
            
            # Open menu
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open', timeout=3000)
            await asyncio.sleep(1)
            
            # Check button text
            button_text = await page.inner_text('#menuHome')
            button_text = button_text.strip().upper()
            
            print(f"  Button text: '{button_text}'")
            
            if button_text == 'HOME':
                print("  ✓ Correctly shows 'HOME' when logged out")
            else:
                issues.append(f"Button shows '{button_text}' when logged out (should be 'HOME')")
                print(f"  ✗ Wrong! Shows '{button_text}' (should be 'HOME')")
            
            # Close menu
            await page.click('#menuBtn')
            await asyncio.sleep(1)
            
        except Exception as e:
            issues.append(f"Test 1 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 2: Check button text when logged in ==========
        print("\n[TEST 2] Menu button text when logged in")
        try:
            # Go to intro and login
            await page.goto(f"{BASE_URL}/intro.html")
            await page.wait_for_load_state('networkidle')
            await page.click('#loginToggleBtn')
            await page.wait_for_selector('.modal-overlay.open')
            await page.fill('#emailInput', 'dazrini@gmail.com')
            await page.fill('#passwordInput', 'gummybear')
            await page.click('#loginBtn')
            await page.wait_for_url(f"{BASE_URL}/index.html", timeout=5000)
            await asyncio.sleep(1)
            
            # Open menu
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open', timeout=3000)
            await asyncio.sleep(1)
            
            # Check button text
            button_text = await page.inner_text('#menuHome')
            button_text = button_text.strip().upper()
            
            print(f"  Button text: '{button_text}'")
            
            if button_text == 'LOGOUT':
                print("  ✓ Correctly shows 'LOGOUT' when logged in")
            else:
                issues.append(f"Button shows '{button_text}' when logged in (should be 'LOGOUT')")
                print(f"  ✗ Wrong! Shows '{button_text}' (should be 'LOGOUT')")
            
            # Test logout functionality
            await page.click('#menuHome')
            try:
                await page.wait_for_selector('#confirmYes', timeout=2000)
                await page.click('#confirmYes')
            except:
                pass
            
            await asyncio.sleep(2)
            current_url = page.url
            
            if 'intro.html' in current_url:
                print("  ✓ Logout redirects to intro.html")
            else:
                issues.append(f"Logout redirects to {current_url} (should be intro.html)")
                print(f"  ✗ Logout redirects to {current_url}")
                
        except Exception as e:
            issues.append(f"Test 2 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== FINAL REPORT ==========
        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)
        
        if len(issues) == 0:
            print("✓ ALL MENU BUTTON TESTS PASSED!")
        else:
            print(f"✗ FOUND {len(issues)} ISSUE(S):\n")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n" + "="*70)
        
        await browser.close()
        
        return issues

if __name__ == "__main__":
    issues = asyncio.run(test_menu_button_text())
    exit(0 if len(issues) == 0 else 1)
