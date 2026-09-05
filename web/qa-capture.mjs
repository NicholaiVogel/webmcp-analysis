// QA capture: renders the site at supported widths and saves screenshots.
// Usage: node qa-capture.mjs [baseURL]
import { chromium } from 'playwright-core';
import fs from 'node:fs';

const BASE = process.argv[2] || 'http://127.0.0.1:4321';
const OUT = '/mnt/work/hermes-scratch/astro-portfolio-site/webmcp-results/qa';
fs.mkdirSync(OUT, { recursive: true });

const shots = [
  { path: '/', name: 'home', widths: [[1440, 900], [768, 1024], [375, 812]] },
  { path: '/project/alza/', name: 'project', widths: [[1440, 900], [375, 812]] },
  { path: '/explore/', name: 'explore', widths: [[1440, 900], [375, 812]] },
  { path: '/methodology/', name: 'methodology', widths: [[1440, 900], [375, 812]] },
];

const browser = await chromium.launch({
  executablePath: '/usr/bin/google-chrome-stable',
  headless: true,
});
const errors = [];
for (const s of shots) {
  for (const [width, height] of s.widths) {
    const ctx = await browser.newContext({ viewport: { width, height } });
    const page = await ctx.newPage();
    page.on('console', (m) => { if (m.type() === 'error') errors.push(`${s.path}@${width}: ${m.text()}`); });
    page.on('pageerror', (e) => errors.push(`${s.path}@${width}: ${e.message}`));
    await page.goto(BASE + s.path, { waitUntil: 'networkidle' });
    await page.waitForTimeout(400);
    const file = `${OUT}/${s.name}-${width}.png`;
    await page.screenshot({ path: file });
    // horizontal overflow check
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
    console.log(`${s.name}@${width}: shot ok, overflowX=${overflow}px`);
    await ctx.close();
  }
}
// interaction check: search filters the table
{
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  await page.goto(BASE + '/', { waitUntil: 'networkidle' });
  await page.fill('#q', 'alza');
  await page.waitForTimeout(600);
  const rows = await page.locator('#tbody tr[data-href]').count();
  const count = await page.textContent('#count');
  console.log(`search "alza": ${rows} rows, count="${count?.trim()}"`);
  await page.fill('#q', '');
  await page.selectOption('#cat', 'game');
  await page.waitForTimeout(400);
  const gameRows = await page.locator('#tbody tr[data-href]').count();
  console.log(`category=game: first batch rows=${gameRows}`);
  await page.selectOption('#cat', '');
  // sort by leverage: first row should have max leverage in dataset (10)
  await page.click('th[data-k="l"]');
  await page.waitForTimeout(400);
  const firstLev = await page.locator('#tbody tr td:nth-child(5)').first().textContent();
  console.log(`sort by leverage: first cell=${firstLev}`);
  await ctx.close();
}
console.log('console errors:', errors.length ? errors.slice(0, 5) : 'none');
await browser.close();
