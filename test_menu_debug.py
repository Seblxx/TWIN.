import asyncio
from playwright.async_api import async_playwright

async def test_menu_debug():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        await page.goto('http://127.0.0.1:5000/index.html', wait_until='networkidle')
        await page.reload(wait_until='networkidle')
        
        # Click menu
        await page.click('.menu-btn')
        await page.wait_for_timeout(500)
        
        # Get the outer HTML of the menu predictions button
        pred_button = page.locator('#menuPredictions')
        outer_html = await pred_button.evaluate("el => el.outerHTML")
        print(f"PREDICTIONS button HTML:\n{outer_html}")
        
        # Get computed style
        display = await pred_button.evaluate("el => getComputedStyle(el).display")
        visibility = await pred_button.evaluate("el => getComputedStyle(el).visibility")
        opacity = await pred_button.evaluate("el => getComputedStyle(el).opacity")
        
        print(f"\nComputed styles:")
        print(f"  display: {display}")
        print(f"  visibility: {visibility}")
        print(f"  opacity: {opacity}")
        
        # Take screenshot
        await page.screenshot(path='playwright_artifacts/menu_debug.png')
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_menu_debug())
