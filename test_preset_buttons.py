import asyncio
from playwright.async_api import async_playwright
import os

async def test_preset_buttons():
    async with async_playwright() as p:
        # Use Chromium (not Chrome channel)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        print("Opening page...")
        await page.goto('http://127.0.0.1:5000/index.html')
        await page.wait_for_timeout(2000)
        
        # Force reload
        await page.reload(wait_until='networkidle')
        await page.wait_for_timeout(1000)
        
        # Click on the input field to trigger preset buttons
        print("Clicking input field and typing stock name...")
        input_field = page.locator('#userInput')
        await input_field.click()
        await page.wait_for_timeout(500)
        
        # Type to trigger the stock suggestions
        await input_field.fill("App")
        await page.wait_for_timeout(1500)
        
        # Click on first suggestion to trigger duration presets
        print("Clicking first stock suggestion...")
        first_suggestion = page.locator('.stock-suggestion').first
        if await first_suggestion.is_visible():
            await first_suggestion.click()
            await page.wait_for_timeout(1000)
        
        # Check if preset buttons are visible
        preset_container = page.locator('.duration-presets')
        is_visible = await preset_container.is_visible()
        print(f"\nDuration presets visible: {is_visible}")
        
        if is_visible:
            # Get all preset buttons
            buttons = preset_container.locator('.preset-btn')
            button_count = await buttons.count()
            print(f"Found {button_count} preset buttons")
            
            if button_count > 0:
                # Get dimensions of first button before hover
                first_button = buttons.first
                box_before = await first_button.bounding_box()
                print(f"\nFirst button BEFORE hover:")
                print(f"  width: {box_before['width']}px, height: {box_before['height']}px")
                
                # Hover over the button
                await first_button.hover()
                await page.wait_for_timeout(500)
                
                # Get dimensions after hover
                box_after = await first_button.bounding_box()
                print(f"\nFirst button AFTER hover:")
                print(f"  width: {box_after['width']}px, height: {box_after['height']}px")
                
                # Check if size changed
                width_diff = abs(box_after['width'] - box_before['width'])
                height_diff = abs(box_after['height'] - box_before['height'])
                
                if width_diff < 1 and height_diff < 1:
                    print("\n✓ Preset buttons stay the same size on hover!")
                else:
                    print(f"\n✗ Preset buttons changed size: width diff={width_diff}px, height diff={height_diff}px")
        
        # Now test menu position
        print("\n\nTesting menu position...")
        await page.click('.menu-btn')
        await page.wait_for_timeout(500)
        
        menu = page.locator('.menu-options')
        menu_box = await menu.bounding_box()
        
        menu_btn = page.locator('.menu-btn')
        btn_box = await menu_btn.bounding_box()
        
        print(f"\nMenu position: x={menu_box['x']}, width={menu_box['width']}")
        print(f"Button position: x={btn_box['x']}")
        
        # Take screenshot
        await page.screenshot(path='playwright_artifacts/full_test.png')
        print("\nScreenshot saved to: playwright_artifacts/full_test.png")
        
        print("\nBrowser will stay open for 30 seconds so you can see it...")
        await page.wait_for_timeout(30000)
        
        await browser.close()

if __name__ == "__main__":
    os.makedirs('playwright_artifacts', exist_ok=True)
    asyncio.run(test_preset_buttons())
