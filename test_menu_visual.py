import asyncio
from playwright.async_api import async_playwright
import os

async def test_menu_visual():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        print("Navigating to TWIN main app...")
        # Force refresh with cache bypass
        await page.goto('http://127.0.0.1:5000/index.html', wait_until='networkidle')
        await page.reload(wait_until='networkidle')
        await page.wait_for_timeout(1000)
        
        # Wait for page to be ready
        await page.wait_for_selector('.menu-btn', timeout=10000)
        print("Page loaded")
        
        # Take initial screenshot
        await page.screenshot(path='playwright_artifacts/menu_before_open.png')
        print("Captured initial state")
        
        # Click menu button to open menu
        print("Opening menu...")
        await page.click('.menu-btn')
        await page.wait_for_timeout(500)  # Wait for fade-in animation
        
        # Take screenshot with menu open
        await page.screenshot(path='playwright_artifacts/menu_open.png')
        print("Captured menu open state")
        
        # Get menu styling details
        menu_options = page.locator('.menu-options')
        is_visible = await menu_options.is_visible()
        print(f"\nMenu visible: {is_visible}")
        
        if is_visible:
            # Get computed styles
            bottom = await menu_options.evaluate("el => getComputedStyle(el).bottom")
            right = await menu_options.evaluate("el => getComputedStyle(el).right")
            gap = await menu_options.evaluate("el => getComputedStyle(el).gap")
            background = await menu_options.evaluate("el => getComputedStyle(el).background")
            backdrop_filter = await menu_options.evaluate("el => getComputedStyle(el).backdropFilter")
            
            print(f"\nMenu positioning:")
            print(f"  bottom: {bottom}")
            print(f"  right: {right}")
            print(f"  gap: {gap}")
            print(f"  background: {background}")
            print(f"  backdrop-filter: {backdrop_filter}")
            
            # Get button styles
            first_button = menu_options.locator('button').first
            font_size = await first_button.evaluate("el => getComputedStyle(el).fontSize")
            letter_spacing = await first_button.evaluate("el => getComputedStyle(el).letterSpacing")
            color = await first_button.evaluate("el => getComputedStyle(el).color")
            
            print(f"\nMenu button text styling:")
            print(f"  font-size: {font_size}")
            print(f"  letter-spacing: {letter_spacing}")
            print(f"  color: {color}")
            
            # Get all button texts
            all_buttons = menu_options.locator('button')
            button_count = await all_buttons.count()
            print(f"\nMenu buttons (total: {button_count}):")
            for i in range(button_count):
                button = all_buttons.nth(i)
                is_vis = await button.is_visible()
                text = await button.inner_text()
                print(f"  {i+1}. {text} (visible: {is_vis})")
            
            # Get user name styles
            user_name = page.locator('.menu-user-name')
            user_name_exists = await user_name.count() > 0
            if user_name_exists:
                is_user_visible = await user_name.is_visible()
                print(f"\nUser name element exists: {user_name_exists}, visible: {is_user_visible}")
                if is_user_visible:
                    user_font_size = await user_name.evaluate("el => getComputedStyle(el).fontSize")
                    user_margin_bottom = await user_name.evaluate("el => getComputedStyle(el).marginBottom")
                    print(f"User name styling:")
                    print(f"  font-size: {user_font_size}")
                    print(f"  margin-bottom: {user_margin_bottom}")
            else:
                print("\nUser name element not found (expected for non-logged in state)")
            
            # Get logout button margin
            logout_btn = page.locator('.menu-logout-btn')
            logout_exists = await logout_btn.count() > 0
            if logout_exists:
                is_logout_visible = await logout_btn.is_visible()
                print(f"\nLogout button exists: {logout_exists}, visible: {is_logout_visible}")
                if is_logout_visible:
                    logout_margin = await logout_btn.evaluate("el => getComputedStyle(el).marginBottom")
                    print(f"Logout button:")
                    print(f"  margin-bottom: {logout_margin}")
            else:
                print("\nLogout button not found (expected for non-logged in state)")
        
        print("\nScreenshots saved to playwright_artifacts/")
        print("Check menu_open.png to see the current menu appearance")
        
        await browser.close()

if __name__ == "__main__":
    # Create artifacts directory if it doesn't exist
    os.makedirs('playwright_artifacts', exist_ok=True)
    asyncio.run(test_menu_visual())
