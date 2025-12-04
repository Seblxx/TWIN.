"""
Streamlined test - No theme testing, fast waits, frontend focus
Tests: Login → Save prediction → Check button enabled → Navigate to predictions
"""
import asyncio
from playwright.async_api import async_playwright

async def quick_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture console
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        print("\n" + "="*80)
        print("⚡ QUICK PREDICTIONS TEST")
        print("="*80)
        
        test_email = "dazrini@gmail.com"
        test_password = "gummybear"
        
        try:
            # 1. Login
            print("\n[1/5] Logging in...")
            await page.goto('http://127.0.0.1:5000/intro.html')
            await page.wait_for_load_state('networkidle')
            await page.locator('#loginToggleBtn').click()
            await page.wait_for_timeout(300)
            
            await page.locator('#emailInput').fill(test_email)
            await page.locator('#passwordInput').fill(test_password)
            await page.locator('#loginBtn').click()
            await page.wait_for_timeout(2000)
            
            if 'index.html' in page.url:
                print("✅ Logged in")
            else:
                print(f"❌ Login failed - still on {page.url}")
                await browser.close()
                return
            
            # 2. Make a prediction
            print("\n[2/5] Running prediction...")
            await page.locator('#userInput').fill("Tesla in 3 days")
            await page.locator('button[onclick="sendTwin()"]').click()
            await page.wait_for_timeout(5000)  # Wait for prediction
            
            star_count = await page.locator('.star-save-btn').count()
            print(f"✓ Found {star_count} star buttons")
            
            # 3. Save prediction
            if star_count > 0:
                print("\n[3/5] Saving prediction...")
                console_logs.clear()
                await page.locator('.star-save-btn').first.click()
                await page.wait_for_timeout(1000)
                
                # Check console for save confirmation
                save_logs = [log for log in console_logs if 'saved' in log.lower() or 'error' in log.lower()]
                for log in save_logs:
                    print(f"   {log}")
                
                # Check if backend was called
                if any('database' in log.lower() for log in console_logs):
                    print("✅ Prediction saved to database")
                else:
                    print("⚠️  No database save confirmation")
            else:
                print("\n[3/5] ⚠️  No predictions to save")
            
            # 4. Check if PREDICTIONS button enabled
            print("\n[4/5] Checking PREDICTIONS button...")
            await page.locator('#menuBtn').click()
            await page.wait_for_timeout(500)
            
            is_disabled = await page.locator('#menuPredictions').get_attribute('disabled')
            if is_disabled:
                print("❌ PREDICTIONS button is DISABLED")
                print("   Checking for errors...")
                errors = [log for log in console_logs if 'error' in log.lower() or '500' in log or '401' in log]
                if errors:
                    for err in errors[-3:]:
                        print(f"   {err}")
            else:
                print("✅ PREDICTIONS button is ENABLED")
                
                # 5. Navigate to predictions page
                print("\n[5/5] Opening predictions page...")
                await page.locator('#menuPredictions').click()
                await page.wait_for_timeout(1500)
                
                if 'predictions.html' in page.url:
                    print("✅ Navigated to predictions page")
                    
                    # Check predictions loaded
                    pred_cards = await page.locator('.prediction-card').count()
                    print(f"✓ Prediction cards: {pred_cards}")
                    
                    if pred_cards > 0:
                        print("✅ ALL TESTS PASSED!")
                    else:
                        print("⚠️  No prediction cards displayed")
                else:
                    print(f"❌ Navigation failed - at {page.url}")
            
            await page.wait_for_timeout(3000)
            await browser.close()
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()

if __name__ == '__main__':
    asyncio.run(quick_test())
