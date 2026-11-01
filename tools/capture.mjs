// Capture the two featured products from their live sites.
// Output goes to .capture/ (gitignored); tools/render.py frames it into assets/.
import { mkdir } from 'node:fs/promises'
import { chromium } from 'playwright'

const OUT = new URL('../.capture/', import.meta.url).pathname
await mkdir(OUT, { recursive: true })

const desktop = { viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, locale: 'en-US', colorScheme: 'light' }
const phone = {
    viewport: { width: 390, height: 844 },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
    locale: 'en-US',
    colorScheme: 'light',
}

const browser = await chromium.launch()
const settle = (page, ms = 3500) => page.waitForTimeout(ms)

async function open(options, url) {
    const context = await browser.newContext(options)
    const page = await context.newPage()
    await page.goto(url, { waitUntil: 'networkidle' })
    await settle(page)
    return { context, page }
}

// Kachi: home on desktop, with the one-time welcome note dismissed.
{
    const { context, page } = await open(desktop, 'https://kachi-game.vercel.app/')
    const welcome = page.getByRole('button', { name: 'Got it', exact: true })
    if (await welcome.count()) await welcome.first().click()
    await settle(page, 1500)
    await page.screenshot({ path: `${OUT}kachi-desktop.png` })
    await context.close()
}

// Kachi: the first twin teach card on a phone.
{
    const { context, page } = await open(phone, 'https://kachi-game.vercel.app/')
    await page.locator('.today .btn').click()
    await page.locator('.twin').first().waitFor()
    await settle(page, 2000)
    await page.screenshot({ path: `${OUT}kachi-phone.png` })
    await context.close()
}

// Wayseeker: the habit field beside the dispensed label, on desktop.
{
    const { context, page } = await open(desktop, 'https://wayseeker.vercel.app/')
    await page.mouse.move(1, 1)
    await settle(page, 1500)
    await page.screenshot({ path: `${OUT}wayseeker-desktop.png` })
    await context.close()
}

// Wayseeker: the habit field on a phone.
{
    const { context, page } = await open(phone, 'https://wayseeker.vercel.app/')
    await page.mouse.move(1, 1)
    await settle(page, 1500)
    await page.screenshot({ path: `${OUT}wayseeker-phone.png` })
    await context.close()
}

await browser.close()
console.log(`captured into ${OUT}`)
