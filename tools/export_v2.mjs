import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { launch } from '../../033_zcode-inspector/scripts/cdp.mjs';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const out = path.join(root, 'assets/v2');
const source = await fs.readFile(path.join(root, 'preview-v2.html'), 'utf8');
const css = source.match(/<style>([\s\S]*?)<\/style>/)[1].replaceAll('100%);', '100% 100%);');
const fonts = [...source.matchAll(/@font-face\{[^}]+\}/g)].map((match) => match[0]).join('\n')
  .replaceAll("url('assets/v2/", "url('")
  .replaceAll("url('assets/", "url('../");
const markup = (selector) => selector === '.hero'
  ? source.match(/<section class="hero frame">[\s\S]*?<\/section>/)[0]
  : source.match(new RegExp(`<section class="[^"]*" id="${selector.slice(1).split('.').at(-1)}">[\\s\\S]*?</section>`))[0];
const documentFor = (body, extra = '', id = '') => `<!doctype html><html lang="en" data-theme="dark"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><base href="http://127.0.0.1:9766/030_github-profile/"><style>${css}${extra}</style></head><body><main data-export="${id}">${body}</main></body></html>`;
const escapeXml = (value) => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');

const sourceServer = spawn('python3', ['-m', 'http.server', '9766', '--bind', '127.0.0.1', '--directory', path.resolve(root, '..')], { stdio: 'ignore' });
const previewServer = spawn('python3', ['-m', 'http.server', '9475', '--bind', '127.0.0.1', '--directory', '/tmp'], { stdio: 'ignore' });
const servers = [sourceServer, previewServer];
const onExit = () => servers.forEach(server => server.kill());
process.once('exit', onExit);
try {
  for (const url of ['http://127.0.0.1:9766/030_github-profile/preview-v2.html', 'http://127.0.0.1:9475/observatory-v2-export.html']) {
    for (let attempt = 0; attempt < 30; attempt += 1) {
      try { if ((await fetch(url)).ok) break; } catch { /* wait for the local server */ }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }
  const browser = await launch({ port: 9472, profile: 'observatory-v2-export', size: [1440, 1000] });
  try {
  await fs.mkdir(out, { recursive: true });
  for (const mobile of [false, true]) {
    const layoutWidth = mobile ? 390 : 1440;
    await browser.send('Emulation.setDeviceMetricsOverride', { width: layoutWidth, height: 1200, deviceScaleFactor: mobile ? 2 : 1, mobile: false });
    for (const theme of ['dark', 'light']) {
      for (const [name, selector, extra] of [
        ['hero', '.hero', '.hero-scope{transform:none!important}.scope-line{display:none!important}.hero-index{display:none!important}'],
        ['observe', '.observation.observe', '.project-links{display:none!important}'],
        ['record', '.observation.record', '.project-links{display:none!important}'],
        ['understand', '.observation.understand', '.editor-line{display:none!important}'],
      ]) {
        if (theme === 'light' && ['record', 'understand'].includes(name)) continue;
        const suffix = `${mobile ? '-mobile' : ''}`;
        const documentId = `${name}-${theme}${suffix}`;
        await fs.writeFile('/tmp/observatory-v2-export.html', documentFor(markup(selector), extra, documentId));
        await browser.goto(`http://127.0.0.1:9475/observatory-v2-export.html?${documentId}`, `main[data-export="${documentId}"]`);
        await browser.evaluate(`document.documentElement.dataset.theme=${JSON.stringify(theme)}`);
        await browser.evaluate('document.fonts.ready');
        const imageState = await browser.evaluate('Promise.all([...document.images].map(async img => {try { await img.decode(); } catch (error) { return {src: img.currentSrc, error: String(error)}; } return {src: img.currentSrc, loaded: img.complete && img.naturalWidth > 0}; }))');
        if (imageState.some(img => !img.loaded)) throw new Error(`${name} ${theme}${suffix}: ${JSON.stringify(imageState)}`);
        await browser.evaluate('new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))');
        const dimensions = await browser.evaluate(`(() => {const r=document.querySelector('main').getBoundingClientRect();return {width:r.width,height:r.height}})()`);
        const clip = { x: 0, y: 0, width: dimensions.width, height: dimensions.height, scale: 1 };
        const capture = () => browser.send('Page.captureScreenshot', { format: 'png', clip, captureBeyondViewport: true });
        if (name === 'hero') {
          const scope = await browser.evaluate(`(() => {const r=document.querySelector('.hero-scope').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()`);
          const base = Buffer.from((await capture()).data, 'base64');
          const extraCss = '.hero-scope{transform:none!important;background:transparent!important;border:0!important;box-shadow:none!important}.hero-scope::after,.scope-grid,.vitals-image{display:none!important}html,body,main,.hero{background:transparent!important}*{visibility:hidden!important}.scope-line{display:block!important;visibility:visible!important;animation:none!important;left:18%!important}.scope-line::before{visibility:visible!important}';
          await browser.evaluate(`document.querySelector('style').textContent+=${JSON.stringify(extraCss)}`);
          await browser.send('Emulation.setDefaultBackgroundColorOverride', { color: { r: 0, g: 0, b: 0, a: 0 } });
          const scanShot = await browser.send('Page.captureScreenshot', { format: 'png', clip: { ...scope, scale: 1 }, captureBeyondViewport: true });
          await browser.send('Emulation.setDefaultBackgroundColorOverride');
          const scan = scanShot.data;
          const label = 'cookabc — Small tools. Closely observed. Local-first software, careful interfaces, and useful details.';
          const animated = `<g class="scan-motion" clip-path="url(#scope)"><image width="${scope.width}" height="${scope.height}" href="data:image/png;base64,${scan}"><animate attributeName="x" values="0;${scope.width * 0.61};0" keyTimes="0;0.5;1" dur="9s" repeatCount="indefinite"/></image></g><image class="scan-still" width="${scope.width}" height="${scope.height}" href="data:image/png;base64,${scan}"/>`;
          const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${dimensions.width}" height="${dimensions.height}" viewBox="0 0 ${dimensions.width} ${dimensions.height}" role="img" aria-label="${escapeXml(label)}"><title>${escapeXml(label)}</title><style>${fonts}@media(prefers-reduced-motion:no-preference){.scan-still{display:none}}@media(prefers-reduced-motion:reduce){.scan-motion{display:none}}</style><defs><clipPath id="scope"><rect width="${scope.width}" height="${scope.height}"/></clipPath></defs><image width="${dimensions.width}" height="${dimensions.height}" href="data:image/png;base64,${base.toString('base64')}"/><g transform="translate(${scope.x} ${scope.y})">${animated}</g></svg>`;
          await fs.writeFile(path.join(out, `observatory-${name}-${theme}${suffix}.svg`), svg);
        } else {
          const shot = Buffer.from((await capture()).data, 'base64');
          const webp = await browser.evaluate(`(async()=>{const img=new Image();img.src='data:image/png;base64,${shot.toString('base64')}';await img.decode();const c=document.createElement('canvas');c.width=img.naturalWidth;c.height=img.naturalHeight;c.getContext('2d').drawImage(img,0,0);return c.toDataURL('image/webp',0.94).split(',')[1]})()`);
          await fs.writeFile(path.join(out, `observatory-${name}-${theme}${suffix}.webp`), Buffer.from(webp, 'base64'));
        }
      }
    }
  }
  for (const file of await fs.readdir(out)) {
    if (/observatory-.*\.(svg|webp)$/.test(file)) console.log(file, (await fs.stat(path.join(out, file))).size);
  }
} finally {
  await browser.close();
}
} finally {
  servers.forEach(server => server.kill());
  process.off('exit', onExit);
}
