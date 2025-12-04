import time
from playwright.sync_api import sync_playwright

print("Testing prediction save and display flow...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 1. Navigate to index.html
    print("\n1. Loading index.html...")
    page.goto("http://127.0.0.1:5000/index.html")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 2. Check localStorage initially
    predictions_before = page.evaluate("localStorage.getItem('twin_predictions')")
    print(f"   Predictions in localStorage before: {predictions_before}")
    
    # 3. Enter a query
    print("\n2. Entering query...")
    user_input = page.locator("#userInput")
    user_input.fill("AAPL in 1 week")
    user_input.press("Enter")
    
    # 4. Wait for star button to appear
    print("\n3. Waiting for prediction result and star button...")
    try:
        star_btn = page.locator(".star-save-btn").last
        star_btn.wait_for(timeout=30000)
        print("   ✓ Star button found!")
        
        # Check if star button is visible
        is_visible = star_btn.is_visible()
        print(f"   Star button visible: {is_visible}")
        
        if not is_visible:
            print("   ✗ Star button exists but is NOT visible!")
            logged_in = page.evaluate("localStorage.getItem('twin_user_logged_in')")
            print(f"   twin_user_logged_in flag: {logged_in}")
        
    except Exception as e:
        print(f"   ✗ Star button not found: {e}")
        browser.close()
        exit(1)
    
    # 5. Click the star button
    print("\n4. Clicking star button to save prediction...")
    star_btn.click()
    time.sleep(1)
    
    # 6. Check localStorage after save
    predictions_after = page.evaluate("localStorage.getItem('twin_predictions')")
    print(f"\n5. Predictions in localStorage after save:\n{predictions_after}")
    
    # Parse and display
    pred_count = page.evaluate("JSON.parse(localStorage.getItem('twin_predictions') || '[]').length")
    print(f"\n   Number of predictions saved: {pred_count}")
    
    # 7. Navigate to predictions.html
    print("\n6. Navigating to predictions.html...")
    page.goto("http://127.0.0.1:5000/predictions.html")
    page.wait_for_load_state("networkidle")
    time.sleep(2)
    
    # 8. Check if predictions are displayed
    print("\n7. Checking predictions display...")
    pred_cards = page.locator(".prediction-item")
    card_count = pred_cards.count()
    print(f"   Number of prediction cards displayed: {card_count}")
    
    if card_count > 0:
        print("\n   ✓ SUCCESS! Predictions are being saved and displayed!")
        print("\n   First card details:")
        first_card = pred_cards.first
        stock_symbol = first_card.locator(".stock-symbol").text_content()
        duration = first_card.locator(".duration-badge").text_content()
        print(f"   - Stock: {stock_symbol}")
        print(f"   - Duration: {duration}")
    else:
        print("\n   ✗ FAIL: No prediction cards displayed on predictions.html!")
        # Check localStorage on predictions page
        pred_on_page = page.evaluate("localStorage.getItem('twin_predictions')")
        print(f"   localStorage on predictions.html: {pred_on_page}")
    
    print("\n8. Taking screenshot...")
    page.screenshot(path="test_save_flow_predictions.png")
    
    print("\nTest complete! Browser will close in 5 seconds...")
    time.sleep(5)
    browser.close()
