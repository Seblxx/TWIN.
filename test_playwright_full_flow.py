"""
Full Flow Playwright Test
Tests: Login → Query → Save → Navigate to Predictions → Logout → Login again (clean session)
"""
import asyncio
from playwright.async_api import async_playwright
import time

ACCOUNT_1 = {"email": "dazrini@gmail.com", "password": "gummybear"}
ACCOUNT_2 = {"email": "test2@gmail.com", "password": "password"}

async def full_flow_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context()
        page = await context.new_page()
        
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        print("\n" + "="*80)
        print("🎭 FULL FLOW PLAYWRIGHT TEST")
        print("="*80)
        
        try:
            # ===== TEST 1: Login Account 1 =====
            print("\n[1/10] Logging in Account 1...")
            await page.goto('http://127.0.0.1:5000/intro.html')
            await page.wait_for_load_state('networkidle')
            
            await page.locator('#loginToggleBtn').click()
            await page.wait_for_timeout(500)
            
            await page.locator('#emailInput').fill(ACCOUNT_1['email'])
            await page.locator('#passwordInput').fill(ACCOUNT_1['password'])
            await page.locator('#loginBtn').click()
            await page.wait_for_timeout(2500)
            
            if 'index.html' in page.url:
                print(f"✅ Logged in as {ACCOUNT_1['email']}")
            else:
                print(f"❌ Login failed")
                await browser.close()
                return
            
            # ===== TEST 2: Make a prediction =====
            print("\n[2/10] Making prediction...")
            await page.locator('#userInput').fill("Apple in 5 days")
            await page.locator('button[onclick="sendTwin()"]').click()
            await page.wait_for_timeout(6000)
            
            star_count = await page.locator('.star-save-btn').count()
            print(f"✅ Prediction generated ({star_count} star buttons)")
            
            # ===== TEST 3: Save prediction =====
            if star_count > 0:
                print("\n[3/10] Saving prediction...")
                console_logs.clear()
                await page.locator('.star-save-btn').first.click()
                await page.wait_for_timeout(1500)
                
                save_logs = [log for log in console_logs if 'saved' in log.lower() and 'database' in log.lower()]
                if save_logs:
                    print(f"✅ Prediction saved to database")
                    for log in save_logs[:1]:
                        print(f"   {log}")
                else:
                    print(f"⚠️  No database save confirmation in console")
            else:
                print("\n[3/10] ⚠️  No predictions to save")
            
            # ===== TEST 4: Check PREDICTIONS button enabled =====
            print("\n[4/10] Checking PREDICTIONS button...")
            await page.locator('#menuBtn').click()
            await page.wait_for_timeout(500)
            
            is_disabled = await page.locator('#menuPredictions').get_attribute('disabled')
            if is_disabled:
                print(f"❌ PREDICTIONS button is disabled")
            else:
                print(f"✅ PREDICTIONS button is enabled")
            
            # ===== TEST 5: Navigate to Predictions page =====
            print("\n[5/10] Navigating to Predictions page...")
            if not is_disabled:
                await page.locator('#menuPredictions').click()
                await page.wait_for_timeout(2000)
                
                if 'predictions.html' in page.url:
                    print(f"✅ On predictions page")
                    
                    pred_cards = await page.locator('.prediction-card').count()
                    print(f"   Prediction cards: {pred_cards}")
                    
                    if pred_cards > 0:
                        # Check stock name
                        first_stock = await page.locator('.prediction-card .stock-name').first.text_content()
                        print(f"   First prediction: {first_stock}")
                else:
                    print(f"❌ Failed to navigate")
                
                # Go back to index
                print("\n[6/10] Going back to index...")
                await page.goto('http://127.0.0.1:5000/index.html')
                await page.wait_for_timeout(1000)
                
                # Check if query is still there (session persistence)
                input_value = await page.locator('#userInput').input_value()
                if input_value:
                    print(f"✅ Query persisted: \"{input_value}\"")
                else:
                    print(f"⚠️  Query cleared (expected to persist)")
            else:
                print(f"⚠️  Skipping predictions page (button disabled)")
            
            # ===== TEST 7: Logout =====
            print("\n[7/10] Logging out...")
            await page.locator('#menuBtn').click()
            await page.wait_for_timeout(500)
            await page.locator('#menuLogout').click()
            await page.wait_for_timeout(500)
            
            # Confirm logout
            confirm_btn = page.locator('button:has-text("Logout")').last
            await confirm_btn.click()
            await page.wait_for_timeout(2000)
            
            if 'intro.html' in page.url:
                print(f"✅ Logged out, redirected to intro")
            else:
                print(f"⚠️  Still on {page.url}")
            
            # ===== TEST 8: Login Account 2 =====
            print("\n[8/10] Logging in Account 2...")
            await page.locator('#loginToggleBtn').click()
            await page.wait_for_timeout(500)
            
            await page.locator('#emailInput').fill(ACCOUNT_2['email'])
            await page.locator('#passwordInput').fill(ACCOUNT_2['password'])
            await page.locator('#loginBtn').click()
            await page.wait_for_timeout(2500)
            
            if 'index.html' in page.url:
                print(f"✅ Logged in as {ACCOUNT_2['email']}")
            else:
                print(f"❌ Login failed")
                await browser.close()
                return
            
            # ===== TEST 9: Check clean session =====
            print("\n[9/10] Checking clean session...")
            input_value = await page.locator('#userInput').input_value()
            if input_value:
                print(f"❌ FAILED: Query from Account 1 still present: \"{input_value}\"")
                print(f"   Session should be clean after logout!")
            else:
                print(f"✅ Clean session: input field is empty")
            
            basic_messages = await page.locator('#messages-basic .bot').count()
            plus_messages = await page.locator('#messages-plus .bot').count()
            if basic_messages > 0 or plus_messages > 0:
                print(f"❌ FAILED: Chat messages from Account 1 still visible")
                print(f"   TWIN-: {basic_messages} messages, TWIN+: {plus_messages} messages")
            else:
                print(f"✅ Clean chat: no previous messages")
            
            # ===== TEST 10: Check predictions isolation =====
            print("\n[10/10] Checking predictions isolation...")
            await page.locator('#menuBtn').click()
            await page.wait_for_timeout(500)
            
            is_disabled = await page.locator('#menuPredictions').get_attribute('disabled')
            if not is_disabled:
                await page.locator('#menuPredictions').click()
                await page.wait_for_timeout(2000)
                
                if 'predictions.html' in page.url:
                    pred_cards = await page.locator('.prediction-card').count()
                    print(f"   Account 2 predictions: {pred_cards}")
                    
                    if pred_cards > 0:
                        stocks = await page.locator('.prediction-card .stock-name').all_text_content()
                        print(f"   Stocks: {stocks}")
                        
                        if any('AAPL' in s or 'Apple' in s for s in stocks):
                            print(f"❌ ISOLATION FAILURE: Account 2 sees Account 1's predictions!")
                        else:
                            print(f"✅ Isolation verified: Only Account 2's predictions")
                    else:
                        print(f"✓ Account 2 has no predictions (expected)")
            
            print("\n" + "="*80)
            print("✅ FULL FLOW TEST COMPLETED")
            print("="*80)
            
            await page.wait_for_timeout(3000)
            await browser.close()
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()

if __name__ == '__main__':
    asyncio.run(full_flow_test())
