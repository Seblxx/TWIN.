"""Quick test to check if Get Started button is accessible"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=500)
    page = browser.new_page()
    
    print("Navigating to intro.html...")
    page.goto("http://localhost:5000/intro.html")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    print("Looking for Get Started button...")
    get_started = page.locator("#getStartedBtn")
    
    is_visible = get_started.is_visible(timeout=5000)
    print(f"Get Started visible: {is_visible}")
    
    if is_visible:
        print("Clicking Get Started...")
        get_started.click()
        time.sleep(3)
        print(f"Current URL: {page.url}")
    else:
        print("Button not found!")
        # Check what's on the page
        print(f"Page title: {page.title()}")
        body_text = page.locator("body").text_content()
        print(f"Body text (first 200 chars): {body_text[:200]}")
    
    input("Press Enter to close...")
    browser.close()
