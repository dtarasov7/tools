import { browser } from 'k6/experimental/browser';
import { sleep } from 'k6';

export const options = {
  insecureSkipTLSVerify: true,
  scenarios: {
    browser: {

      startTime: '1s',
      gracefulStop: '2s',
      vus: 10,
      iterations: 100,
      executor: 'shared-iterations',
      options: {
        browser: {
            type: 'chromium',
        },
      },
    },
  },
  thresholds: {
    checks: ["rate==1.0"]
  }
}

export default async function () {
  const page = browser.newPage();

  try {
    console.log("https://first.sz.rshbcloud.ru/")
    await page.goto('https://first.sz.rshbcloud.ru/');
    sleep(randomIntBetween(1, 2))
    console.log("https://first.sz.rshbcloud.ru/natural")
    await page.goto('https://first.sz.rshbcloud.ru/natural');

  } finally {
//    page.close();
  }

//  page = browser.newPage();
//  try {
//    await page.goto('https://first.sz.rshbcloud.ru/natural');
//  } finally {
//    page.close();
//  }

//  console.log("https://first.sz.rshbcloud.ru/natural/deposits")
//  page = browser.newPage();
//  try {
//    await page.goto('https://first.sz.rshbcloud.ru/natural/deposits');
//  } finally {
//    page.close();
//  }

//  console.log("https://first.sz.rshbcloud.ru/natural/deposit/income")
//  page = browser.newPage();
//  try {
//    await page.goto('https://first.sz.rshbcloud.ru/natural/deposit/income');
//  } finally {
//    page.close();
//  }
}

export function randomIntBetween(min, max) { // min and max included
  return Math.floor(Math.random() * (max - min + 1) + min);
}
