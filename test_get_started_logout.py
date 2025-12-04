"""
Test Get Started flow and Logout functionality
"""
from playwright.sync_api import sync_playwright, expect
import time

def test_get_started_and_logout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()
        
        print("\n=== TEST 1: Get Started Flow ===")
        page.goto("http://127.0.0.1:5000/intro.html")
        page.wait_for_load_state("networkidle")
        
        # Click Get Started
        print("Clicking 'Get Started' button...")
        get_started = page.locator("#getStartedBtn")
        get_started.click()
        page.wait_for_load_state("networkidle")
        
        # Verify we're on index.html
        print(f"Current URL: {page.url}")
        assert "index.html" in page.url, "Should navigate to index.html"
        
        # Check localStorage - should NOT have user data
        print("\nChecking localStorage for guest session...")
        is_logged_in = page.evaluate("localStorage.getItem('twin_user_logged_in')")
        user_email = page.evaluate("localStorage.getItem('twin_user_email')")
        user_mode = page.evaluate("localStorage.getItem('twin_user_mode')")
        token = page.evaluate("localStorage.getItem('twin_supabase_token')")
        last_query = page.evaluate("localStorage.getItem('twin_last_query')")
        
        print(f"  twin_user_logged_in: {is_logged_in}")
        print(f"  twin_user_email: {user_email}")
        print(f"  twin_user_mode: {user_mode}")
        print(f"  twin_supabase_token: {token}")
        print(f"  twin_last_query: {last_query}")
        
        assert is_logged_in is None, "Should NOT be logged in"
        assert user_email is None, "Should have no user email"
        assert user_mode == 'guest', "Should be in guest mode"
        assert token is None, "Should have no token"
        assert last_query is None, "Should have no saved query"
        
        # Check input field is empty
        user_input = page.locator("#userInput")
        input_value = user_input.input_value()
        print(f"\nInput field value: '{input_value}'")
        assert input_value == "", "Input field should be empty"
        
        # Check menu button shows HOME (not LOGOUT)
        print("\nOpening menu to check button text...")
        menu_btn = page.locator("#menuBtn")
        menu_btn.click()
        page.wait_for_timeout(500)
        
        home_btn = page.locator("#menuHome")
        home_text = home_btn.text_content()
        print(f"Menu button text: '{home_text}'")
        assert home_text == "HOME", "Should show HOME when not logged in"
        
        # Close menu
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        
        print("\n[OK] Get Started flow works correctly - blank slate with no login data")
        
        print("\n=== TEST 2: Login and Logout Flow ===")
        
        # Go back to intro
        page.goto("http://127.0.0.1:5000/intro.html")
        page.wait_for_load_state("networkidle")
        
        # Click "Already a member? Sign in"
        print("Opening login modal...")
        login_toggle = page.locator("#loginToggleBtn")
        login_toggle.click()
        page.wait_for_timeout(500)
        
        # Fill in login credentials
        print("Logging in as dazrini@gmail.com...")
        email_input = page.locator("#emailInput")
        password_input = page.locator("#passwordInput")
        login_btn = page.locator("#loginBtn")
        
        email_input.fill("dazrini@gmail.com")
        password_input.fill("gummybear")
        login_btn.click()
        
        # Wait for redirect to index.html
        page.wait_for_url("**/index.html", timeout=10000)
        print(f"Logged in! Current URL: {page.url}")
        
        # Verify logged in state
        is_logged_in = page.evaluate("localStorage.getItem('twin_user_logged_in')")
        user_email = page.evaluate("localStorage.getItem('twin_user_email')")
        print(f"\n  twin_user_logged_in: {is_logged_in}")
        print(f"  twin_user_email: {user_email}")
        assert is_logged_in == 'true', "Should be logged in"
        assert user_email == 'dazrini@gmail.com', "Should have correct email"
        
        # Open menu and check button shows LOGOUT
        print("\nOpening menu to check LOGOUT button...")
        menu_btn.click()
        page.wait_for_timeout(500)
        
        logout_btn = page.locator("#menuHome")
        logout_text = logout_btn.text_content()
        print(f"Menu button text: '{logout_text}'")
        assert logout_text == "LOGOUT", "Should show LOGOUT when logged in"
        
        # Click LOGOUT
        print("\nClicking LOGOUT button...")
        logout_btn.click()
        page.wait_for_timeout(500)
        
        # Check if confirmation modal appeared
        modal = page.locator("#modalOverlay")
        modal_visible = modal.evaluate("el => el.classList.contains('open')")
        print(f"Confirmation modal visible: {modal_visible}")
        assert modal_visible, "Logout confirmation modal should appear"
        
        # Click Yes to confirm
        print("Clicking 'Yes' to confirm logout...")
        confirm_yes = page.locator("#confirmYes")
        
        # Add console logging to see what happens
        page.on("console", lambda msg: print(f"BROWSER: {msg.text}"))
        
        confirm_yes.click()
        
        # Wait longer for navigation to complete (setTimeout is 10ms + navigation time)
        page.wait_for_timeout(2000)
        
        # Check current URL manually
        current_url = page.url
        print(f"Current URL after clicking Yes: {current_url}")
        
        # Wait for redirect to intro.html if not there yet
        if "intro.html" not in current_url:
            print("Waiting for redirect...")
            try:
                page.wait_for_url("**/intro.html", timeout=5000)
                current_url = page.url
                print(f"Redirected to: {current_url}")
            except:
                print("ERROR: Redirect did not happen!")
                is_logged_in = page.evaluate("localStorage.getItem('twin_user_logged_in')")
                print(f"  twin_user_logged_in after logout attempt: {is_logged_in}")
                raise AssertionError("Logout redirect failed!")
        print(f"Logged out! Current URL: {page.url}")
        
        # Verify logout cleared data
        print("\nVerifying logout cleared all user data...")
        is_logged_in = page.evaluate("localStorage.getItem('twin_user_logged_in')")
        user_email = page.evaluate("localStorage.getItem('twin_user_email')")
        token = page.evaluate("localStorage.getItem('twin_supabase_token')")
        
        print(f"  twin_user_logged_in: {is_logged_in}")
        print(f"  twin_user_email: {user_email}")
        print(f"  twin_supabase_token: {token}")
        
        assert is_logged_in is None, "Should have cleared login flag"
        assert user_email is None, "Should have cleared email"
        assert token is None, "Should have cleared token"
        
        print("\n[OK] Logout flow works correctly - redirects to intro.html and clears all data")
        
        print("\n=== TEST 3: Modal Styling Consistency ===")
        
        # Go to index.html as guest
        page.goto("http://127.0.0.1:5000/intro.html")
        page.wait_for_load_state("networkidle")
        
        get_started = page.locator("#getStartedBtn")
        get_started.click()
        page.wait_for_load_state("networkidle")
        
        # Open menu and click HOME to trigger confirm modal
        print("\nOpening confirm modal to check styling...")
        menu_btn = page.locator("#menuBtn")
        menu_btn.click()
        page.wait_for_timeout(500)
        
        home_btn = page.locator("#menuHome")
        home_btn.click()
        page.wait_for_timeout(500)
        
        # Check modal styling
        confirm_yes = page.locator("#confirmYes")
        confirm_no = page.locator("#confirmNo")
        
        # Wait for buttons to be visible
        expect(confirm_yes).to_be_visible()
        expect(confirm_no).to_be_visible()
        
        yes_bg = confirm_yes.evaluate("el => window.getComputedStyle(el).background")
        yes_padding = confirm_yes.evaluate("el => window.getComputedStyle(el).padding")
        yes_border_radius = confirm_yes.evaluate("el => window.getComputedStyle(el).borderRadius")
        
        print(f"\n'Yes' button styling:")
        print(f"  Background: {yes_bg[:80]}...")
        print(f"  Padding: {yes_padding}")
        print(f"  Border radius: {yes_border_radius}")
        
        # Should have gradient background
        assert "gradient" in yes_bg.lower() or "48b6ff" in yes_bg or "ff5ea8" in yes_bg, "Yes button should have gradient"
        assert "16px" in yes_padding, "Should have 16px padding"
        assert "12px" in yes_border_radius, "Should have 12px border radius"
        
        print("\n[OK] Modal styling matches login modal")
        
        # Close browser
        page.keyboard.press("Escape")
        time.sleep(1)
        
        browser.close()
        print("\n" + "="*50)
        print("ALL TESTS PASSED!")
        print("="*50)

if __name__ == "__main__":
    test_get_started_and_logout()
