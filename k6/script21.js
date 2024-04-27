import { browser } from 'k6/experimental/browser';
import { group } from 'k6';

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
//    'browser_web_vital_fcp{group:first1}': ['max < 10000'],
//    'browser_web_vital_fcp{group::first2}': ['max < 10000'],
//    'browser_web_vital_fcp{group:::first3}': ['max < 10000'],
//    'browser_web_vital_fcp{group:::first4}': ['max < 10000'],
//    'browser_web_vital_cls{group:::first4}': ['max < 10000'],
//    'browser_web_vital_lcp{group:::first4}': ['max < 10000'],
//    'browser_web_vital_ttfb{group:::first4}': ['max < 10000'],
  }
}

export default async function () {
  const page = browser.newPage();

  console.log("https://first.sz.rshbcloud.ru/")
  try {
    await group('first1',  function () {
       page.goto('https://first.sz.rshbcloud.ru/')
    })
  } finally {
//    page.close();
  }

  console.log("https://first.sz.rshbcloud.ru/natural")
//  page = browser.newPage();
  try {
   await group('first2', function () {
    page.goto('https://first.sz.rshbcloud.ru/natural')
    })
  } finally {
//    page.close();
  }

  console.log("https://first.sz.rshbcloud.ru/natural/deposits")
//  page = browser.newPage();
  try {
   await group('first3', function () {
    page.goto('https://first.sz.rshbcloud.ru/natural/deposits')
    })
  } finally {
//    page.close();
  }

  console.log("https://first.sz.rshbcloud.ru/natural/deposit/income")
//  page = browser.newPage();
  try {
   await group('first4', function () {
    page.goto('https://first.sz.rshbcloud.ru/natural/deposit/income')
    })
  } finally {
//    page.close();
  }
}
