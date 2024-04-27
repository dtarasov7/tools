import { chromium } from 'k6/experimental/browser';

export default async function () {
  const browser = chromium.launch({ headless: false });
  const page = browser.newPage();
  try {
    await page.goto('https://test.k6.io/', { waitUntil: 'networkidle' })
    page.screenshot({ path: 'screenshot.png' });
  } finally {
    page.close();
    browser.close();
  }
}

