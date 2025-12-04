"""
Playwright test to verify theme switching works on both intro.html and index.html
"""
import asyncio
from playwright.async_api import async_playwright

async def test_theme_switching():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🧪 Testing theme switching on intro.html...")
        
        # Navigate to intro.html
        await page.goto('file:///c:/Users/seblxx/Documents/GitHub/TWIN/intro.html')
        await page.wait_for_load_state('networkidle')
        
        # Get initial theme CSS href
        initial_theme = await page.locator('#themeCss').get_attribute('href')
        print(f"✓ Initial theme: {initial_theme}")
        
        # Click theme toggle circle
        theme_toggle = page.locator('#themeToggle')
        await theme_toggle.click()
        await page.wait_for_timeout(500)  # Wait for CSS to load
        
        # Verify theme changed
        new_theme = await page.locator('#themeCss').get_attribute('href')
        print(f"✓ Theme after toggle: {new_theme}")
        
        if initial_theme == new_theme:
            print("❌ FAIL: Theme did not change on intro.html")
            await browser.close()
            return False
        else:
            print("✅ PASS: Theme changed successfully on intro.html")
        
        # Click a few more times to cycle through themes
        for i in range(3):
            await theme_toggle.click()
            await page.wait_for_timeout(500)
            current_theme = await page.locator('#themeCss').get_attribute('href')
            print(f"✓ Theme cycle {i+2}: {current_theme}")
        
        print("\n🧪 Testing theme persistence on index.html...")
        
        # Click "Get Started" to go to main app
        get_started_btn = page.locator('#getStartedBtn')
        await get_started_btn.click()
        await page.wait_for_load_state('networkidle')
        
        # Verify we're on index.html
        current_url = page.url
        print(f"✓ Navigated to: {current_url}")
        
        # Verify theme CSS is applied
        main_theme = await page.locator('#themeCss').get_attribute('href')
        print(f"✓ Theme on main app: {main_theme}")
        
        # Verify the theme matches what we set on intro page
        saved_theme = await page.evaluate('() => localStorage.getItem("twin_theme_css")')
        print(f"✓ Saved theme in localStorage: {saved_theme}")
        
        if saved_theme not in main_theme:
            print(f"❌ FAIL: Theme did not persist from intro to main app")
            await browser.close()
            return False
        else:
            print("✅ PASS: Theme persisted correctly to main app")
        
        # Test theme toggle on main app
        print("\n🧪 Testing theme toggle on main app...")
        main_theme_toggle = page.locator('#themeToggle')
        initial_main_theme = await page.locator('#themeCss').get_attribute('href')
        
        await main_theme_toggle.click()
        await page.wait_for_timeout(500)
        
        new_main_theme = await page.locator('#themeCss').get_attribute('href')
        print(f"✓ Theme before toggle: {initial_main_theme}")
        print(f"✓ Theme after toggle: {new_main_theme}")
        
        if initial_main_theme == new_main_theme:
            print("❌ FAIL: Theme did not change on main app")
            await browser.close()
            return False
        else:
            print("✅ PASS: Theme changed successfully on main app")
        
        print("\n✅ All theme switching tests passed!")
        
        # Keep browser open for 3 seconds to see the result
        await page.wait_for_timeout(3000)
        
        await browser.close()
        return True

if __name__ == '__main__':
    success = asyncio.run(test_theme_switching())
    exit(0 if success else 1)
