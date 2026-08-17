// 验证词库三件套/计时工具/行测助手页面加载
import puppeteer from 'puppeteer';

const BASE = 'http://127.0.0.1:8090';
const pages = [
  ['词语辨析', '/prep/cybx'],
  ['高频词语', '/prep/highword'],
  ['生词锦囊', '/prep/myword'],
  ['词语查询', '/prep/getword'],
  ['计时工具', '/prep/timer'],
  ['行测助手', '/prep/aide']
];

const browser = await puppeteer.launch({ headless: 'new', args: ['--no-sandbox'] });
const page = await browser.newPage();
await page.setViewport({ width: 1440, height: 900 });
await page.setDefaultTimeout(15000);

// 登录
await page.goto(BASE + '/login', { waitUntil: 'networkidle2' });
await page.type('input[placeholder="请输入账号"]', 'admin');
await page.type('input[placeholder="请输入密码"]', 'admin123');
await page.type('input[placeholder="请输入验证码"]', '0000');
await page.click('button[type="button"].el-button--primary');
await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 20000 }).catch(() => {});
await new Promise(r => setTimeout(r, 3000));

let allOk = true;
for (const [name, path] of pages) {
  try {
    await page.goto(BASE + path, { waitUntil: 'networkidle2', timeout: 20000 });
    await new Promise(r => setTimeout(r, 2500));
    const body = await page.evaluate(() => document.body.innerText.slice(0, 400));
    const ok = !/404|Not Found|加载失败/.test(body) && body.length > 50;
    console.log(`[${ok ? 'OK' : 'FAIL'}] ${name} ${path} :: ${body.slice(0, 80).replace(/\n/g, ' ')}`);
    if (!ok) allOk = false;
  } catch (e) {
    console.log(`[FAIL] ${name} ${path} :: ${e.message}`);
    allOk = false;
  }
}

// 行测助手交互：开始练习 → 提交一题
try {
  await page.goto(BASE + '/prep/aide', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 2000));
  await page.evaluate(() => {
    const btns = [...document.querySelectorAll('button')];
    const start = btns.find(b => b.innerText.includes('开始练习'));
    if (start) start.click();
  });
  await new Promise(r => setTimeout(r, 1500));
  const qText = await page.evaluate(() => {
    const el = document.querySelector('.p-question');
    return el ? el.innerText : '';
  });
  console.log('行测助手题目: ' + qText);
  if (qText) {
    // 尝试解析并提交
    const m = qText.match(/(-?\d+)\s*([+\-×÷])\s*(\d+)\s*=\s*？/);
    if (m) {
      const a = parseInt(m[1]), b = parseInt(m[3]);
      const ans = m[2] === '+' ? a + b : m[2] === '-' ? a - b : m[2] === '×' ? a * b : Math.round(a / b * 100) / 100;
      await page.type('.p-input', String(ans));
      await page.keyboard.press('Enter');
      await new Promise(r => setTimeout(r, 1000));
      const fb = await page.evaluate(() => {
        const el = document.querySelector('.p-feedback');
        return el ? el.innerText : '';
      });
      console.log('提交反馈: ' + fb);
    }
  }
} catch (e) {
  console.log('行测助手交互 FAIL: ' + e.message);
  allOk = false;
}

// 计时工具交互
try {
  await page.goto(BASE + '/prep/timer', { waitUntil: 'networkidle2' });
  await new Promise(r => setTimeout(r, 2000));
  await page.evaluate(() => {
    const btns = [...document.querySelectorAll('button')];
    const start = btns.find(b => b.innerText.trim() === '开始');
    if (start) start.click();
  });
  await new Promise(r => setTimeout(r, 2500));
  const clock = await page.evaluate(() => {
    const el = document.querySelector('.clock');
    return el ? el.innerText : '';
  });
  console.log('计时工具显示: ' + clock + ' (应已倒数/计时)');
} catch (e) {
  console.log('计时工具交互 FAIL: ' + e.message);
}

await browser.close();
console.log(allOk ? '=== ALL PAGES OK ===' : '=== SOME FAILURES ===');
process.exit(allOk ? 0 : 1);
