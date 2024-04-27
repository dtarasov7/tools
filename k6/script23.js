import { browser } from 'k6/experimental/browser';
//import { group } from 'k6';
import { sleep } from 'k6';

export const options = {
  insecureSkipTLSVerify: true,
  blockHostnames: ['*yandex.ru', '*.mindbox.ru'],
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
    'browser_web_vital_fcp{url:https://first.sz.rshbcloud.ru/}': ['max < 10000'],
    'browser_web_vital_fcp{url:https://first.sz.rshbcloud.ru/natural}': ['max < 10000'],
    'browser_web_vital_fcp{url:https://first.sz.rshbcloud.ru/natural/deposits}': ['max < 10000'],
    'browser_web_vital_fcp{url:https://first.sz.rshbcloud.ru/natural/deposits/income}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://first.sz.rshbcloud.ru/}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://first.sz.rshbcloud.ru/natural}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://first.sz.rshbcloud.ru/natural/deposits}': ['max < 10000'],
    'browser_web_vital_lcp{url:https://first.sz.rshbcloud.ru/natural/deposits/income}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://first.sz.rshbcloud.ru/}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://first.sz.rshbcloud.ru/natural}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://first.sz.rshbcloud.ru/natural/deposits}': ['max < 10000'],
    'browser_web_vital_ttfb{url:https://first.sz.rshbcloud.ru/natural/deposits/income}': ['max < 10000'],
  }
}

export default async function () {
  const page = browser.newPage();

  try {
      console.error("https://first.sz.rshbcloud.ru/");

      await      page.goto('https://first.sz.rshbcloud.ru/');
//      sleep(randomIntBetween(1, 2))
      console.log("https://first.sz.rshbcloud.ru/natural");

      await page.goto('https://first.sz.rshbcloud.ru/natural');
//      sleep(randomIntBetween(1, 2))
      console.log("https://first.sz.rshbcloud.ru/natural/deposits");

      await   page.goto('https://first.sz.rshbcloud.ru/natural/deposits');
//      sleep(randomIntBetween(1, 2))
      console.log("https://first.sz.rshbcloud.ru/natural/deposit/income");

      await  page.goto('https://first.sz.rshbcloud.ru/natural/deposit/income');
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
