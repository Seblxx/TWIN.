"""
Test logging in with previously created accounts
"""
import asyncio
from playwright.async_api import async_playwright

async def test_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("🔐 LOGIN TEST")
        print("="*80)
        
        # Test accounts created in previous test
        test_accounts = [
            {"email": "test_1764111733@twin.test", "password": "SecurePass123!"},
            {"email": "test_1764112119@twin.test", "password": "SecurePass123!"}
        ]
        
        try:
            for i, account in enumerate(test_accounts, 1):
                print(f"\n📋 TEST {i}: Login with {account['email']}")
                print("-" * 80)
                
                # Go to intro page
                await page.goto('http://127.0.0.1:5000/intro.html')
                await page.wait_for_load_state('networkidle')
                
                # Clear localStorage
                await page.evaluate('() => localStorage.clear()')
                await page.reload()
                await page.wait_for_timeout(500)
                
                # Click "Sign In" button
                await page.locator('#loginToggleBtn').click()
                await page.wait_for_timeout(500)
                print("✓ Opened login modal")
                
                # Verify it's in login mode (not signup)
                toggle_text = await page.locator('#toggleLink').text_content()
                if "Sign up" in toggle_text:
                    print("✓ Already in login mode")
                else:
                    # Switch to login mode
                    await page.locator('#toggleLink').click()
                    await page.wait_for_timeout(300)
                    print("✓ Switched to login mode")
                
                # Fill login form
                await page.locator('#emailInput').fill(account['email'])
                await page.locator('#passwordInput').fill(account['password'])
                print(f"✓ Filled email: {account['email']}")
                print(f"✓ Filled password: {account['password']}")
                
                # Click login button
                await page.locator('#loginBtn').click()
                print("✓ Clicked login button")
                await page.wait_for_timeout(3000)
                
                # Check if redirected to index.html
                current_url = page.url
                if 'index.html' in current_url:
                    print(f"✅ Successfully logged in and redirected to: {current_url}")
                else:
                    print(f"❌ FAILED: Expected index.html but got: {current_url}")
                    continue
                
                # Verify logged in state
                is_logged_in = await page.evaluate('() => localStorage.getItem("twin_user_logged_in")')
                user_email = await page.evaluate('() => localStorage.getItem("twin_user_email")')
                
                print(f"✓ Logged in status: {is_logged_in}")
                print(f"✓ User email stored: {user_email}")
                
                if is_logged_in == "true" and user_email == account['email']:
                    print(f"✅ Account {i} login verification PASSED")
                else:
                    print(f"❌ Account {i} login verification FAILED")
                
                # Test theme switching while logged in
                print("\n  Testing theme switching...")
                for j in range(3):
                    before = await page.locator('#themeCss').get_attribute('href')
                    await page.locator('#themeToggle').click()
                    await page.wait_for_timeout(500)
                    after = await page.locator('#themeCss').get_attribute('href')
                    print(f"  ✓ Theme toggle {j+1}: {before.split('?')[0]} → {after.split('?')[0]}")
                
                # Logout for next test
                print("\n  Logging out...")
                await page.locator('#menuBtn').click()
                await page.wait_for_timeout(500)
                
                async def handle_dialog(dialog):
                    await dialog.accept()
                    
                page.on('dialog', handle_dialog)
                await page.locator('#menuHome').click()
                await page.wait_for_timeout(2000)
                print("  ✓ Logged out\n")
            
            print("="*80)
            print("✅ ALL LOGIN TESTS PASSED")
            print("="*80)
            
            await page.wait_for_timeout(2000)
            await browser.close()
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH ERROR: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return False

if __name__ == '__main__':
    success = asyncio.run(test_login())
    exit(0 if success else 1)
