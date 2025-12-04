"""
Comprehensive test for all fixes:
1. Intro page colors (light, monochrome, liquidglass)
2. Index page LOGOUT layout
3. Predictions page (no scrollbars, company logos)
4. Query blocking
"""
import asyncio
from playwright.async_api import async_playwright

async def test_all_fixes():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=600)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("🔧 TESTING ALL FIXES")
        print("="*80)
        
        test_email = "test_1764112119@twin.test"
        test_password = "SecurePass123!"
        
        # TEST 1: Intro page theme colors
        print("\n📋 TEST 1: Intro Page Theme Colors")
        print("-" * 80)
        
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        # Test each theme
        themes = [
            ('light.css', 'LIGHT', 'Teal/Purple gradient, black TWIN, visible text'),
            ('monochrome.css', 'MONOCHROME', 'White TWIN, red icons, green button'),
            ('liquidglass.css', 'LIQUID GLASS', 'White TWIN, white Get Started button with black text')
        ]
        
        for theme_file, theme_name, expected in themes:
            await page.evaluate(f'''() => {{
                const link = document.getElementById('themeCss');
                link.href = '{theme_file}?v=13';
                if ('{theme_file}'.includes('liquidglass')) {{
                    document.documentElement.setAttribute('data-theme', 'liquidglass');
                }} else {{
                    document.documentElement.removeAttribute('data-theme');
                }}
            }}''')
            await page.wait_for_timeout(1500)
            print(f"  ✓ {theme_name}: {expected}")
        
        # TEST 2: Login and check index layout
        print("\n📋 TEST 2: Index Page LOGOUT Layout")
        print("-" * 80)
        
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        await page.locator('#loginToggleBtn').click()
        await page.wait_for_timeout(500)
        
        await page.locator('#emailInput').fill(test_email)
        await page.locator('#passwordInput').fill(test_password)
        await page.locator('#loginBtn').click()
        await page.wait_for_timeout(3000)
        
        # Check if LOGOUT button is positioned correctly (not overlapping TWIN)
        logout_visible = await page.locator('#topLogoutBtn').is_visible()
        print(f"  ✓ LOGOUT button visible: {logout_visible}")
        
        if logout_visible:
            logout_position = await page.locator('#topLogoutBtn').bounding_box()
            twin_position = await page.locator('.app-title').bounding_box()
            
            if logout_position and twin_position:
                # Check if logout is to the right of TWIN (not overlapping)
                no_overlap = logout_position['x'] > (twin_position['x'] + twin_position['width'])
                print(f"  ✓ LOGOUT positioned correctly (not overlapping): {no_overlap}")
        
        # TEST 3: Query blocking
        print("\n📋 TEST 3: Query Blocking (Prevent Duplicate TWIN- Queries)")
        print("-" * 80)
        
        # Try to send two queries rapidly
        await page.locator('#userInput').fill('Apple in 5 days')
        
        # Click TWIN button twice rapidly
        await page.locator('button[onclick="sendTwin()"]').click()
        await page.wait_for_timeout(100)
        
        # Try to click again (should be blocked)
        await page.locator('button[onclick="sendTwin()"]').click()
        await page.wait_for_timeout(100)
        
        # Also try the "Analyze with TWIN-" button (should also be blocked)
        await page.locator('button[onclick="sendBasic()"]').click()
        
        print("  ✓ Attempted duplicate queries (should be blocked by JS)")
        await page.wait_for_timeout(8000)
        
        # Count messages
        basic_messages = await page.locator('#messages-basic .bot').count()
        print(f"  ✓ TWIN- messages after rapid clicks: {basic_messages}")
        print(f"  ✓ Expected: 1-2 (not 3+), Result: {'PASS' if basic_messages <= 2 else 'FAIL - query blocking not working'}")
        
        # TEST 4: Predictions page
        print("\n📋 TEST 4: Predictions Page (No Scrollbars + Company Logos)")
        print("-" * 80)
        
        # Star the prediction
        star_buttons = await page.locator('.star-save-btn').count()
        if star_buttons > 0:
            await page.locator('.star-save-btn').first.click()
            await page.wait_for_timeout(1000)
            print("  ✓ Prediction starred")
        else:
            print("  ⚠️  No star button found (may need to wait longer)")
        
        # Navigate to predictions
        await page.locator('#menuBtn').click()
        await page.wait_for_timeout(500)
        await page.locator('#menuPredictions').click()
        await page.wait_for_timeout(2000)
        
        if 'predictions.html' in page.url:
            print("  ✓ On predictions page")
            
            # Check for company logos
            logos = await page.locator('.prediction-card img').count()
            print(f"  ✓ Company logos found: {logos}")
            
            if logos > 0:
                logo_src = await page.locator('.prediction-card img').first.get_attribute('src')
                print(f"  ✓ Logo URL: {logo_src}")
                is_clearbit = 'clearbit.com' in logo_src
                print(f"  ✓ Using Clearbit API: {is_clearbit}")
            else:
                print("  ❌ NO COMPANY LOGOS - Check if logo URL is correct")
            
            # Check for scrollbars (should be hidden)
            scrollbar_test = await page.evaluate('''() => {
                const body = document.body;
                const predPage = document.querySelector('.predictions-page');
                const bodyStyle = window.getComputedStyle(body);
                const pageStyle = predPage ? window.getComputedStyle(predPage) : null;
                
                return {
                    bodyScrollbar: bodyStyle.scrollbarWidth,
                    bodyMsOverflow: bodyStyle.msOverflowStyle,
                    pageScrollbar: pageStyle ? pageStyle.scrollbarWidth : null,
                    pageMsOverflow: pageStyle ? pageStyle.msOverflowStyle : null
                };
            }''')
            
            print(f"  ✓ Scrollbar settings: {scrollbar_test}")
            no_scrollbar = scrollbar_test.get('bodyScrollbar') == 'none' or scrollbar_test.get('pageScrollbar') == 'none'
            print(f"  ✓ Scrollbars hidden: {no_scrollbar}")
            
            await page.wait_for_timeout(5000)
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        print("\nManual verification needed:")
        print("  1. Light theme: Text should be VISIBLE, teal/purple colors")
        print("  2. Monochrome: WHITE TWIN logo, red icons, green button")
        print("  3. Liquid Glass: Pure black/white, no gray, white button with black text")
        print("  4. Index: LOGOUT button should be beside TWIN, not overlapping")
        print("  5. Predictions: No visible scrollbars, Apple logo should show")
        print("  6. Query blocking: Only 1-2 TWIN- messages, not 3+")
        print("="*80)
        
        await page.wait_for_timeout(5000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_all_fixes())
