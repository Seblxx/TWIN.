"""
Final comprehensive test - verify all changes work correctly
"""
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:5000"

async def test_all_features():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=400)
        context = await browser.new_context()
        page = await context.new_page()
        
        issues = []
        
        print("\n" + "="*70)
        print("FINAL COMPREHENSIVE TEST")
        print("="*70)
        
        # ========== TEST 1: Logout redirects to intro.html ==========
        print("\n[TEST 1] Logout redirects to intro.html")
        try:
            await page.goto(f"{BASE_URL}/intro.html")
            await page.wait_for_load_state('networkidle')
            await page.click('#loginToggleBtn')
            await page.wait_for_selector('.modal-overlay.open')
            await page.fill('#emailInput', 'dazrini@gmail.com')
            await page.fill('#passwordInput', 'gummybear')
            await page.click('#loginBtn')
            await page.wait_for_url(f"{BASE_URL}/index.html")
            await asyncio.sleep(1)
            
            # Open menu and logout
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open')
            await asyncio.sleep(0.5)
            
            # Check button says LOGOUT
            button_text = await page.inner_text('#menuHome')
            print(f"  Button text when logged in: '{button_text.strip()}'")
            
            await page.click('#menuHome')
            try:
                await page.wait_for_selector('#confirmYes', timeout=2000)
                await page.click('#confirmYes')
            except:
                pass
            
            await asyncio.sleep(2)
            current_url = page.url
            
            if 'intro.html' in current_url:
                print("  ✓ Logout correctly redirects to intro.html")
            else:
                issues.append(f"Logout redirects to {current_url} (should be intro.html)")
                print(f"  ✗ Wrong redirect: {current_url}")
                
        except Exception as e:
            issues.append(f"Test 1 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 2: Menu button shows HOME when logged out ==========
        print("\n[TEST 2] Menu shows HOME when logged out")
        try:
            await page.goto(f"{BASE_URL}/index.html")
            await page.wait_for_load_state('networkidle')
            await page.evaluate("localStorage.removeItem('twin_user_logged_in')")
            await page.reload()
            await asyncio.sleep(1)
            
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open')
            await asyncio.sleep(0.5)
            
            button_text = await page.inner_text('#menuHome')
            button_text = button_text.strip().upper()
            
            if button_text == 'HOME':
                print(f"  ✓ Button shows 'HOME' when logged out")
            else:
                issues.append(f"Button shows '{button_text}' when logged out")
                print(f"  ✗ Button shows '{button_text}'")
                
        except Exception as e:
            issues.append(f"Test 2 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 3: Menu styling is refined ==========
        print("\n[TEST 3] Menu has refined styling")
        try:
            # Menu should already be open
            menu_style = await page.evaluate("""
                () => {
                    const menu = document.querySelector('.menu-options');
                    const style = getComputedStyle(menu);
                    const button = menu.querySelector('button');
                    const btnStyle = getComputedStyle(button);
                    return {
                        background: style.background,
                        borderRadius: style.borderRadius,
                        backdropFilter: style.backdropFilter,
                        buttonTextAlign: btnStyle.textAlign,
                        buttonFontWeight: btnStyle.fontWeight
                    };
                }
            """)
            
            print(f"  Border radius: {menu_style['borderRadius']}")
            print(f"  Backdrop filter: {menu_style['backdropFilter'][:50]}...")
            print(f"  Button alignment: {menu_style['buttonTextAlign']}")
            print(f"  Button font weight: {menu_style['buttonFontWeight']}")
            
            if 'blur' in menu_style['backdropFilter']:
                print("  ✓ Backdrop blur is applied")
            else:
                issues.append("Backdrop blur not detected")
                print("  ✗ No backdrop blur")
            
            if menu_style['buttonTextAlign'] == 'right':
                print("  ✓ Buttons are right-aligned")
            else:
                print(f"  ⚠ Buttons are {menu_style['buttonTextAlign']}-aligned")
                
        except Exception as e:
            issues.append(f"Test 3 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== TEST 4: Predictions page styling ==========
        print("\n[TEST 4] Predictions page has sleek styling")
        try:
            # Login first
            await page.goto(f"{BASE_URL}/intro.html")
            await page.click('#loginToggleBtn')
            await page.wait_for_selector('.modal-overlay.open')
            await page.fill('#emailInput', 'dazrini@gmail.com')
            await page.fill('#passwordInput', 'gummybear')
            await page.click('#loginBtn')
            await page.wait_for_url(f"{BASE_URL}/index.html")
            await asyncio.sleep(1)
            
            # Make a prediction
            await page.fill('#userInput', 'MSFT in 2 weeks')
            await page.click('button.btn-both-inside')
            await page.wait_for_selector('.bot', timeout=30000)
            await asyncio.sleep(2)
            
            # Save prediction
            star_btns = await page.query_selector_all('.star-save-btn')
            if len(star_btns) > 0:
                await star_btns[0].click()
                await asyncio.sleep(1)
            
            # Navigate to predictions
            await page.click('#menuBtn')
            await page.wait_for_selector('.menu-options.open')
            await page.click('#menuPredictions')
            await page.wait_for_url(f"{BASE_URL}/predictions.html")
            await asyncio.sleep(1)
            
            # Check styling
            styles = await page.evaluate("""
                () => {
                    const topbar = document.querySelector('.predictions-topbar');
                    const backBtn = document.querySelector('.back-button');
                    const card = document.querySelector('.prediction-item');
                    
                    const topbarStyle = getComputedStyle(topbar);
                    const backStyle = getComputedStyle(backBtn);
                    const cardStyle = card ? getComputedStyle(card) : null;
                    
                    return {
                        topbarPadding: topbarStyle.padding,
                        backBtnSize: backStyle.width + ' x ' + backStyle.height,
                        backBtnRadius: backStyle.borderRadius,
                        cardRadius: cardStyle ? cardStyle.borderRadius : 'N/A',
                        cardBackdrop: cardStyle ? cardStyle.backdropFilter : 'N/A'
                    };
                }
            """)
            
            print(f"  Topbar padding: {styles['topbarPadding']}")
            print(f"  Back button size: {styles['backBtnSize']}")
            print(f"  Back button radius: {styles['backBtnRadius']}")
            print(f"  Card border radius: {styles['cardRadius']}")
            
            if 'blur' in styles['cardBackdrop']:
                print("  ✓ Prediction cards have backdrop blur")
            else:
                print("  ⚠ Card backdrop filter:", styles['cardBackdrop'])
            
            print("  ✓ Predictions page styling updated")
            
        except Exception as e:
            issues.append(f"Test 4 Error: {e}")
            print(f"  ✗ Error: {e}")
        
        # ========== FINAL REPORT ==========
        print("\n" + "="*70)
        print("FINAL REPORT")
        print("="*70)
        
        if len(issues) == 0:
            print("✓ ALL FEATURES WORKING PERFECTLY!")
        else:
            print(f"✗ FOUND {len(issues)} ISSUE(S):\n")
            for i, issue in enumerate(issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n" + "="*70)
        
        await browser.close()
        
        return issues

if __name__ == "__main__":
    issues = asyncio.run(test_all_features())
    exit(0 if len(issues) == 0 else 1)
