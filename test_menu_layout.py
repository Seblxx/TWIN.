"""
Test the new menu layout and scrollbar fixes:
1. Stock suggestions dropdown - no scrollbar
2. Menu sidebar - appears beside TWIN+ panel
3. LOGOUT button in menu with user email
"""
import asyncio
from playwright.async_api import async_playwright

async def test_menu_layout():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("🎨 TESTING NEW MENU LAYOUT & SCROLLBAR FIXES")
        print("="*80)
        
        test_email = "test_1764112119@twin.test"
        test_password = "SecurePass123!"
        
        # Login first
        print("\n📋 Logging in...")
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        await page.locator('#loginToggleBtn').click()
        await page.wait_for_timeout(500)
        
        await page.locator('#emailInput').fill(test_email)
        await page.locator('#passwordInput').fill(test_password)
        await page.locator('#loginBtn').click()
        await page.wait_for_timeout(3000)
        
        print("✅ Logged in successfully")
        
        # TEST 1: Stock suggestions scrollbar
        print("\n📋 TEST 1: Stock Suggestions Scrollbar")
        print("-" * 80)
        
        # Click on input to show suggestions
        await page.locator('#userInput').click()
        await page.wait_for_timeout(1000)
        
        # Check if stock suggestions are visible
        suggestions_visible = await page.locator('#stockSuggestions').is_visible()
        print(f"  ✓ Stock suggestions visible: {suggestions_visible}")
        
        if suggestions_visible:
            # Check scrollbar styles
            scrollbar_test = await page.evaluate('''() => {
                const suggestions = document.querySelector('.stock-suggestions');
                if (!suggestions) return null;
                const style = window.getComputedStyle(suggestions);
                return {
                    scrollbarWidth: style.scrollbarWidth,
                    msOverflowStyle: style.msOverflowStyle,
                    hasWebkitScrollbar: suggestions.matches('::-webkit-scrollbar')
                };
            }''')
            print(f"  ✓ Scrollbar settings: {scrollbar_test}")
            no_scrollbar = scrollbar_test and scrollbar_test.get('scrollbarWidth') == 'none'
            print(f"  ✓ Scrollbar hidden: {no_scrollbar}")
        
        # Click outside to close suggestions
        await page.locator('.app-title').click()
        await page.wait_for_timeout(500)
        
        # TEST 2: Menu layout
        print("\n📋 TEST 2: Menu Layout (Sidebar Design)")
        print("-" * 80)
        
        # Open menu
        await page.locator('#menuBtn').click()
        await page.wait_for_timeout(1000)
        
        # Check if menu is visible
        menu_visible = await page.locator('#menuOptions.open').is_visible()
        print(f"  ✓ Menu visible: {menu_visible}")
        
        if menu_visible:
            # Check menu position (should be on right side)
            menu_box = await page.locator('#menuOptions').bounding_box()
            viewport = page.viewport_size
            
            if menu_box and viewport:
                is_right_side = menu_box['x'] > viewport['width'] / 2
                print(f"  ✓ Menu positioned on right side: {is_right_side}")
                print(f"  ✓ Menu position: x={menu_box['x']}, width={menu_box['width']}")
                print(f"  ✓ Viewport width: {viewport['width']}")
            
            # Check if user section is visible
            user_section_visible = await page.locator('#menuUserSection').is_visible()
            print(f"  ✓ User section visible: {user_section_visible}")
            
            if user_section_visible:
                # Check user email
                user_email = await page.locator('#menuUserEmail').text_content()
                print(f"  ✓ User email in menu: {user_email}")
                
                # Check logout button
                logout_btn_visible = await page.locator('#menuLogoutBtn').is_visible()
                print(f"  ✓ Logout button visible: {logout_btn_visible}")
            
            # Check that there's no black overlay
            has_overlay = await page.evaluate('''() => {
                // Check if there's any element with semi-transparent black background covering the page
                const elements = document.querySelectorAll('*');
                for (let el of elements) {
                    const style = window.getComputedStyle(el);
                    const bg = style.background;
                    const pos = style.position;
                    if (pos === 'fixed' && bg.includes('rgba(0, 0, 0') && el.id !== 'menuOptions') {
                        const rect = el.getBoundingClientRect();
                        // Check if it covers most of the viewport
                        if (rect.width > window.innerWidth * 0.5 && rect.height > window.innerHeight * 0.5) {
                            return true;
                        }
                    }
                }
                return false;
            }''')
            print(f"  ✓ No black overlay covering page: {not has_overlay}")
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        print("\nManual verification:")
        print("  1. Stock suggestions dropdown should have NO visible scrollbar")
        print("  2. Menu should slide in from RIGHT as a sidebar")
        print("  3. Menu should appear BESIDE TWIN+ panel (not overlay)")
        print("  4. NO black background should cover the page")
        print("  5. User email and LOGOUT button should be at TOP of menu")
        print("="*80)
        
        await page.wait_for_timeout(10000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_menu_layout())
