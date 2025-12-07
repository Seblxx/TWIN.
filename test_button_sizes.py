import time
from playwright.sync_api import sync_playwright

def test_button_sizes():
    """Test TWIN and Analyze buttons to check if they're stretching"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
            java_script_enabled=True
        )
        page = context.new_page()
        
        # Navigate to the app with cache buster
        import random
        cache_buster = random.randint(1000000, 9999999)
        print(f"Loading page (cache buster: {cache_buster})...")
        page.goto(f'http://127.0.0.1:5000/index.html?v={cache_buster}', wait_until='domcontentloaded')
        page.reload(wait_until='domcontentloaded')
        time.sleep(3)
        
        # Take screenshot BEFORE typing anything
        print("\n=== BEFORE INPUT - Taking screenshot ===")
        page.screenshot(path='before_input.png', full_page=True)
        
        # Find the TWIN button (btn-both-inside)
        twin_button = page.locator('.btn-both-inside')
        if twin_button.count() > 0:
            box = twin_button.bounding_box()
            styles = twin_button.evaluate("""(element) => {
                const computed = window.getComputedStyle(element);
                return {
                    width: computed.width,
                    maxWidth: computed.maxWidth,
                    minWidth: computed.minWidth,
                    display: computed.display,
                    position: computed.position,
                    right: computed.right,
                    padding: computed.padding
                };
            }""")
            print("\n=== TWIN BUTTON (BEFORE typing) ===")
            print(f"Actual size: {box['width']:.1f}px x {box['height']:.1f}px")
            print(f"Computed width: {styles['width']}")
            print(f"Computed max-width: {styles['maxWidth']}")
            print(f"Computed min-width: {styles['minWidth']}")
            print(f"Position: {styles['position']}, right: {styles['right']}")
            print(f"Padding: {styles['padding']}")
            
            before_width = box['width']
            
            if box['width'] > 150:
                print(f"⚠️ WARNING: TWIN button is TOO WIDE ({box['width']:.1f}px)")
            else:
                print(f"✓ TWIN button size looks normal")
        else:
            print("✗ TWIN button (.btn-both-inside) not found!")
            before_width = 0
        
        # Now TYPE something and check again
        print("\n=== TYPING 'Apple' ===")
        input_field = page.locator('#userInput')
        input_field.fill('Apple')
        time.sleep(2)
        
        # Click on stock suggestion
        print("\n=== CLICKING STOCK SUGGESTION ===")
        stock_card = page.locator('.stock-card').first
        if stock_card.count() > 0:
            stock_card.click()
            print("✓ Clicked on Apple stock")
            time.sleep(2)
        else:
            print("✗ No stock suggestions found")
        
        # Now the duration presets should be visible
        print("\n=== CHECKING DURATION PRESET BUTTONS ===")
        preset_buttons = page.locator('.preset-btn').all()
        print(f"Found {len(preset_buttons)} preset buttons")
        
        if len(preset_buttons) > 0:
            for i, btn in enumerate(preset_buttons):
                text = btn.text_content()
                box = btn.bounding_box()
                if box:
                    print(f"  Button '{text}': {box['width']:.1f}px x {box['height']:.1f}px")
                    if box['width'] > 200:
                        print(f"    ⚠️⚠️⚠️ THIS BUTTON IS HUGE!")
        
        # Take screenshot AFTER clicking stock
        print("\n=== AFTER STOCK SELECTION - Taking screenshot ===")
        page.screenshot(path='after_stock_click.png', full_page=True)
        
        # Check TWIN button size AFTER typing
        if twin_button.count() > 0:
            box_after = twin_button.bounding_box()
            print("\n=== TWIN BUTTON (AFTER typing) ===")
            print(f"Actual size: {box_after['width']:.1f}px x {box_after['height']:.1f}px")
            print(f"Change: {box_after['width'] - before_width:+.1f}px width")
            
            if abs(box_after['width'] - before_width) > 5:
                print(f"⚠️⚠️⚠️ BUTTON SIZE CHANGED BY {box_after['width'] - before_width:+.1f}px!")
            else:
                print("✓ Button size remained stable")
        
        # Find the Analyze with TWIN- button
        analyze_button = page.locator('.btn.btn-plus')
        if analyze_button.count() > 0:
            box = analyze_button.bounding_box()
            styles = analyze_button.evaluate("""(element) => {
                const computed = window.getComputedStyle(element);
                return {
                    width: computed.width,
                    maxWidth: computed.maxWidth,
                    display: computed.display
                };
            }""")
            print("\n=== ANALYZE WITH TWIN- BUTTON ===")
            print(f"Actual size: {box['width']:.1f}px x {box['height']:.1f}px")
            print(f"Computed width: {styles['width']}")
            print(f"Computed max-width: {styles['maxWidth']}")
            
            if box['width'] > 250:
                print(f"⚠️ WARNING: Analyze button is TOO WIDE ({box['width']:.1f}px)")
            else:
                print(f"✓ Analyze button size looks normal")
        else:
            print("✗ Analyze button (.btn.btn-plus) not found!")
        
        # Take full page screenshot
        print("\nTaking screenshot...")
        page.screenshot(path='button_sizes_test.png', full_page=True)
        print("Screenshot saved: button_sizes_test.png")
        
        # Keep browser open for 30 seconds
        print("\nBrowser will stay open for 30 seconds - CHECK THE BUTTONS!")
        print("Look at the TWIN button and Analyze with TWIN- button sizes")
        time.sleep(30)
        
        browser.close()

if __name__ == '__main__':
    test_button_sizes()
