"""
Simple test to just open the app and let you manually test
"""
import asyncio
from playwright.async_api import async_playwright

async def open_app():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("🌐 OPENING APP FOR MANUAL TESTING")
        print("="*80)
        
        # Open intro page
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        print("\n✅ App opened at intro.html")
        print("\nMANUAL TEST CHECKLIST:")
        print("="*80)
        print("1. INTRO PAGE THEME COLORS:")
        print("   - Click theme circle (bottom-left) to cycle themes")
        print("   - LIGHT: Black TWIN, vibrant purple→pink button, green→blue icons")
        print("   - MONOCHROME: Black TWIN, red→dark red button, red→green icons")
        print("   - LIQUID GLASS: Black TWIN, solid black button, white icons")
        print()
        print("2. LOGIN:")
        print("   - Click 'Sign In' button")
        print("   - Email: test_1764112119@twin.test")
        print("   - Password: SecurePass123!")
        print("   - Login and verify redirect to index.html")
        print()
        print("3. QUERY & PREDICTIONS:")
        print("   - Try query: 'Apple in 3 days'")
        print("   - Click TWIN button")
        print("   - Star the prediction (click star icon)")
        print("   - Open menu (hamburger) → PREDICTIONS")
        print("   - Verify: No visible scrollbars")
        print("   - Verify: Company logo shows (Apple logo)")
        print()
        print("="*80)
        print("⏳ Browser will stay open for 5 minutes...")
        print("   Close this terminal to exit")
        print("="*80)
        
        # Keep browser open for 5 minutes
        await page.wait_for_timeout(300000)
        
        await browser.close()

if __name__ == '__main__':
    asyncio.run(open_app())
