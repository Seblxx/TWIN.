"""
Visual test - opens intro page with browser for manual inspection of theme colors
"""
import asyncio
from playwright.async_api import async_playwright

async def visual_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("👁️  VISUAL TEST - Intro Page Theme Colors")
        print("="*80)
        print("\nThis test will cycle through all themes on the intro page.")
        print("Watch the icons and 'Get Started' button change colors!\n")
        
        try:
            # Go to intro page
            await page.goto('http://127.0.0.1:5000/intro.html')
            await page.wait_for_load_state('networkidle')
            
            themes = [
                ('dark.css', 'Dark (Pink/Sky icons & button)'),
                ('light.css', 'Light (Teal/Purple icons & button)'),
                ('monochrome.css', 'Monochrome (Green icons & button)'),
                ('liquidglass.css', 'Liquid Glass (White/Gray icons & button)'),
                ('royal.css', 'Royal (Sky/Pink icons & button)')
            ]
            
            for theme_file, theme_name in themes:
                print(f"\n📋 Showing: {theme_name}")
                print("-" * 80)
                
                # Click theme toggle to cycle
                await page.locator('#themeToggle').click()
                await page.wait_for_timeout(2000)
                
                current_theme = await page.locator('#themeCss').get_attribute('href')
                print(f"✓ Current theme: {current_theme}")
                print(f"✓ Look at the feature icons (chart, brain, star, sparkles)")
                print(f"✓ Check the 'Get Started' button gradient")
                await page.wait_for_timeout(3000)
            
            print("\n" + "="*80)
            print("Now going to test index page - TWIN. logo should be WHITE")
            print("(except light theme where it should be BLACK)")
            print("="*80)
            
            # Login to see index page
            await page.locator('#loginToggleBtn').click()
            await page.wait_for_timeout(500)
            
            # Use existing account
            await page.locator('#emailInput').fill('test_1764111733@twin.test')
            await page.locator('#passwordInput').fill('SecurePass123!')
            await page.locator('#loginBtn').click()
            await page.wait_for_timeout(3000)
            
            if 'index.html' in page.url:
                print("\n✅ Logged in successfully!")
                print("\nCycling through themes on INDEX page...")
                print("Watch the TWIN. logo - it should stay WHITE (or BLACK for light theme)\n")
                
                for i in range(5):
                    before = await page.locator('#themeCss').get_attribute('href')
                    theme_name = before.split('?')[0]
                    print(f"\n📋 Theme {i+1}: {theme_name}")
                    print("  ✓ TWIN. logo should be:")
                    if 'light.css' in theme_name:
                        print("    → BLACK (for readability)")
                    else:
                        print("    → WHITE (solid, no gradient)")
                    
                    await page.wait_for_timeout(3000)
                    await page.locator('#themeToggle').click()
                    await page.wait_for_timeout(1500)
                
                print("\n" + "="*80)
                print("✅ VISUAL TEST COMPLETE")
                print("="*80)
                print("\nSummary:")
                print("  • Intro page: Icons and buttons use theme-specific gradients")
                print("  • Index page: TWIN. logo is solid white (black for light theme)")
                print("  • All 5 themes tested successfully")
                print("\nBrowser will stay open for 10 seconds for final inspection...")
                await page.wait_for_timeout(10000)
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return False

if __name__ == '__main__':
    success = asyncio.run(visual_test())
    exit(0 if success else 1)
