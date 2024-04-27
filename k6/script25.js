import { browser } from 'k6/experimental/browser';
//import { group } from 'k6';
import { sleep } from 'k6';

export const options = {
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
  insecureSkipTLSVerify: true,
  scenarios: {
    browser: {
      startTime: '1s',
      gracefulStop: '2s',
      vus: 5,
      iterations: 20,
      executor: 'shared-iterations',
//        executor: 'ramping-vus',
//       startVUs: 0,
//       stages: [
//         { duration: '120s', target: 5 },
//         { duration: '30s', target: 0 },
//       ],
//       gracefulRampDown: '0s',
      options: {
        browser: {
            type: 'chromium',
        },
      },
    },
  },
  thresholds: {
    checks: ["rate==1.0"],
    'browser_web_vital_fcp{url:https://test.k6.io/}': ['max < 10000'],
    'browser_web_vital_fcp{url:https://test.k6.io/news.php}': ['max < 10000'],
    'browser_web_vital_fcp{url:https://test.k6.io/browser.php}': ['max < 10000'],
    'browser_web_vital_fcp{url:https://test.k6.io/contacts.php}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://test.k6.io/}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://test.k6.io/news.php}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://test.k6.io/browser.php}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://test.k6.io/contacts.php}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://test.k6.io/}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://test.k6.io/news.php}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://test.k6.io/browser.php}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://test.k6.io/contacts.php}': ['max < 10000'],
  }
}

export default async function () {
  const page = browser.newPage();

  try {
      console.log("https://test.k6.io/");
      await      page.goto('https://test.k6.io/');
//      sleep(randomIntBetween(1, 2))
      console.log("https://test.k6.io/news.php");

      await page.goto('https://test.k6.io/news.php');
//      sleep(randomIntBetween(1, 2))
      console.log("https://test.k6.io/browser.php");

      await   page.goto('https://test.k6.io/browser.php');
//      sleep(randomIntBetween(1, 2))
      console.log("https://test.k6.io/contacts.php");

      await  page.goto('https://test.k6.io/contacts.php');
//      sleep(randomIntBetween(1, 2))
  } catch (error) {
    console.error(error);
  } finally {
    page.close();
  }
}


export function randomIntBetween(min, max) { // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}
