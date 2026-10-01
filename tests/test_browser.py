"""HTTP browser checks with the actual site files and original local media.

Usage: python tests/test_browser.py --browser chromium
Requires Playwright and the selected browser. Contact responses and external
video frames are mocked; no contact message is sent. Google Fonts may load.
"""
import argparse
import functools
import json
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'game.html', 'history.html', 'fun.html', 'contact.html', 'thank-you.html']
WIDTHS = [320, 375, 390, 768, 1024, 1440]
parser = argparse.ArgumentParser()
parser.add_argument('--browser', choices=['chromium', 'firefox', 'webkit'], default='chromium')
parser.add_argument('--baseline', type=Path)
args = parser.parse_args()
REPORTS = ROOT / 'reports' / args.browser
REPORTS.mkdir(parents=True, exist_ok=True)
checks, errors, missing, font_status = [], [], [], []

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def serve(directory):
    server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Handler, directory=str(directory)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, 'http://127.0.0.1:' + str(server.server_port) + '/'

def check(description, condition):
    checks.append({'check': description, 'passed': bool(condition)})
    assert condition, description

server, base = serve(ROOT)
baseline_server = None
try:
    with sync_playwright() as pw:
        browser = getattr(pw, args.browser).launch()
        context = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
        context.route('https://formspree.io/**', lambda r: r.fulfill(status=503, content_type='application/json', body='{"error":"Mock response. Nothing was sent."}'))
        context.route('https://www.youtube-nocookie.com/**', lambda r: r.fulfill(status=200, content_type='text/html', body='<p>Third-party video playback is not part of this test.</p>'))
        context.route('https://www.youtube.com/embed/**', lambda r: r.fulfill(status=200, content_type='text/html', body='<p>Video mock</p>'))
        page = context.new_page()
        page.set_default_timeout(12000)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('response', lambda r: missing.append(r.url) if r.url.startswith(base) and r.status >= 400 else None)

        def go(filename):
            page.goto(base + filename, wait_until='load')
            page.evaluate('document.fonts.ready')

        for width in WIDTHS:
            page.set_viewport_size({'width': width, 'height': 900})
            for filename in PAGES:
                go(filename)
                check(f'{filename}: no horizontal overflow at {width}px', page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
                check(f'{filename}: single main and h1 at {width}px', page.locator('main').count() == 1 and page.locator('h1').count() == 1)
                check(f'{filename}: local images loaded at {width}px', page.evaluate("[...document.images].filter(i=>i.loading !== 'lazy').every(i=>i.complete && i.naturalWidth>0)"))
                if width < 992:
                    page.locator('.navbar-toggler').click()
                    check(f'{filename}: mobile menu opens at {width}px', page.locator('#navbarNav').is_visible())
                    page.keyboard.press('Escape')
                    check(f'{filename}: Escape closes menu at {width}px', not page.locator('#navbarNav').is_visible())
                if width in (390, 1440):
                    page.screenshot(path=str(REPORTS / f'{filename[:-5]}-{width}.png'), full_page=True)
                    font_status.append({'page': filename, 'width': width, 'fonts': page.evaluate("[...document.fonts].map(f=>({family:f.family,status:f.status}))")})

        page.set_viewport_size({'width': 390, 'height': 844})
        go('game.html')
        check('Empty name locks all curse controls', page.locator('.curse-button:disabled').count() == 3)
        page.locator('#name').fill('   ')
        page.locator('#name').blur()
        check('Whitespace gives visible validation', page.locator('#name-error').is_visible() and page.locator('#firstButton').is_disabled())
        page.locator('#name').fill('Sam O’Brien-Olinger')
        check('Valid name immediately unlocks only the first part', page.locator('#firstButton').is_enabled() and page.locator('#secondButton').is_disabled())
        for button, output in [('firstButton','firstResult'), ('secondButton','secondResult'), ('thirdButton','thirdResult')]:
            page.locator('#' + button).click()
            check(f'{button}: phrase generated and button locks', bool(page.locator('#' + output).inner_text()) and page.locator('#' + button).is_disabled())
        check('Three parts unlock the final reveal', page.locator('#finalButton').is_enabled())
        page.locator('#motion-toggle').click()
        page.locator('#finalButton').click()
        check('Reveal uses a modal dialog', page.locator('#loading-panel').evaluate('(el)=>el.open'))
        page.keyboard.press('Escape')
        check('Reveal can be cancelled without losing progress', page.locator('#finalButton').is_enabled() and bool(page.locator('#thirdResult').inner_text()))
        page.locator('#finalButton').click()
        page.locator('#curse-and-beetlejuice').wait_for(state='visible')
        check('Result includes name and receives focus', page.locator('#finalResult').inner_text().startswith('Sam O’Brien-Olinger ') and page.locator('#result-title').evaluate('(el)=>el===document.activeElement'))
        for width in (390, 1440):
            page.set_viewport_size({'width':width, 'height':900})
            page.screenshot(path=str(REPORTS / f'result-{width}.png'), full_page=True)
            check(f'Result fits at {width}px', page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'))
        page.locator('#refresh').click()
        check('Replay resets and focuses name without navigation', page.locator('#name').input_value() == '' and page.locator('#name').evaluate('(el)=>el===document.activeElement'))
        page.locator('#name').fill('<img src=x onerror=alert(1)>')
        for button in ['firstButton','secondButton','thirdButton']:
            page.locator('#'+button).click()
        page.locator('#finalButton').click()
        page.locator('#curse-and-beetlejuice').wait_for(state='visible')
        check('Markup-like names stay literal text', page.locator('#finalResult img').count() == 0 and '<img' in page.locator('#finalResult').inner_text())

        go('contact.html')
        page.locator('#fullname').fill('UI regression test')
        page.locator('#email').fill('bad-email')
        page.locator('#message').fill('This message must never be sent. All responses are mocked.')
        page.locator('#send-message').click()
        check('Invalid email blocked', page.locator('#email').evaluate('(el)=>!el.validity.valid'))
        page.locator('#email').fill('test@example.com')
        page.locator('#send-message').click()
        page.wait_for_function("document.querySelector('#form-status').textContent.includes('could not confirm')")
        check('Failure preserves user input', 'must never be sent' in page.locator('#message').input_value() and page.locator('#send-message').is_enabled())
        page.route('https://formspree.io/**', lambda r: r.fulfill(status=200, content_type='application/json', body='{"ok":true}'))
        page.locator('#send-message').click()
        page.wait_for_url('**/thank-you.html')
        check('Confirmed mocked response navigates to thank-you', 'sent successfully' in page.locator('#thanks-message').inner_text())
        page.reload()
        check('Direct thank-you does not claim unconfirmed delivery', 'sent successfully' not in page.locator('#thanks-message').inner_text())
        check('No local asset failures', not missing)
        check('No uncaught JavaScript errors', not errors)

        # Baseline screenshots are visual evidence, not test assertions.
        if args.baseline:
            baseline_server, baseline = serve(args.baseline)
            before = context.new_page()
            for width in (390, 1440):
                before.set_viewport_size({'width':width, 'height':900})
                for filename in ['index.html', 'game.html']:
                    before.goto(baseline + filename, wait_until='load')
                    before.evaluate('document.fonts.ready')
                    before.screenshot(path=str(REPORTS / f'before-{filename[:-5]}-{width}.png'), full_page=True)
            before.close()
        browser.close()
finally:
    server.shutdown()
    if baseline_server:
        baseline_server.shutdown()
    summary = {'browser':args.browser, 'passed':sum(c['passed'] for c in checks), 'checks':checks, 'javascript_errors':errors, 'missing_local_assets':missing, 'font_status':font_status, 'limits':['Formspree responses mocked; no message sent.', 'Third-party videos mocked; availability/playback not verified.', 'Browser engines on Linux, not physical mobile devices.', 'Not a complete accessibility audit.']}
    (REPORTS / 'results.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
