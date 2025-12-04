const { test, expect } = require('@playwright/test');
const fs = require('fs');
const pixelmatch = require('pixelmatch');
const PNG = require('pngjs').PNG;

// Path to your reference screenshot
const referencePath = 'reference_menu.png';

// Helper to compare screenshots
async function compareScreenshots(actualPath, referencePath) {
  const img1 = PNG.sync.read(fs.readFileSync(actualPath));
  const img2 = PNG.sync.read(fs.readFileSync(referencePath));
  const { width, height } = img1;
  const diff = new PNG({ width, height });
  const mismatched = pixelmatch(img1.data, img2.data, diff.data, width, height, { threshold: 0.1 });
  return mismatched;
}

test('Menu layout matches reference screenshot', async ({ page }) => {
  await page.goto('http://localhost:5000'); // Change to your local URL
  await page.click('#menuBtn');
  await page.waitForSelector('.menu-options.open');
  const menu = await page.locator('.menu-options');
  const screenshotPath = 'menu_test.png';
  await menu.screenshot({ path: screenshotPath });

  // Compare screenshots
  const mismatched = await compareScreenshots(screenshotPath, referencePath);
  expect(mismatched).toBeLessThan(100); // Acceptable threshold
});
