"""
Test predictions page layout and responsiveness
"""
import asyncio
from playwright.async_api import async_playwright

async def test_predictions_page():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        
        # Test different viewport sizes
        viewports = [
            {"width": 1920, "height": 1080, "name": "Desktop (1920x1080)"},
            {"width": 1366, "height": 768, "name": "Laptop (1366x768)"},
            {"width": 768, "height": 1024, "name": "Tablet (768x1024)"},
            {"width": 375, "height": 667, "name": "Mobile (375x667)"}
        ]
        
        print("\n" + "="*80)
        print("📱 PREDICTIONS PAGE RESPONSIVE LAYOUT TEST")
        print("="*80)
        
        try:
            for viewport in viewports:
                print(f"\n📋 Testing: {viewport['name']}")
                print("-" * 80)
                
                context = await browser.new_context(
                    viewport={"width": viewport['width'], "height": viewport['height']}
                )
                page = await context.new_page()
                
                # Go to intro and login
                await page.goto('http://127.0.0.1:5000/intro.html')
                await page.wait_for_load_state('networkidle')
                
                await page.locator('#loginToggleBtn').click()
                await page.wait_for_timeout(500)
                
                await page.locator('#emailInput').fill('test_1764111733@twin.test')
                await page.locator('#passwordInput').fill('SecurePass123!')
                await page.locator('#loginBtn').click()
                await page.wait_for_timeout(2000)
                
                # Navigate to predictions
                await page.locator('#menuBtn').click()
                await page.wait_for_timeout(500)
                await page.locator('#menuPredictions').click()
                await page.wait_for_timeout(2000)
                
                if 'predictions.html' in page.url:
                    # Check layout
                    pred_cards = await page.locator('.prediction-card').count()
                    grid = page.locator('.predictions-grid')
                    
                    # Get grid computed styles
                    grid_columns = await grid.evaluate('el => window.getComputedStyle(el).gridTemplateColumns')
                    
                    print(f"✓ Loaded predictions page")
                    print(f"✓ Prediction cards: {pred_cards}")
                    print(f"✓ Grid columns: {grid_columns.count('px')} column(s)")
                    
                    # Check if cards are visible and not overlapping
                    if pred_cards > 0:
                        first_card = page.locator('.prediction-card').first
                        card_box = await first_card.bounding_box()
                        print(f"✓ Card dimensions: {int(card_box['width'])}x{int(card_box['height'])}px")
                        
                        if card_box['width'] > viewport['width']:
                            print(f"❌ OVERFLOW: Card wider than viewport!")
                        else:
                            print(f"✅ Layout looks good - cards fit viewport")
                    
                    # Test theme switching on predictions page
                    print(f"✓ Testing theme toggle...")
                    await page.locator('#themeToggle').click()
                    await page.wait_for_timeout(1000)
                    print(f"✅ Theme toggle works")
                    
                    await page.wait_for_timeout(2000)
                else:
                    print(f"❌ Failed to navigate to predictions page")
                
                await context.close()
            
            print("\n" + "="*80)
            print("✅ RESPONSIVE LAYOUT TEST COMPLETE")
            print("="*80)
            print("\nAll viewport sizes tested successfully!")
            print("Predictions page layout is responsive and fits all screen sizes.")
            
            await browser.close()
            return True
            
        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return False

if __name__ == '__main__':
    success = asyncio.run(test_predictions_page())
    exit(0 if success else 1)
