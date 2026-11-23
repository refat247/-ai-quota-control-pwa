"""OCR Preview build smoke test (NOT part of default CI: needs dist-ocr/ and Pillow).
Serves dist-ocr on a real loopback origin, uploads a SYNTHETIC screenshot rendered here, and checks that
on-device OCR fills the paste box, the existing preview shows correct used %, nothing is saved, and every
request stays on the same origin. Run: OCR_MODULES_DIR=... npm run build:ocr-preview && python3 -I tests/ocr_preview_smoke.py"""
import io, json, sys, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist-ocr'
STORE = 'ai-quota-control-center-v1'

def font(size):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'):
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def synthetic_png():
    img = Image.new('RGB', (1280, 720), 'white'); d = ImageDraw.Draw(img)
    d.text((60, 40), 'Plan limits', fill='black', font=font(40))
    d.text((60, 150), '5-hour limit', fill='black', font=font(34))
    d.text((60, 210), 'Resets in 19m', fill=(90, 90, 90), font=font(30)); d.text((900, 210), '94% left', fill='black', font=font(30))
    d.text((60, 340), 'Weekly limit', fill='black', font=font(34))
    d.text((60, 400), 'Resets in 1d 7h', fill=(90, 90, 90), font=font(30)); d.text((900, 400), '20% left', fill='black', font=font(30))
    buf = io.BytesIO(); img.save(buf, 'PNG'); return buf.getvalue()

class Quiet(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=str(DIST), **k)
    def log_message(self, *a): pass
    def guess_type(self, path):
        return 'application/gzip' if path.endswith('.gz') else super().guess_type(path)

def main(png_path=None):
    assert DIST.exists(), 'run npm run build:ocr-preview first'
    png = Path(png_path).read_bytes() if png_path else synthetic_png()
    srv = ThreadingHTTPServer(('127.0.0.1', 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    origin = f'http://127.0.0.1:{srv.server_address[1]}'
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True, args=['--no-sandbox'])
            ctx = b.new_context(viewport={'width': 390, 'height': 844}, service_workers='block'); page = ctx.new_page()
            page.on('dialog', lambda d: d.accept())
            errors, urls, csp = [], [], []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda m: csp.append(m.text) if 'Content Security Policy' in m.text else None)
            page.on('request', lambda r: urls.append(r.url))
            page.goto(origin + '/', wait_until='domcontentloaded')
            page.locator('button[data-tab="quotas"]').first.click()
            page.locator('#usagePanel summary').click()
            assert page.locator('label[for="usageOcrFile"]').is_visible(), 'OCR button missing'
            assert page.locator('#ocrPreviewBanner').count() == 1, 'preview banner missing'
            page.locator('#usageOcrFile').set_input_files(files=[{'name': 'shot.png', 'mimeType': 'image/png', 'buffer': png}])
            # The preview page's CSP forbids string eval, so poll through locators (no page.evaluate/wait_for_function).
            import time
            deadline = time.time() + 120
            while time.time() < deadline and len(page.locator('#usagePaste').input_value()) <= 10:
                page.wait_for_timeout(500)
            text = page.locator('#usagePaste').input_value()
            print('OCR TEXT >>>\n' + text + '\n<<<')
            print('STATUS >>> ' + page.locator('#usageOcrStatus').inner_text())
            assert 'Nothing is saved yet' in page.locator('#usageOcrStatus').inner_text()
            page.locator('[data-usage-action="preview"]').click()
            panel = page.locator('#usagePanel').inner_text(); print(panel)
            if not png_path:
                assert 'used 6%' in panel and 'used 80%' in panel, panel
            assert page.locator('[data-usage-action="confirm"]').is_disabled(), 'confirm must stay blocked without a pool'
            state = ctx.storage_state()
            assert not [o for o in state['origins'] if o.get('localStorage')], 'OCR/preview wrote localStorage'
            assert not state['cookies'], 'cookies set'
            foreign = [u for u in urls if not u.startswith(origin) and not u.startswith('data:') and not u.startswith('blob:')]
            assert not foreign, foreign
            assert not errors, errors
            assert not csp, csp
            print('PASS OCR preview: on-device OCR -> paste box -> preview (6% / 80% used), nothing saved, same-origin only, no CSP violations')
            b.close()
    finally:
        srv.shutdown(); srv.server_close()

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
