import asyncio
from playwright.async_api import async_playwright
import os

OUT_DIR = os.path.join(os.getcwd(), 'playwright_artifacts')
os.makedirs(OUT_DIR, exist_ok=True)

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=['--start-maximized'])
        context = await browser.new_context(viewport={'width':1280, 'height':900})
        page = await context.new_page()

        # Print console messages
        page.on('console', lambda msg: print(f"PAGE_CONSOLE: {msg.type} - {msg.text}"))

        # Ensure logged-in state so menu items like PREDICTIONS are visible
        await context.add_init_script("localStorage.setItem('twin_user_logged_in','true'); localStorage.setItem('twin_user_email','tester@example.com');")

        print('Navigating to http://localhost:5000')
        await page.goto('http://localhost:5000', wait_until='load')

        # Wait for menu button
        print('Waiting for menu button')
        await page.wait_for_selector('.menu-fab', timeout=10000)
        await page.screenshot(path=os.path.join(OUT_DIR, 'before_menu_click.png'))
        print('Screenshot saved: before_menu_click.png')

        # Click menu button
        print('Clicking menu button')
        await page.click('.menu-btn')

        # Wait for menu to open
        try:
            await page.wait_for_selector('.menu-options.open', timeout=5000)
            print('Menu opened (found .menu-options.open)')
        except Exception as e:
            print('Menu did not open:', e)

        menu_open_path = os.path.join(OUT_DIR, 'menu_open.png')
        await page.screenshot(path=menu_open_path)
        print('Screenshot saved:', menu_open_path)

        # Try clicking PREDICTIONS menu item
        try:
            pred_btn = await page.wait_for_selector('#menuPredictions', timeout=3000)
            # Ensure it's visible/clickable
            visible = await pred_btn.is_visible()
            enabled = await pred_btn.is_enabled()
            print('Predictions button visible:', visible, 'enabled:', enabled)
            if visible and enabled:
                await pred_btn.click()
                # Wait for navigation
                await page.wait_for_url('**/predictions.html', timeout=5000)
                print('Navigated to predictions.html')
                pred_path = os.path.join(OUT_DIR, 'predictions_page.png')
                await page.screenshot(path=pred_path)
                print('Screenshot saved:', pred_path)
            else:
                print('Predictions button not clickable')
        except Exception as e:
            print('Error clicking PREDICTIONS:', e)

        print('Test complete, keeping browser open for 6s so you can observe')
        await page.wait_for_timeout(6000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
