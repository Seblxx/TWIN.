import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        # Launch Chromium in headed mode so the browser window is visible
        browser = await p.chromium.launch(headless=False, args=['--start-maximized'])
        context = await browser.new_context(viewport={'width':1280, 'height':900})
        page = await context.new_page()
        # Capture page console messages
        page.on('console', lambda msg: print(f"PAGE CONSOLE: {msg.text}") )
        await page.goto('file:///C:/Users/seblxx/Documents/GitHub/TWIN/index.html')
        # Report initial class lists for menu elements
        menu_opts_class = await page.evaluate("() => document.getElementById('menuOptions') ? document.getElementById('menuOptions').className : ''")
        menu_overlay_class = await page.evaluate("() => document.getElementById('menuOverlay') ? document.getElementById('menuOverlay').className : ''")
        print(f"Initial menuOptions.className: {menu_opts_class}")
        print(f"Initial menuOverlay.className: {menu_overlay_class}")

        # Do not click other UI elements to avoid side-effects
        # Check if menu button is visible
        menu_btn_visible = await page.is_visible('.menu-fab')
        print(f"Menu button visible: {menu_btn_visible}")
        # Click menu button and check menu visibility (headful)
        if menu_btn_visible:
            await page.click('.menu-btn')
            menu_open_visible = await page.is_visible('.menu-options.open')
            print(f"Menu open visible: {menu_open_visible}")
            # Check overlay visibility
            overlay_visible = await page.is_visible('#menuOverlay.open')
            print(f"Menu overlay visible: {overlay_visible}")
            # Keep the browser open a moment so you can observe the UI
            await page.wait_for_timeout(8000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
