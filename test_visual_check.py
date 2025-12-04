"""
Visual test to verify:
1. Intro page theme colors (light, monochrome, liquidglass with new changes)
2. Company logos in predictions
3. No scrollbars in predictions
"""
import asyncio
from playwright.async_api import async_playwright

async def visual_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("🎨 VISUAL CHECK TEST")
        print("="*80)
        
        # Use existing account from comprehensive test
        test_email = "test_1764112119@twin.test"
        test_password = "SecurePass123!"
        
        # STEP 1: Check intro page theme colors
        print("\n📋 STEP 1: Checking intro page theme colors")
        print("-" * 80)
        
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        # Test Light theme
        print("✓ Testing LIGHT theme intro colors...")
        themes_to_test = ['light.css', 'monochrome.css', 'liquidglass.css']
        
        for theme in themes_to_test:
            # Set theme directly
            await page.evaluate(f'''() => {{
                const link = document.getElementById('themeCss');
                link.href = '{theme}?v=13';
                localStorage.setItem('twin_theme_css', '{theme}');
            }}''')
            await page.wait_for_timeout(1000)
            
            # Get computed styles
            logo_color = await page.evaluate('''() => {
                const logo = document.querySelector('.logo');
                return window.getComputedStyle(logo).background;
            }''')
            
            button_bg = await page.evaluate('''() => {
                const btn = document.querySelector('.btn-primary');
                return window.getComputedStyle(btn).background;
            }''')
            
            print(f"  {theme}:")
            print(f"    - Logo: {logo_color[:100]}...")
            print(f"    - Button: {button_bg[:100]}...")
            
            await page.wait_for_timeout(2000)
        
        # STEP 2: Login and check predictions
        print("\n📋 STEP 2: Logging in to check predictions page")
        print("-" * 80)
        
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        await page.locator('#loginToggleBtn').click()
        await page.wait_for_timeout(500)
        
        await page.locator('#emailInput').fill(test_email)
        await page.locator('#passwordInput').fill(test_password)
        await page.locator('#loginBtn').click()
        await page.wait_for_timeout(3000)
        
        current_url = page.url
        if 'index.html' in current_url:
            print(f"✅ Logged in successfully")
        else:
            print(f"⚠️  Login may have failed - URL: {current_url}")
        
        # STEP 3: Navigate to predictions and check layout
        print("\n📋 STEP 3: Checking predictions page layout")
        print("-" * 80)
        
        # Check if there are predictions
        predictions = await page.evaluate('() => JSON.parse(localStorage.getItem("twin_predictions") || "[]")')
        print(f"✓ Found {len(predictions)} saved predictions")
        
        if len(predictions) > 0:
            # Navigate to predictions page
            await page.locator('#menuBtn').click()
            await page.wait_for_timeout(500)
            await page.locator('#menuPredictions').click()
            await page.wait_for_timeout(2000)
            
            if 'predictions.html' in page.url:
                print("✅ Successfully navigated to predictions page")
                
                # Check for scrollbars
                has_scrollbar = await page.evaluate('''() => {
                    const container = document.querySelector('.predictions-grid') || 
                                    document.querySelector('.predictions-page');
                    if (!container) return null;
                    const style = window.getComputedStyle(container);
                    return {
                        scrollbarWidth: style.scrollbarWidth,
                        overflowY: style.overflowY,
                        msOverflowStyle: style.msOverflowStyle
                    };
                }''')
                print(f"  Scrollbar styles: {has_scrollbar}")
                
                # Check prediction cards
                cards = await page.locator('.prediction-card').count()
                print(f"✓ Prediction cards displayed: {cards}")
                
                # Take screenshot
                await page.screenshot(path='predictions_visual.png')
                print("✓ Screenshot saved as 'predictions_visual.png'")
                
                # Wait to view
                await page.wait_for_timeout(5000)
            else:
                print(f"⚠️  Expected predictions.html but got: {page.url}")
        else:
            print("⚠️  No predictions saved - skipping predictions page check")
        
        print("\n" + "="*80)
        print("✅ VISUAL CHECK COMPLETED")
        print("="*80)
        print("\nPlease review:")
        print("  1. Intro page colors for light/monochrome/liquidglass themes")
        print("  2. Predictions page layout (no visible scrollbars)")
        print("  3. Screenshot: predictions_visual.png")
        print("="*80)
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(visual_test())
