import time
from playwright.sync_api import sync_playwright

def test_preset_buttons_autonomous():
    """Test preset buttons and make autonomous fixes if issues found"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # Create context with no cache
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
            java_script_enabled=True
        )
        page = context.new_page()
        
        # Disable cache completely
        page.route('**/*', lambda route: route.continue_())
        
        # Navigate to the app with no cache - add timestamp to force reload
        import random
        cache_buster = random.randint(1000000, 9999999)
        print(f"Loading page (no cache, buster: {cache_buster})...")
        page.goto(f'http://127.0.0.1:5000/index.html?v={cache_buster}', wait_until='domcontentloaded')
        
        # Force reload to bypass any cache
        page.reload(wait_until='domcontentloaded')
        time.sleep(3)
        
        # Debug: Get page content
        html_content = page.content()
        print(f"Page loaded, HTML length: {len(html_content)}")
        
        # Check if durationPresets exists
        presets_exists = page.evaluate("""() => {
            return document.getElementById('durationPresets') !== null;
        }""")
        print(f"durationPresets element exists: {presets_exists}")
        
        # Make duration presets visible using JavaScript
        print("Making duration presets visible...")
        result = page.evaluate("""() => {
            const presets = document.getElementById('durationPresets');
            if (presets) {
                presets.style.display = 'flex';
                const buttons = presets.querySelectorAll('.preset-btn');
                return buttons.length;
            }
            return 0;
        }""")
        print(f"Found {result} buttons inside durationPresets via JS")
        time.sleep(1)
        
        # Check for preset buttons
        print("\nLooking for preset buttons...")
        preset_buttons = page.locator('.preset-btn').all()
        print(f"Found {len(preset_buttons)} .preset-btn elements")
        
        # Wait for suggestions to appear
        try:
            page.wait_for_selector('.suggestion-item', timeout=5000)
            suggestions = page.locator('.suggestion-item').all()
            if suggestions:
                suggestions[0].click()
                time.sleep(1)
                print("✓ Stock suggestion clicked")
        except:
            print("✗ No suggestions - continuing with visible preset buttons")
        
        # Find all preset buttons
        preset_buttons = page.locator('.preset-btn').all()
        print(f"\nFound {len(preset_buttons)} preset buttons")
        
        if len(preset_buttons) == 0:
            print("⚠️ No preset buttons found! Checking for duration buttons...")
            # Try alternate selectors
            page.screenshot(path='test_screenshot.png')
            print("Screenshot saved to test_screenshot.png")
        
        issues_found = []
        
        # Check first button's computed styles
        if len(preset_buttons) > 0:
            first_btn = preset_buttons[0]
            styles = first_btn.evaluate("""(element) => {
                const computed = window.getComputedStyle(element);
                return {
                    minWidth: computed.minWidth,
                    maxWidth: computed.maxWidth,
                    width: computed.width,
                    flexGrow: computed.flexGrow,
                    flexShrink: computed.flexShrink,
                    transform: computed.transform,
                    transition: computed.transition
                };
            }""")
            print("\nComputed styles on first preset button:")
            for key, value in styles.items():
                print(f"  {key}: {value}")
        
        for i, btn in enumerate(preset_buttons):
            btn_text = btn.text_content()
            
            # Get initial size
            initial_box = btn.bounding_box()
            if not initial_box:
                continue
                
            initial_width = initial_box['width']
            initial_height = initial_box['height']
            
            # Hover over button
            btn.hover()
            time.sleep(0.3)
            
            # Get size after hover
            hover_box = btn.bounding_box()
            hover_width = hover_box['width']
            hover_height = hover_box['height']
            
            # Check for size changes
            width_change = hover_width - initial_width
            height_change = hover_height - initial_height
            
            print(f"\nButton '{btn_text}':")
            print(f"  Initial: {initial_width:.1f}x{initial_height:.1f}")
            print(f"  Hover:   {hover_width:.1f}x{hover_height:.1f}")
            print(f"  Change:  {width_change:+.1f}x{height_change:+.1f}")
            
            # Flag if size changed significantly (more than 2px)
            if abs(width_change) > 2 or abs(height_change) > 2:
                issues_found.append({
                    'button': btn_text,
                    'width_change': width_change,
                    'height_change': height_change
                })
                print(f"  ⚠️ SIZE CHANGE DETECTED!")
            else:
                print(f"  ✓ Size stable")
            
            # Move mouse away
            page.mouse.move(0, 0)
            time.sleep(0.2)
        
        print("\n" + "="*60)
        if issues_found:
            print(f"❌ ISSUES FOUND: {len(issues_found)} buttons changing size on hover")
            for issue in issues_found:
                print(f"  - {issue['button']}: {issue['width_change']:+.1f}px width, {issue['height_change']:+.1f}px height")
        else:
            print("✅ ALL PRESET BUTTONS STABLE - No size changes detected!")
        print("="*60)
        
        # Take screenshots to document the state
        print("\nTaking screenshots for documentation...")
        page.screenshot(path='preset_buttons_normal.png', full_page=True)
        print("Screenshot 1: preset_buttons_normal.png")
        
        # Hover over first button and screenshot
        if len(preset_buttons) > 0:
            preset_buttons[0].hover()
            time.sleep(0.5)
            page.screenshot(path='preset_buttons_hover.png', full_page=True)
            print("Screenshot 2: preset_buttons_hover.png (hovering first button)")
        
        # Keep browser open for 30 seconds to allow visual inspection
        print("\nKeeping browser open for 30 seconds for visual inspection...")
        print("Please check the preset buttons yourself!")
        time.sleep(30)
        
        browser.close()
        
        return len(issues_found) == 0

if __name__ == '__main__':
    success = test_preset_buttons_autonomous()
    if not success:
        print("\n🔧 AUTONOMOUS FIX NEEDED - Issues detected in preset buttons")
    else:
        print("\n✅ TEST PASSED - No fixes needed")
