"""
Quick test to show the menu display
"""

import sys
import time

sys.path.insert(0, r'C:\Users\seblxx\Documents\GitHub\TWIN\.venv\Lib\site-packages')

from playwright.sync_api import sync_playwright

def test_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page()
        
        print("\n=== Testing Menu Display ===\n")
        
        # Navigate to index page
        print("1. Opening main page...")
        page.goto('http://127.0.0.1:5000/index.html')
        page.wait_for_load_state('networkidle')
        time.sleep(2)
        
        # Click menu button
        print("2. Opening menu...")
        page.click('.menu-btn')
        time.sleep(3)
        
        print("3. Menu should now be visible - check the bottom-right corner")
        time.sleep(5)
        
        # Close menu
        print("4. Closing menu...")
        page.click('.menu-overlay')
        time.sleep(2)
        
        # Open again
        print("5. Opening menu again...")
        page.click('.menu-btn')
        time.sleep(5)
        
        print("\n=== Test Complete - You can see the menu! ===\n")
        
        time.sleep(3)
        browser.close()

if __name__ == "__main__":
    test_menu()
