import asyncio
from playwright.async_api import async_playwright
import os

async def test_chrome():
    async with async_playwright() as p:
        # Launch Chrome (not Chromium) with visible browser
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome"  # Use actual Chrome
        )
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        print("Opening page in Chrome...")
        await page.goto('http://127.0.0.1:5000/index.html')
        await page.wait_for_timeout(2000)
        
        # Force reload to clear cache
        await page.reload(wait_until='networkidle')
        await page.wait_for_timeout(1000)
        
        print("Clicking menu button...")
        await page.click('.menu-btn')
        await page.wait_for_timeout(1000)
        
        # Take screenshot
        screenshot_path = 'playwright_artifacts/chrome_menu_test.png'
        await page.screenshot(path=screenshot_path, full_page=False)
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Get menu position relative to viewport
        menu = page.locator('.menu-options')
        menu_box = await menu.bounding_box()
        
        menu_btn = page.locator('.menu-btn')
        btn_box = await menu_btn.bounding_box()
        
        print(f"\nMenu button position:")
        print(f"  x: {btn_box['x']}, y: {btn_box['y']}")
        print(f"  width: {btn_box['width']}, height: {btn_box['height']}")
        
        print(f"\nMenu options position:")
        print(f"  x: {menu_box['x']}, y: {menu_box['y']}")
        print(f"  width: {menu_box['width']}, height: {menu_box['height']}")
        
        # Check if menu ends above the button
        menu_bottom = menu_box['y'] + menu_box['height']
        btn_top = btn_box['y']
        
        print(f"\nMenu bottom edge: {menu_bottom}")
        print(f"Button top edge: {btn_top}")
        print(f"Gap between menu and button: {btn_top - menu_bottom}px")
        
        if menu_bottom <= btn_top:
            print("✓ Menu is positioned ABOVE the button")
        else:
            print("✗ Menu OVERLAPS the button")
        
        # Keep browser open for 10 seconds so you can see it
        print("\nBrowser will stay open for 10 seconds...")
        await page.wait_for_timeout(10000)
        
        await browser.close()

if __name__ == "__main__":
    os.makedirs('playwright_artifacts', exist_ok=True)
    asyncio.run(test_chrome())
