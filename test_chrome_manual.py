"""
Manual Chrome Browser Test - Real User Flow
Tests actual browser behavior for:
1. Get Started button → should NOT auto-login
2. Fresh session → should be blank slate
3. Logout button → should return to intro page logged out
"""
import asyncio
from playwright.async_api import async_playwright
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def test_chrome_manual():
    async with async_playwright() as p:
        # Launch Chrome (not Chromium - actual Chrome)
        browser = await p.chromium.launch(
            headless=False,
            channel='chrome',  # Use actual Chrome
            slow_mo=800  # Slow down so we can see
        )
        context = await browser.new_context()
        page = await context.new_page()
        
        print("="*80)
        print("MANUAL CHROME TEST - Real User Flow")
        print("="*80)
        
        # ===== TEST 1: Get Started Button =====
        print("\n[TEST 1] Click 'Get Started' - Should NOT auto-login")
        print("-"*80)
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)
        
        # Click Get Started
        get_started_btn = page.locator('button:has-text("Get Started")')
        if await get_started_btn.count() > 0:
            print("✓ Found 'Get Started' button")
            await get_started_btn.click()
            await page.wait_for_timeout(2000)
            
            # Check if we're on index.html
            if 'index.html' in page.url:
                print("✓ Navigated to index.html")
                
                # Check if logged in (should NOT be)
                user_email = await page.evaluate("localStorage.getItem('twin_user_email')")
                is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
                
                if user_email or is_logged_in == 'true':
                    print(f"❌ FAIL: Auto-logged in as {user_email}")
                    print(f"   twin_user_logged_in: {is_logged_in}")
                else:
                    print("✓ PASS: Not logged in (guest mode)")
                    
                # Check input field is empty
                input_value = await page.locator('#userInput').input_value()
                if input_value:
                    print(f"❌ FAIL: Input not empty: '{input_value}'")
                else:
                    print("✓ PASS: Input field empty (blank slate)")
                    
                # Check chat is empty
                basic_msgs = await page.locator('#messages-basic .message').count()
                plus_msgs = await page.locator('#messages-plus .message').count()
                if basic_msgs > 0 or plus_msgs > 0:
                    print(f"❌ FAIL: Chat not empty (TWIN-: {basic_msgs}, TWIN+: {plus_msgs})")
                else:
                    print("✓ PASS: Chat empty (blank slate)")
        else:
            print("❌ Get Started button not found")
        
        # ===== TEST 2: Login and Check State =====
        print("\n[TEST 2] Login and verify authenticated state")
        print("-"*80)
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_timeout(1000)
        
        # Switch to login
        await page.locator('#loginToggleBtn').click()
        await page.wait_for_timeout(500)
        
        # Login
        await page.locator('#emailInput').fill('dazrini@gmail.com')
        await page.locator('#passwordInput').fill('gummybear')
        await page.locator('#loginBtn').click()
        await page.wait_for_timeout(3000)
        
        if 'index.html' in page.url:
            print("✓ Logged in and redirected to index.html")
            
            user_email = await page.evaluate("localStorage.getItem('twin_user_email')")
            print(f"✓ Logged in as: {user_email}")
        else:
            print("❌ Login failed or didn't redirect")
        
        # ===== TEST 3: Logout Button =====
        print("\n[TEST 3] Click Logout - Should return to intro.html logged out")
        print("-"*80)
        
        # Open menu
        await page.locator('#menuBtn').click()
        await page.wait_for_timeout(800)
        
        # Find logout button (menuHome button that shows "LOGOUT" when logged in)
        logout_btn = page.locator('#menuHome')
        logout_visible = await logout_btn.is_visible()
        
        if logout_visible:
            print("✓ Logout button visible")
            
            # Check button text
            button_text = await logout_btn.text_content()
            print(f"  Button text: {button_text}")
            
            await logout_btn.click()
            await page.wait_for_timeout(1000)
            
            # Wait for modal to appear
            modal = page.locator('#modalOverlay')
            if await modal.is_visible():
                print("✓ Confirmation modal appeared")
                
                # Click the "Yes" button in the modal
                confirm_yes = page.locator('#confirmYes')
                await confirm_yes.click()
                await page.wait_for_timeout(2000)
            
            # Check URL
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            if 'intro.html' in current_url:
                print("✓ PASS: Returned to intro.html")
            else:
                print(f"❌ FAIL: Still on {current_url} (should be intro.html)")
            
            # Check logged out state
            user_email = await page.evaluate("localStorage.getItem('twin_user_email')")
            is_logged_in = await page.evaluate("localStorage.getItem('twin_user_logged_in')")
            
            if user_email or is_logged_in == 'true':
                print(f"❌ FAIL: Still logged in state - email: {user_email}, logged_in: {is_logged_in}")
            else:
                print("✓ PASS: Logged out (localStorage cleared)")
        else:
            print("❌ Logout button not visible")
        
        # ===== TEST 4: Fresh Session After Logout =====
        print("\n[TEST 4] Navigate to index.html after logout - Should be blank slate")
        print("-"*80)
        
        # Click Get Started again
        get_started = page.locator('button:has-text("Get Started")')
        if await get_started.count() > 0:
            await get_started.click()
            await page.wait_for_timeout(2000)
            
            # Check blank slate
            input_value = await page.locator('#userInput').input_value()
            basic_msgs = await page.locator('#messages-basic .message').count()
            plus_msgs = await page.locator('#messages-plus .message').count()
            
            blank_slate = not input_value and basic_msgs == 0 and plus_msgs == 0
            
            if blank_slate:
                print("✓ PASS: Fresh blank slate (no input, no messages)")
            else:
                print(f"❌ FAIL: Not blank - input: '{input_value}', msgs: {basic_msgs}/{plus_msgs}")
        
        print("\n" + "="*80)
        print("TEST COMPLETE - Review results above")
        print("="*80)
        print("\nBrowser will stay open for 10 seconds for manual inspection...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_chrome_manual())
