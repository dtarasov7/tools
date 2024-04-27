import { browser } from 'k6/experimental/browser';
import { group } from 'k6';
import { sleep } from 'k6';

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
//    'browser_web_vital_fcp{https://first.sz.rshbcloud.ru/}': ['max < 10000'],
//    'browser_web_vital_fcp{https://first.sz.rshbcloud.ru/natural}': ['max < 10000'],
//    'browser_web_vital_fcp{https://first.sz.rshbcloud.ru/natural/deposits}': ['max < 10000'],
//    'browser_web_vital_fcp{https://first.sz.rshbcloud.ru/natural/deposits/income}': ['max < 10000'],
  }
}

export default async function () {
  const page = browser.newPage();

  try {
      console.log("https://first.sz.rshbcloud.ru/")

      await group('first1',  function () {
        page.goto('https://first.sz.rshbcloud.ru/');
      })

//      sleep(randomIntBetween(1, 2))
      console.log("https://first.sz.rshbcloud.ru/natural")

      await  group('first2',  function () {
      page.goto('https://first.sz.rshbcloud.ru/natural');
      })
//      sleep(randomIntBetween(1, 2))
      console.log("https://first.sz.rshbcloud.ru/natural/deposits")

      await  group('first3',  function () {
      page.goto('https://first.sz.rshbcloud.ru/natural/deposits');
      })
//      sleep(randomIntBetween(1, 2))
      console.log("https://first.sz.rshbcloud.ru/natural/deposit/income")

      await group('first4',  function () {
       page.goto('https://first.sz.rshbcloud.ru/natural/deposit/income');
      })
//      sleep(randomIntBetween(1, 2))
  } finally {
    page.close();
  }
}


export function randomIntBetween(min, max) { // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}
