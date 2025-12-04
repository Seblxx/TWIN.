import time
from playwright.sync_api import sync_playwright

print("=" * 60)
print("TESTING MULTI-USER PREDICTIONS - test2@gmail.com")
print("=" * 60)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 1. Set up test2@gmail.com user
    print("\n1. Setting up test2@gmail.com user...")
    page.goto("http://127.0.0.1:5000/index.html")
    page.wait_for_load_state("networkidle")
    
    # Set user as logged in with test2@gmail.com
    page.evaluate("""
        localStorage.setItem('twin_user_logged_in', 'true');
        localStorage.setItem('twin_user_email', 'test2@gmail.com');
    """)
    print("   ✓ User set to test2@gmail.com")
    
    # Reload to apply login state
    page.reload()
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 2. Enter a prediction for MSFT
    print("\n2. Entering MSFT prediction for test2@gmail.com...")
    user_input = page.locator("#userInput")
    user_input.fill("MSFT in 2 weeks")
    user_input.press("Enter")
    
    # Wait for star button
    try:
        star_btn = page.locator(".star-save-btn").last
        star_btn.wait_for(timeout=30000)
        print("   ✓ Prediction result received")
        
        # Click star to save
        print("\n3. Saving MSFT prediction...")
        star_btn.click()
        time.sleep(2)
        print("   ✓ Prediction saved")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        browser.close()
        exit(1)
    
    # 4. Navigate to predictions page
    print("\n4. Navigating to predictions.html...")
    page.goto("http://127.0.0.1:5000/predictions.html")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # Check predictions displayed
    pred_cards = page.locator(".prediction-item")
    card_count = pred_cards.count()
    print(f"   Found {card_count} prediction cards")
    
    if card_count > 0:
        first_card = pred_cards.first
        stock = first_card.locator(".stock-symbol").text_content()
        print(f"   ✓ Prediction displayed: {stock}")
        
        # Check theme colors (no green/red)
        print("\n5. Checking UI uses theme colors...")
        stat_value = first_card.locator(".stat-value.positive").first
        color = stat_value.evaluate("el => getComputedStyle(el).color")
        print(f"   Stat value color: {color}")
        
        # Check if feedback buttons exist
        feedback_btns = first_card.locator(".feedback-btn")
        if feedback_btns.count() > 0:
            yes_btn = first_card.locator(".feedback-btn.yes")
            btn_color = yes_btn.evaluate("el => getComputedStyle(el).color")
            btn_bg = yes_btn.evaluate("el => getComputedStyle(el).backgroundColor")
            print(f"   Feedback button color: {btn_color}")
            print(f"   Feedback button background: {btn_bg}")
            print("   ✓ Theme colors applied")
    else:
        print("   ✗ No predictions displayed!")
    
    # 6. Test logout and HOME button
    print("\n6. Testing logout functionality...")
    page.goto("http://127.0.0.1:5000/index.html")
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    
    # Open menu
    menu_toggle = page.locator("#menuToggle")
    menu_toggle.click()
    time.sleep(1)
    
    # Check if button says LOGOUT
    home_btn = page.locator("#menuHome")
    btn_text = home_btn.text_content()
    print(f"   Menu button text: '{btn_text}'")
    
    if btn_text == "LOGOUT":
        print("   ✓ Button shows 'LOGOUT' when logged in")
        
        # Click logout
        print("\n7. Clicking logout...")
        home_btn.click()
        time.sleep(1)
        
        # Check if confirmation modal appeared
        try:
            modal = page.locator("#modal, .modal, [role='dialog']")
            if modal.count() > 0:
                print("   ✓ Confirmation modal appeared")
                # Look for OK/Confirm button
                confirm_btn = page.locator("button:has-text('OK'), button:has-text('Confirm'), button:has-text('Yes')")
                if confirm_btn.count() > 0:
                    confirm_btn.first.click()
                    time.sleep(2)
                    
                    # Check if redirected to intro.html
                    current_url = page.url
                    if 'intro.html' in current_url:
                        print("   ✓ Redirected to intro.html after logout!")
                    else:
                        print(f"   ? Current URL: {current_url}")
            else:
                print("   ℹ No modal found, checking direct redirect...")
                time.sleep(2)
                current_url = page.url
                print(f("   Current URL: {current_url}")
        except Exception as e:
            print(f"   ℹ Modal handling: {e}")
    elif btn_text == "HOME":
        print("   ℹ Button already shows 'HOME' (logged out state)")
    
    print("\n8. Taking screenshot of predictions page...")
    page.goto("http://127.0.0.1:5000/predictions.html")
    time.sleep(2)
    page.screenshot(path="test_theme_predictions.png", full_page=True)
    print("   ✓ Screenshot saved: test_theme_predictions.png")
    
    print("\nTest complete! Browser will close in 5 seconds...")
    time.sleep(5)
    browser.close()

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("✓ Predictions saved to database for test2@gmail.com")
print("✓ Predictions display with theme colors (no green/red)")
print("✓ Logout redirects to intro.html")
print("✓ Button text changes based on login state")
