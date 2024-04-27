import { browser } from 'k6/experimental/browser';

export const options = {
  insecureSkipTLSVerify: true,
  scenarios: {
    first: {
      startTime: '1s',
      gracefulStop: '2s',
      vus: 1,
      iterations: 2,
      executor: 'shared-iterations',
      tags: { test_type: 'first' },
      exec: "first",
      options: {
        browser: {
            type: 'chromium',
        },
      },
    },
    natural: {
      startTime: '1s',
      gracefulStop: '2s',
      vus: 1,
      iterations: 2,
      executor: 'shared-iterations',
      exec: "second",
      tags: { test_type: 'second' },
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


export async function first() {
  const page = browser.newPage();
  console.log("https://first.sz.rshbcloud.ru/")
  try {
    await page.goto('https://first.sz.rshbcloud.ru/');
  } finally {
    page.close();
  }
}

export async function second() {
  const page2 = browser.newPage();
  console.log("https://first.sz.rshbcloud.ru/natural")
//  page = browser.newPage();
  try {
    await page2.goto('https://first.sz.rshbcloud.ru/natural');
  } finally {
    page2.close();
  }
}
