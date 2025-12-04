import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        page.on('console', lambda msg: print(f"PRED PAGE CONSOLE: {msg.text}"))
        # Ensure logged-in state so the page doesn't redirect away
        await page.add_init_script("localStorage.setItem('twin_user_logged_in','true'); localStorage.setItem('twin_predictions','[]');")
        await page.goto('file:///C:/Users/seblxx/Documents/GitHub/TWIN/predictions.html')
        # wait for page to settle
        await page.wait_for_timeout(500)
        print(f"Resolved page URL: {page.url}")
        content = await page.content()
        print(f"Pred page content length: {len(content)}")
        print(content[:800])
        # attempt to read page-title with a short timeout
        try:
            title = await page.text_content('.page-title', timeout=2000)
            print(f"Predictions page title: {title}")
        except Exception as e:
            print(f"Failed to get .page-title: {e}")
        cards = await page.evaluate("() => document.querySelectorAll('.prediction-card').length")
        print(f"Prediction cards count: {cards}")
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_test())
