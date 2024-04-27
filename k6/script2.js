import { browser } from 'k6/experimental/browser';

export const options = {
  insecureSkipTLSVerify: true,
  scenarios: {
    browser: {

      startTime: '1s',
      gracefulStop: '2s',
      vus: 1,
      iterations: 2,
      executor: 'shared-iterations',
      options: {
        browser: {
            type: 'chromium',
        },
      },
    },
  },
  thresholds: {
    checks: ["rate==1.0"],
    'browser_web_vital_fcp{gropu:::first1}': ['max < 1000'],
    'browser_web_vital_fcp{gropu:::first2}': ['max < 1000'],
    'browser_web_vital_fcp{gropu:::first3}': ['max < 1000'],
    'browser_web_vital_fcp{gropu:::first4}': ['max < 1000'],
  }
}

export default async function () {
  const page = browser.newPage();

  console.log("https://first.sz.rshbcloud.ru/")
  try {
       await page.goto('https://first.sz.rshbcloud.ru/');
  } finally {
//    page.close();
  }

  console.log("https://first.sz.rshbcloud.ru/natural")
//  page = browser.newPage();
  try {
    await page.goto('https://first.sz.rshbcloud.ru/natural');
  } finally {
//    page.close();
  }

  console.log("https://first.sz.rshbcloud.ru/natural/deposits")
//  page = browser.newPage();
  try {
    await page.goto('https://first.sz.rshbcloud.ru/natural/deposits');
  } finally {
//    page.close();
  }

  console.log("https://first.sz.rshbcloud.ru/natural/deposit/income")
//  page = browser.newPage();
  try {
    await page.goto('https://first.sz.rshbcloud.ru/natural/deposit/income');
  } finally {
//    page.close();
  }
}
