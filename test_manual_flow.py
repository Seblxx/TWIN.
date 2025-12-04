"""
Manual test script for theme switching, login/signup, and query execution
Run this and manually verify the colors match across pages
"""
import asyncio
from playwright.async_api import async_playwright

async def test_manual_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*70)
        print("🧪 MANUAL TESTING FLOW")
        print("="*70)
        print("\n👁️  Please visually verify each step as it executes...")
        
        # Clear localStorage to start fresh
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.evaluate('() => localStorage.clear()')
        
        print("\n📋 PART 1: THEME GRADIENT VERIFICATION")
        print("-" * 70)
        print("Testing each theme's logo gradient on intro page...")
        
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)
        
        themes = [
            ('Dark', 'dark.css', 'Pink → Black gradient'),
            ('Light', 'light.css', 'Teal → Purple gradient'),
            ('Monochrome', 'monochrome.css', 'White with shadow'),
            ('Liquid Glass', 'liquidglass.css', 'White → Gray gradient'),
            ('Royal', 'royal.css', 'Sky Blue → Pink gradient')
        ]
        
        for theme_name, theme_file, expected in themes:
            current = await page.locator('#themeCss').get_attribute('href')
            print(f"\n✓ {theme_name} Theme ({current})")
            print(f"  Expected logo: {expected}")
            input(f"  👁️  VERIFY: Does TWIN logo show {expected}? (Press Enter to continue)")
            
            # Click to next theme
            if theme_name != 'Royal':
                await page.locator('#themeToggle').click()
                await page.wait_for_timeout(500)
        
        print("\n📋 PART 2: SIGNUP TEST")
        print("-" * 70)
        await page.locator('#loginToggleBtn').click()
        await page.wait_for_timeout(500)
        await page.locator('#toggleLink').click()  # Switch to signup
        await page.wait_for_timeout(300)
        
        # Fill signup form
        test_email = f"test_{int(asyncio.get_event_loop().time())}@example.com"
        await page.locator('#usernameInput').fill('TestUser')
        await page.locator('#emailInput').fill(test_email)
        await page.locator('#passwordInput').fill('test123456')
        
        print(f"✓ Filling signup form...")
        print(f"  Email: {test_email}")
        print(f"  Username: TestUser")
        print(f"  Password: test123456")
        input("  👁️  VERIFY: Form filled correctly? (Press Enter to submit)")
        
        await page.locator('#loginBtn').click()
        await page.wait_for_timeout(3000)
        
        # Should redirect to index.html
        current_url = page.url
        print(f"✓ Redirected to: {current_url}")
        input("  👁️  VERIFY: Successfully logged in and on index.html? (Press Enter)")
        
        print("\n📋 PART 3: INDEX PAGE THEME VERIFICATION")
        print("-" * 70)
        print("Cycling through all themes on main app...")
        
        for i, (theme_name, theme_file, expected) in enumerate(themes):
            current = await page.locator('#themeCss').get_attribute('href')
            print(f"\n✓ {theme_name} Theme on index.html")
            print(f"  Expected TWIN. title: {expected}")
            print(f"  Buttons: Check TWIN-, TWIN+, Explain colors match theme")
            input(f"  👁️  VERIFY: Colors correct? (Press Enter to continue)")
            
            if i < len(themes) - 1:
                await page.locator('#themeToggle').click()
                await page.wait_for_timeout(500)
        
        print("\n📋 PART 4: QUERY EXECUTION TEST")
        print("-" * 70)
        print("Testing stock query with company logo...")
        
        # Set to dark theme for testing
        await page.locator('#themeToggle').click()
        await page.wait_for_timeout(500)
        
        # Fill query
        await page.locator('#userInput').fill('Apple in 5 days')
        print("✓ Query: 'Apple in 5 days'")
        input("  👁️  VERIFY: Query entered? (Press Enter to submit)")
        
        # Click TWIN button (both)
        await page.locator('.btn-both-inside').click()
        await page.wait_for_timeout(8000)  # Wait for API responses
        
        print("✓ Query executed")
        input("  👁️  VERIFY: \n  - Apple logo displayed?\n  - TWIN- result shown?\n  - TWIN+ diagnostics shown?\n  - Explain button visible and NOT pink?\n  (Press Enter)")
        
        print("\n📋 PART 5: EXPLAIN BUTTON COLOR CHECK")
        print("-" * 70)
        print("Checking Explain button is transparent (not pink) in royal theme...")
        
        # Find current theme and cycle to royal
        while True:
            current = await page.locator('#themeCss').get_attribute('href')
            if 'royal' in current:
                break
            await page.locator('#themeToggle').click()
            await page.wait_for_timeout(500)
        
        print("✓ Switched to Royal theme")
        input("  👁️  VERIFY: Explain button is transparent with white text/border (NOT pink)? (Press Enter)")
        
        print("\n📋 PART 6: PREDICTIONS PAGE (LOGGED IN)")
        print("-" * 70)
        print("Opening menu to go to predictions...")
        
        # Open menu
        await page.locator('#menuBtn').click()
        await page.wait_for_timeout(500)
        
        print("✓ Menu opened")
        input("  👁️  VERIFY: PREDICTIONS button visible in menu? (Press Enter to click)")
        
        # Go to predictions
        await page.locator('#menuPredictions').click()
        await page.wait_for_timeout(2000)
        
        current_url = page.url
        print(f"✓ Navigated to: {current_url}")
        
        # Check if we have predictions
        has_predictions = await page.locator('.prediction-card').count() > 0
        
        if has_predictions:
            print("✓ Predictions displayed")
            input("  👁️  VERIFY: \n  - PREDICTIONS title gradient matches Royal theme?\n  - Theme toggle circle visible?\n  - Prediction cards styled correctly?\n  (Press Enter)")
            
            # Test theme toggle on predictions
            await page.locator('#themeToggle').click()
            await page.wait_for_timeout(500)
            print("✓ Theme toggled on predictions page")
            input("  👁️  VERIFY: Theme changed successfully? (Press Enter)")
        else:
            print("ℹ️  No predictions to display (need to star a prediction first)")
        
        print("\n" + "="*70)
        print("✅ MANUAL TESTING COMPLETE!")
        print("="*70)
        print("\nSummary of what was tested:")
        print("  ✓ Logo gradients on intro page (all 5 themes)")
        print("  ✓ Signup functionality")
        print("  ✓ Theme persistence to index page")
        print("  ✓ Logo gradients on index page (all 5 themes)")
        print("  ✓ Query execution with company logo")
        print("  ✓ Explain button color (royal theme)")
        print("  ✓ Predictions page (if logged in)")
        print("\nBrowser will close in 5 seconds...")
        await page.wait_for_timeout(5000)
        
        await browser.close()
        return True

if __name__ == '__main__':
    asyncio.run(test_manual_flow())
