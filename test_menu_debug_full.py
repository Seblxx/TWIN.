import asyncio
from playwright.async_api import async_playwright

async def debug_menu():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, channel="chrome")
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        # Listen for console errors
        page.on("console", lambda msg: print(f"CONSOLE: {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        
        await page.goto('http://127.0.0.1:5000/index.html')
        await page.wait_for_timeout(2000)
        await page.reload(wait_until='networkidle')
        await page.wait_for_timeout(1000)
        
        # Check if menu button exists
        menu_btn_count = await page.locator('.menu-btn').count()
        print(f"\nMenu button found: {menu_btn_count}")
        
        if menu_btn_count > 0:
            print("Clicking menu button...")
            await page.click('.menu-btn')
            await page.wait_for_timeout(1000)
            
            # Check menu visibility
            menu = page.locator('.menu-options')
            is_visible = await menu.is_visible()
            has_open_class = await menu.evaluate("el => el.classList.contains('open')")
            opacity = await menu.evaluate("el => getComputedStyle(el).opacity")
            pointer_events = await menu.evaluate("el => getComputedStyle(el).pointerEvents")
            
            print(f"\nMenu state:")
            print(f"  Visible: {is_visible}")
            print(f"  Has 'open' class: {has_open_class}")
            print(f"  Opacity: {opacity}")
            print(f"  Pointer events: {pointer_events}")
            
            # Check button visibility
            buttons = menu.locator('button')
            button_count = await buttons.count()
            print(f"\nMenu buttons: {button_count}")
            for i in range(button_count):
                btn = buttons.nth(i)
                text = await btn.inner_text()
                visible = await btn.is_visible()
                print(f"  {i+1}. '{text}' - visible: {visible}")
        
        await page.screenshot(path='playwright_artifacts/debug_menu.png', full_page=True)
        print("\nScreenshot saved. Browser staying open for 15 seconds...")
        await page.wait_for_timeout(15000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_menu())
