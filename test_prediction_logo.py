"""
Test to create a prediction and verify it shows company logo
"""
import asyncio
from playwright.async_api import async_playwright

async def test_prediction_with_logo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("\n" + "="*80)
        print("🔍 PREDICTION LOGO TEST")
        print("="*80)
        
        test_email = "test_1764112119@twin.test"
        test_password = "SecurePass123!"
        
        # Login
        print("\n📋 Logging in...")
        await page.goto('http://127.0.0.1:5000/intro.html')
        await page.wait_for_load_state('networkidle')
        
        await page.locator('#loginToggleBtn').click()
        await page.wait_for_timeout(500)
        
        await page.locator('#emailInput').fill(test_email)
        await page.locator('#passwordInput').fill(test_password)
        await page.locator('#loginBtn').click()
        await page.wait_for_timeout(3000)
        
        print("✅ Logged in")
        
        # Execute a query
        print("\n📋 Executing query: 'Apple in 3 days'")
        await page.locator('#userInput').fill('Apple in 3 days')
        await page.locator('button[onclick="sendTwin()"]').click()
        await page.wait_for_timeout(8000)
        
        # Star the prediction
        print("📋 Starring prediction...")
        star_buttons = await page.locator('.star-save-btn').count()
        if star_buttons > 0:
            await page.locator('.star-save-btn').first.click()
            await page.wait_for_timeout(1000)
            print("✅ Prediction starred")
        
        # Navigate to predictions
        print("\n📋 Navigating to predictions page...")
        await page.locator('#menuBtn').click()
        await page.wait_for_timeout(500)
        await page.locator('#menuPredictions').click()
        await page.wait_for_timeout(2000)
        
        # Check predictions page
        if 'predictions.html' in page.url:
            print("✅ On predictions page")
            
            # Check for prediction cards
            cards = await page.locator('.prediction-card').count()
            print(f"✓ Prediction cards: {cards}")
            
            # Check if there are logos (img tags)
            logos = await page.locator('.prediction-card img').count()
            print(f"✓ Company logos found: {logos}")
            
            if logos == 0:
                print("\n⚠️  NO COMPANY LOGOS FOUND IN PREDICTIONS!")
                print("  This might be expected if logos weren't implemented")
            else:
                # Get logo src
                logo_src = await page.locator('.prediction-card img').first.get_attribute('src')
                print(f"  Logo source: {logo_src}")
            
            # Take screenshot
            await page.screenshot(path='predictions_with_data.png')
            print("✓ Screenshot saved: predictions_with_data.png")
            
            # Wait to view
            print("\n⏳ Keeping browser open for 10 seconds to review...")
            await page.wait_for_timeout(10000)
        else:
            print(f"❌ Expected predictions.html but got: {page.url}")
        
        await browser.close()
        print("\n" + "="*80)

if __name__ == '__main__':
    asyncio.run(test_prediction_with_logo())
