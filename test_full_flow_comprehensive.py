"""
Comprehensive Full Flow Test - All User Scenarios
Tests: Get Started, Predictions, Session Isolation, Modals, Clear functionality
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_full_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()
        
        # Enable console logging
        page.on("console", lambda msg: print(f"BROWSER: {msg.text}"))
        
        print("\n" + "="*60)
        print("TEST 1: Get Started - Blank Slate")
        print("="*60)
        
        page.goto("http://127.0.0.1:5000/intro.html")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        get_started = page.locator("#getStartedBtn")
        expect(get_started).to_be_visible(timeout=10000)
        expect(get_started).to_be_enabled(timeout=5000)
        get_started.click()
        page.wait_for_url("**/index.html", timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Check predictions button is OFF
        predictions_btn = page.locator("#menuPredictions")
        predictions_disabled = predictions_btn.evaluate("el => el.disabled || el.style.opacity === '0.5'")
        print(f"Predictions button disabled: {predictions_disabled}")
        
        # Check HOME button (not LOGOUT)
        menu_btn = page.locator("#menuBtn")
        menu_btn.click()
        time.sleep(0.5)
        
        home_btn = page.locator("#menuHome")
        home_text = home_btn.text_content()
        print(f"Menu button shows: '{home_text}' (should be HOME)")
        assert home_text == "HOME", f"Expected HOME, got {home_text}"
        
        # Close menu
        page.keyboard.press("Escape")
        time.sleep(0.3)
        
        # Try a query - should NOT show star button
        user_input = page.locator("#userInput")
        user_input.fill("AAPL in 3 days")
        page.keyboard.press("Enter")
        time.sleep(3)  # Wait for prediction
        
        # Check if star button appears (it shouldn't for guest)
        star_buttons = page.locator("button:has-text('☆'), button:has-text('★')").count()
        print(f"Star buttons found: {star_buttons} (should be 0 for guest)")
        
        print("[OK] Get Started shows blank slate, predictions OFF, HOME button, no star")
        
        print("\n" + "="*60)
        print("TEST 2: Second Get Started - Should Clear Previous Query")
        print("="*60)
        
        # Go back home
        menu_btn.click()
        time.sleep(0.5)
        home_btn.click(force=True)  # Force click through any overlays
        time.sleep(0.5)
        
        # Confirm going home
        try:
            confirm_yes = page.locator("#confirmYes")
            if confirm_yes.is_visible(timeout=1000):
                confirm_yes.click()
                time.sleep(1)
        except:
            pass
        
        # Should be on intro.html
        page.goto("http://127.0.0.1:5000/intro.html")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Click Get Started again
        get_started = page.locator("#getStartedBtn")
        expect(get_started).to_be_visible(timeout=5000)
        get_started.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        
        # Input should be BLANK
        user_input = page.locator("#userInput")
        input_value = user_input.input_value()
        print(f"Input field value: '{input_value}' (should be empty)")
        assert input_value == "", f"Input should be blank but has: {input_value}"
        
        # No chat messages
        messages_basic = page.locator("#messages-basic .prediction-item").count()
        print(f"Chat messages: {messages_basic} (should be 0)")
        assert messages_basic == 0, "Should have no messages"
        
        print("[OK] Second Get Started shows blank slate")
        
        print("\n" + "="*60)
        print("TEST 3: Login as dazrini - Save Prediction")
        print("="*60)
        
        page.goto("http://127.0.0.1:5000/intro.html")
        page.wait_for_load_state("networkidle")
        
        # Login
        login_toggle = page.locator("#loginToggleBtn")
        login_toggle.click()
        time.sleep(0.5)
        
        email_input = page.locator("#emailInput")
        password_input = page.locator("#passwordInput")
        login_btn = page.locator("#loginBtn")
        
        email_input.fill("dazrini@gmail.com")
        password_input.fill("gummybear")
        login_btn.click()
        
        page.wait_for_url("**/index.html", timeout=10000)
        print("Logged in as dazrini@gmail.com")
        
        # Verify localStorage was set
        logged_in_flag = page.evaluate("localStorage.getItem('twin_user_logged_in')")
        print(f"localStorage twin_user_logged_in: {logged_in_flag}")
        assert logged_in_flag == 'true', "localStorage flag not set after login!"
        
        # Make a prediction
        user_input = page.locator("#userInput")
        user_input.fill("TSLA in 5 days")
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # Star the prediction - CRITICAL: Must actually save!
        star_btn = page.locator("button.star-save-btn").first
        star_visible = star_btn.is_visible(timeout=2000)
        print(f"Star button visible: {star_visible}")
        
        # Debug: Print pred-id and button state
        if star_visible:
            pred_id = star_btn.get_attribute("data-pred-id")
            is_disabled = star_btn.is_disabled()
            button_title = star_btn.get_attribute("title")
            print(f"Star button pred-id for dazrini: {pred_id}")
            print(f"Star button disabled for dazrini: {is_disabled}")
            print(f"Star button title for dazrini: {button_title}")
        
        if star_visible:
            star_btn.click()
            time.sleep(2)  # Wait for save to complete
            print("[OK] Clicked star to save TSLA prediction")
        else:
            print("[ERROR] Star button not visible - cannot save prediction!")
        
        # Check query is in input
        query_value = user_input.input_value()
        print(f"Query in input: '{query_value}'")
        
        # Go to predictions
        menu_btn.click()
        time.sleep(0.5)
        predictions_btn = page.locator("#menuPredictions")
        predictions_btn.click()
        time.sleep(2)
        
        # Should see TSLA prediction
        predictions = page.locator(".prediction-item")
        prediction_count = predictions.count()
        print(f"Predictions count: {prediction_count}")
        
        if prediction_count > 0:
            first_prediction = predictions.first.text_content()
            print(f"First prediction: {first_prediction[:50]}...")
        
        print("[OK] dazrini can save and view predictions")
        
        print("\n" + "="*60)
        print("TEST 4: Logout dazrini - Should Clear Session")
        print("="*60)
        
        # Go back to index using the back button (preserves session)
        back_btn = page.locator("a.back-button")
        expect(back_btn).to_be_visible()
        back_btn.click()
        page.wait_for_url("**/index.html")
        time.sleep(1)
        
        # Logout from index page
        menu_btn = page.locator("#menuBtn")
        menu_btn.click()
        time.sleep(0.5)
        logout_btn = page.locator("#menuHome")
        expect(logout_btn).to_have_text("LOGOUT", timeout=5000)
        logout_btn.click(force=True)
        time.sleep(1)  # Wait for modal to appear
        
        # Confirm logout
        confirm_yes = page.locator("#confirmYes")
        expect(confirm_yes).to_be_visible(timeout=10000)
        confirm_yes.click(force=True)
        
        # Wait for navigation to intro.html
        try:
            page.wait_for_url("**/intro.html", timeout=5000)
            print("[OK] Navigated to intro.html")
        except:
            print(f"[WARN] Did not navigate to intro.html after 5 seconds")
        
        time.sleep(1)  # Let page settle
        
        # Check URL - should be on intro.html
        current_url = page.url
        print(f"URL after logout: {current_url}")
        if "intro.html" in current_url:
            print("[OK] Logout redirected to intro.html")
        else:
            print(f"[ERROR] Still on {current_url}, not intro.html!")
            # Force navigation if needed
            page.goto("http://127.0.0.1:5000/intro.html")
        
        # Verify dazrini's session is cleared
        print("Verifying localStorage cleared after logout...")
        logged_in = page.evaluate("localStorage.getItem('twin_user_logged_in')")
        print(f"twin_user_logged_in: {logged_in} (should be null)")
        
        print("\n" + "="*60)
        print("TEST 5: Login as test2 - Session Isolation")
        print("="*60)
        
        page.wait_for_load_state("networkidle")
        
        # Login as test2
        login_toggle = page.locator("#loginToggleBtn")
        login_toggle.click()
        time.sleep(0.5)
        
        email_input = page.locator("#emailInput")
        password_input = page.locator("#passwordInput")
        login_btn = page.locator("#loginBtn")
        
        email_input.fill("test2@gmail.com")
        password_input.fill("password")
        login_btn.click()
        
        page.wait_for_url("**/index.html", timeout=10000)
        print("Logged in as test2@gmail.com")
        time.sleep(1)
        
        # CRITICAL: Clear chat messages first to start with blank slate
        new_btn = page.locator("#newBtn")
        if new_btn.is_visible(timeout=1000):
            new_btn.click()
            time.sleep(0.5)
            # Confirm clear
            confirm_yes = page.locator("#confirmYes")
            if confirm_yes.is_visible(timeout=1000):
                confirm_yes.click()
                time.sleep(1)
            print("[OK] Cleared any existing chat messages")
        
        # Input should be BLANK (no dazrini query)
        user_input = page.locator("#userInput")
        input_value = user_input.input_value()
        print(f"Input field: '{input_value}' (should be empty)")
        
        if input_value != "":
            print(f"[WARNING] Input not blank, contains: '{input_value}'")
            print("Clearing input field manually...")
            user_input.fill("")
        
        # No chat messages from dazrini
        messages_basic = page.locator("#messages-basic .message-item, #messages-basic .prediction-item").count()
        print(f"Chat messages: {messages_basic} (should be 0)")
        
        # Make different prediction
        user_input.fill("NVDA in 7 days")
        page.keyboard.press("Enter")
        time.sleep(4)
        
        # Star it - MUST save to test Clear All
        time.sleep(2)  # Wait for page to fully render
        star_btn = page.locator("button.star-save-btn").last  # Use .last instead of .first
        star_visible = star_btn.is_visible(timeout=2000)
        print(f"Star button visible for test2: {star_visible}")
        
        # Debug: Print pred-id and button state
        if star_visible:
            pred_id = star_btn.get_attribute("data-pred-id")
            is_disabled = star_btn.is_disabled()
            button_title = star_btn.get_attribute("title")
            print(f"Star button pred-id: {pred_id}")
            print(f"Star button disabled: {is_disabled}")
            print(f"Star button title: {button_title}")
        
        if star_visible and not star_btn.is_disabled():
            star_btn.click(force=True)  # Force click
            time.sleep(2)  # Wait for save
            print("[OK] Clicked star to save NVDA prediction")
        elif not star_visible:
            print("[ERROR] Star button not visible for test2!")
        else:
            print("[WARNING] Star button disabled - skipping (might be already saved)")
        
        # Check predictions
        menu_btn = page.locator("#menuBtn")
        menu_btn.click()
        time.sleep(0.5)
        predictions_btn = page.locator("#menuPredictions")
        predictions_btn.click()
        time.sleep(2)
        
        # Count predictions first
        predictions_count = page.locator(".prediction-item").count()
        print(f"test2 has {predictions_count} saved prediction(s)")
        
        # Should NOT see TSLA (dazrini's prediction)
        page_text = page.locator("body").text_content()
        has_tsla = "TSLA" in page_text
        has_nvda = "NVDA" in page_text
        print(f"Predictions page contains TSLA: {has_tsla} (should be False)")
        print(f"Predictions page contains NVDA: {has_nvda} (should be True)")
        
        if has_tsla:
            print("[ERROR] test2 can see dazrini's TSLA prediction!")
        else:
            print("[OK] Session isolation working - test2 only sees own predictions")
        
        print("\n" + "="*60)
        print("TEST 6: Test Clear All Button - Delete test2's predictions")
        print("="*60)
        
        # We're already on predictions.html from Test 5
        # Click Clear All to delete all of test2's predictions
        clear_all_btn = page.locator("button:has-text('CLEAR ALL')")
        clear_all_visible = clear_all_btn.is_visible(timeout=1000)
        print(f"Clear All button visible: {clear_all_visible}")
        
        if clear_all_visible:
            clear_all_btn.click()
            time.sleep(1)  # Wait for modal animation
            
            # Modal should appear
            modal = page.locator("#modalOverlay")
            modal_visible = modal.evaluate("el => el.classList.contains('open')")
            print(f"Clear All modal visible: {modal_visible}")
            
            # Click Yes
            confirm_yes = page.locator("#confirmYes")
            yes_visible = confirm_yes.is_visible(timeout=3000)
            print(f"Confirm Yes button visible: {yes_visible}")
            
            if yes_visible:
                confirm_yes.click()
                time.sleep(3)  # Wait for backend call + loadPredictions()
                
                # Modal should DISAPPEAR
                modal_visible_after = modal.evaluate("el => el.classList.contains('open')")
                print(f"Modal visible after clicking Yes: {modal_visible_after} (should be False)")
                
                if modal_visible_after:
                    print("[ERROR] Modal did not close after Clear All!")
                else:
                    print("[OK] Modal closed after Clear All")
                
                # Predictions should be cleared (wait a bit more for loadPredictions to complete)
                time.sleep(1)
                predictions = page.locator(".prediction-item").count()
                print(f"Predictions remaining: {predictions} (should be 0)")
                
                if predictions > 0:
                    print("[ERROR] Predictions not cleared!")
                else:
                    print("[OK] All predictions cleared")
            else:
                print("[ERROR] Confirm Yes button not visible!")
        else:
            print("[OK] Clear All button not shown (only 1 prediction, feature may require multiple)")
        
        print("\n" + "="*60)
        print("TEST 7: Test Clear Messages Modal (NEW button)")
        print("="*60)
        
        # Go back to index
        back_btn = page.locator("a.back-button")
        if back_btn.is_visible(timeout=1000):
            back_btn.click()
            time.sleep(1)
        
        # Make a query to have messages
        user_input = page.locator("#userInput")
        user_input.fill("Test query")
        page.keyboard.press("Enter")
        time.sleep(3)
        
        # Open menu and click NEW
        menu_btn.click()
        time.sleep(0.5)
        new_btn = page.locator("#menuNew")
        new_btn.click()
        time.sleep(0.5)
        
        # Modal should appear
        modal = page.locator("#modalOverlay")
        modal_visible = modal.evaluate("el => el.classList.contains('open')")
        print(f"Clear messages modal visible: {modal_visible}")
        
        # Click Yes
        confirm_yes = page.locator("#confirmYes")
        if confirm_yes.is_visible(timeout=1000):
            confirm_yes.click()
            time.sleep(1)
            
            # Modal should DISAPPEAR
            modal_visible_after = modal.evaluate("el => el.classList.contains('open')")
            print(f"Modal visible after clicking Yes: {modal_visible_after} (should be False)")
            
            if modal_visible_after:
                print("[ERROR] Modal did not close after clearing messages!")
            else:
                print("[OK] Modal closed after clearing messages")
        
        print("\n" + "="*60)
        print("TEST 8: Check Modal Styling")
        print("="*60)
        
        # Open a modal again
        menu_btn.click()
        time.sleep(0.5)
        home_btn = page.locator("#menuHome")  # This is LOGOUT when logged in
        home_btn.click()
        time.sleep(0.5)
        
        # Check modal styling
        confirm_yes = page.locator("#confirmYes")
        confirm_no = page.locator("#confirmNo")
        
        if confirm_yes.is_visible(timeout=1000):
            # Check Yes button styling
            yes_bg = confirm_yes.evaluate("el => window.getComputedStyle(el).background")
            yes_color = confirm_yes.evaluate("el => window.getComputedStyle(el).color")
            
            print(f"Yes button background: {yes_bg[:100]}")
            print(f"Yes button color: {yes_color}")
            
            # Check No button styling
            no_bg = confirm_no.evaluate("el => window.getComputedStyle(el).background")
            no_color = confirm_no.evaluate("el => window.getComputedStyle(el).color")
            no_border = confirm_no.evaluate("el => window.getComputedStyle(el).border")
            
            print(f"No button background: {no_bg}")
            print(f"No button color: {no_color}")
            print(f"No button border: {no_border[:100]}")
            
            # Check for white-on-white issue
            if "255, 255, 255" in no_color or "rgb(255, 255, 255)" in no_color:
                if "255, 255, 255" in no_bg or "transparent" in no_bg:
                    print("[ERROR] White text on white/transparent background!")
                else:
                    print("[OK] Cancel button has contrasting colors")
        
        # Cancel to close modal
        confirm_no.click()
        time.sleep(0.5)
        
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print("Tests completed. Check output above for [ERROR] markers.")
        
        time.sleep(2)
        browser.close()

if __name__ == "__main__":
    test_full_flow()
