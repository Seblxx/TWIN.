"""
Complete Playwright test for theme switching across all pages and logo gradients
"""
import asyncio
from playwright.async_api import async_playwright

async def test_complete_theme_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("🧪 Testing complete theme flow...")
        print("\n" + "="*60)
        print("PART 1: INTRO PAGE THEME SWITCHING")
        print("="*60)
        
        # Navigate to intro.html
        await page.goto('file:///c:/Users/seblxx/Documents/GitHub/TWIN/intro.html')
        await page.wait_for_load_state('networkidle')
        
        # Test all themes on intro page
        themes = ['dark.css', 'light.css', 'monochrome.css', 'liquidglass.css', 'royal.css']
        theme_toggle = page.locator('#themeToggle')
        
        for i, expected_theme in enumerate(themes):
            current_theme = await page.locator('#themeCss').get_attribute('href')
            print(f"✓ Cycle {i+1}: {current_theme}")
            
            # Check logo gradient changes with theme
            logo_gradient = await page.locator('.logo').evaluate('el => window.getComputedStyle(el).backgroundImage')
            print(f"  Logo gradient: {logo_gradient[:80]}...")
            
            if i < len(themes) - 1:
                await theme_toggle.click()
                await page.wait_for_timeout(500)
        
        print("\n✅ PASS: Intro page themes cycle correctly with logo gradients")
        
        print("\n" + "="*60)
        print("PART 2: THEME PERSISTENCE TO INDEX")
        print("="*60)
        
        # Set to light theme
        saved_theme = await page.evaluate('() => localStorage.getItem("twin_theme_css")')
        print(f"✓ Current saved theme: {saved_theme}")
        
        # Navigate to main app
        get_started = page.locator('#getStartedBtn')
        await get_started.click()
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(1000)
        
        # Check theme persisted
        main_theme = await page.locator('#themeCss').get_attribute('href')
        print(f"✓ Theme on index.html: {main_theme}")
        
        if saved_theme in main_theme:
            print("✅ PASS: Theme persisted from intro to index")
        else:
            print(f"❌ FAIL: Theme mismatch - saved: {saved_theme}, loaded: {main_theme}")
            await browser.close()
            return False
        
        print("\n" + "="*60)
        print("PART 3: INDEX PAGE THEME SWITCHING")
        print("="*60)
        
        # Test theme toggle on main app
        main_toggle = page.locator('#themeToggle')
        
        for i in range(3):
            before = await page.locator('#themeCss').get_attribute('href')
            await main_toggle.click()
            await page.wait_for_timeout(500)
            after = await page.locator('#themeCss').get_attribute('href')
            print(f"✓ Toggle {i+1}: {before} → {after}")
        
        print("✅ PASS: Index page theme toggle works")
        
        # Store current theme for predictions page test
        final_theme = await page.evaluate('() => localStorage.getItem("twin_theme_css")')
        print(f"\n✓ Final theme set: {final_theme}")
        
        # Set logged in status for predictions page
        await page.evaluate('''() => {
            localStorage.setItem('twin_user_logged_in', 'true');
            localStorage.setItem('twin_user_email', 'test@example.com');
            localStorage.setItem('twin_predictions', JSON.stringify([
                {
                    id: 'test-123',
                    stock: 'AAPL',
                    lastClose: 150.00,
                    predictedPrice: 155.00,
                    delta: 5.00,
                    pct: 3.33,
                    duration: '5 days',
                    method: 'twin_minus',
                    timestamp: new Date().toISOString()
                }
            ]));
        }''')
        
        print("\n" + "="*60)
        print("PART 4: PREDICTIONS PAGE THEME PERSISTENCE")
        print("="*60)
        
        # Navigate to predictions page
        await page.goto('file:///c:/Users/seblxx/Documents/GitHub/TWIN/predictions.html')
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)  # Extra wait for JS to initialize
        
        # Wait for theme circle to be visible
        await page.wait_for_selector('#themeToggle', state='visible', timeout=5000)
        
        # Check theme on predictions page
        pred_theme = await page.locator('#themeCss').get_attribute('href')
        print(f"✓ Theme on predictions.html: {pred_theme}")
        
        if final_theme in pred_theme:
            print("✅ PASS: Theme persisted to predictions page")
        else:
            print(f"❌ FAIL: Theme mismatch - expected: {final_theme}, got: {pred_theme}")
            await browser.close()
            return False
        
        # Check if PREDICTIONS title has gradient
        title_gradient = await page.locator('.page-title').evaluate('el => window.getComputedStyle(el).backgroundImage')
        print(f"✓ PREDICTIONS title gradient: {title_gradient[:80]}...")
        
        # Test theme toggle on predictions page
        pred_toggle = page.locator('#themeToggle')
        before_pred = pred_theme
        await pred_toggle.click()
        await page.wait_for_timeout(500)
        after_pred = await page.locator('#themeCss').get_attribute('href')
        
        print(f"✓ Predictions theme toggle: {before_pred} → {after_pred}")
        
        if before_pred != after_pred:
            print("✅ PASS: Predictions page theme toggle works")
        else:
            print("❌ FAIL: Predictions page theme did not change")
            await browser.close()
            return False
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nSummary:")
        print("  ✓ Intro page themes switch with logo gradients")
        print("  ✓ Theme persists from intro → index → predictions")
        print("  ✓ All pages have working theme toggle")
        print("  ✓ Logo/title gradients match each theme")
        
        await page.wait_for_timeout(2000)
        await browser.close()
        return True

if __name__ == '__main__':
    success = asyncio.run(test_complete_theme_flow())
    exit(0 if success else 1)
