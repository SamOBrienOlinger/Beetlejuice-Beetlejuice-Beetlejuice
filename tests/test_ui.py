"""Offline Chromium regression checks: python tests/test_ui.py.

Requires Python 3, Playwright and Chromium. The browser renders the actual local
HTML/CSS/JS without navigation or external downloads. Artwork/fonts/audio/video
are blocked. Storage, clipboard, Formspree responses and the final navigation
boundary are mocked. NO MESSAGE IS SENT. This is not a live-site, cross-browser,
asset-rendering or actual delivery test.
"""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'game.html', 'history.html', 'fun.html', 'contact.html', 'thank-you.html']
WIDTHS = [320, 375, 390, 768, 1024, 1440]
results = []


def check(description, condition):
    assert condition, description
    results.append(description)


class OfflinePage:
    """Isolated document fixtures; substitute only external browser boundaries."""
    def __init__(self, context, errors, javascript=True):
        self.context, self.errors, self.javascript = context, errors, javascript
        self.page = None
        self.local, self.session = {}, {}
        self.viewport = {'width': 1440, 'height': 960}
        self.filename = None

    def __getattr__(self, name):
        return getattr(self.page, name)

    def set_viewport_size(self, viewport):
        self.viewport = viewport
        if self.page: self.page.set_viewport_size(viewport)

    def open(self, filename):
        if self.page:
            if self.javascript:
                self.local, self.session = self.page.evaluate('[window.__local, window.__session]')
            self.page.close()
        self.filename = filename
        self.page = self.context.new_page()
        self.page.set_viewport_size(self.viewport)
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        import re
        source = (ROOT / filename).read_text()
        source = re.sub(r'<link[^>]*>', '', source)
        source = re.sub(r'<script[^>]*src=[^>]*></script>', '', source)
        source = source.replace('</head>', '<style>' + (ROOT / 'assets/css/styles.css').read_text() + '</style></head>')
        self.page.set_content(source, wait_until='domcontentloaded')
        if self.javascript:
            self.page.evaluate("""([local, session]) => {
                window.__local = local; window.__session = session;
                const storage = (values) => ({getItem:key => values[key] ?? null,
                  setItem:(key,value) => {values[key]=String(value)},
                  removeItem:key => {delete values[key]}});
                Object.defineProperty(window, 'localStorage', {value:storage(local), configurable:true});
                Object.defineProperty(window, 'sessionStorage', {value:storage(session), configurable:true});
                window.fetch = async () => {throw new Error('Network disabled in offline tests')};
            }""", [self.local, self.session])
            script = (ROOT / 'assets/js/script.js').read_text()
            script = script.replace("window.location.assign('thank-you.html');", "window.__navigation = 'thank-you.html';")
            self.page.add_script_tag(content=script)


def go(page, filename):
    page.open(filename)


with sync_playwright() as pw:
    executable = os.environ.get('CHROMIUM_EXECUTABLE')
    if not executable and Path('/usr/bin/chromium').exists():
        executable = '/usr/bin/chromium'
    browser = pw.chromium.launch(executable_path=executable, headless=True, args=['--no-sandbox'])
    context = browser.new_context(viewport={'width': 1440, 'height': 960}, reduced_motion='reduce')
    # Never call external services during tests; fonts and images are out of scope.
    context.route('**/*', lambda route: route.abort())
    errors = []
    page = OfflinePage(context, errors)

    for width in WIDTHS:
        page.set_viewport_size({'width': width, 'height': 900})
        for filename in PAGES:
            go(page, filename)
            overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 1')
            check(f'{filename}: no horizontal overflow at {width}px (assets blocked)', not overflow)
            check(f'{filename}: one main and one h1 at {width}px', page.locator('main').count() == 1 and page.locator('h1').count() == 1)
            check(f'{filename}: no duplicate IDs at {width}px', page.evaluate('''() => {
              const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
              return new Set(ids).size === ids.length;
            }'''))
            if width < 992:
                check(f'{filename}: mobile menu initially closed at {width}px', not page.locator('#navbarNav').is_visible())
                page.locator('.navbar-toggler').click()
                check(f'{filename}: mobile menu opens at {width}px', page.locator('#navbarNav').is_visible())
                page.keyboard.press('Escape')
                check(f'{filename}: Escape restores menu focus at {width}px', page.locator('.navbar-toggler').evaluate('(el) => el === document.activeElement'))

    page.set_viewport_size({'width': 390, 'height': 844})
    go(page, 'game.html')
    check('All curse controls disabled before a name', page.locator('.curse-button:disabled').count() == 3 and page.locator('#finalButton').is_disabled())
    page.locator('#name').fill('   ')
    page.locator('#name').blur()
    check('Whitespace is rejected with visible feedback', page.locator('#name-error').is_visible() and page.locator('#firstButton').is_disabled())
    page.locator('#name').fill('Sam O’Brien-Olinger')
    check('Typing a valid name unlocks only the first part immediately', page.locator('#firstButton').is_enabled() and page.locator('#secondButton').is_disabled() and page.locator('#finalButton').is_disabled())
    for button, output in [('firstButton','firstResult'),('secondButton','secondResult'),('thirdButton','thirdResult')]:
        page.locator('#' + button).click()
        check(f'{button}: generates a phrase and locks its control', bool(page.locator('#' + output).inner_text()) and page.locator('#' + button).is_disabled())
    check('Final reveal unlocks after all three parts', page.locator('#finalButton').is_enabled() and page.locator('#curse-progress').get_attribute('value') == '3')
    page.locator('#name').fill('')
    check('Clearing a completed name relocks the reveal', page.locator('#finalButton').is_disabled())
    page.locator('#name').fill('Sam')
    page.evaluate("localStorage.setItem('beetlejuice-motion','running')")
    # Use the motion control to allow the longer spinner while checking cancel.
    page.locator('#motion-toggle').click()
    page.locator('#finalButton').click()
    check('Spinner opens as a modal dialog', page.locator('#loading-panel').evaluate('(el) => el.open'))
    page.keyboard.press('Escape')
    check('Escape cancels reveal without losing the three parts', not page.locator('#loading-panel').is_visible() and page.locator('#finalButton').is_enabled() and bool(page.locator('#thirdResult').inner_text()))
    page.locator('#finalButton').click()
    page.locator('#curse-and-beetlejuice').wait_for(state='visible')
    check('Result reveals safely and receives heading focus', page.locator('#finalResult').inner_text().startswith('Sam ') and page.locator('#result-title').evaluate('(el) => el === document.activeElement'))
    check('Footer is not hidden while playing', page.locator('#foot').is_visible())
    page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true,value:{writeText:async(text)=>{window.copiedCurse=text;}}})")
    page.locator('#copy-curse').click()
    page.wait_for_function("document.querySelector('#copy-status').textContent.includes('has been copied')")
    check('Copy uses the full generated text', page.evaluate('window.copiedCurse') == page.locator('#finalResult').inner_text())
    page.evaluate("Object.defineProperty(navigator, 'clipboard', {configurable:true,value:{writeText:async()=>{throw new Error('denied');}}})")
    page.locator('#copy-curse').click()
    page.wait_for_function("document.querySelector('#copy-status').textContent.includes('Automatic copying')")
    check('Denied clipboard permission gives a manual fallback', page.evaluate('getSelection().toString()') == page.locator('#finalResult').inner_text())
    page.locator('#refresh').click()
    check('Replay clears state without a reload', page.locator('#name').input_value() == '' and page.locator('#firstResult').inner_text() == '' and page.locator('#firstButton').is_disabled())
    check('Replay focuses the name field', page.locator('#name').evaluate('(el) => el === document.activeElement'))

    # Injection-shaped input must be literal text, never executable markup.
    page.locator('#name').fill('<img src=x onerror=alert(1)>')
    for button in ['firstButton','secondButton','thirdButton']:
        page.locator('#' + button).click()
    page.locator('#finalButton').click()
    page.locator('#curse-and-beetlejuice').wait_for(state='visible')
    check('HTML-looking names are output as text', page.locator('#finalResult img').count() == 0 and '<img' in page.locator('#finalResult').inner_text())
    page.locator('#refresh').click()
    page.locator('#motion-toggle').click()
    # Random generation invariant through repeated complete browser journeys.
    common = set('a an and at be been by for has in is of on shall that the their through to will with'.split())
    import re
    for run in range(20):
        page.locator('#name').fill('Test')
        for button in ['firstButton','secondButton','thirdButton']:
            page.locator('#' + button).click()
        seen = set()
        for output in ['firstResult','secondResult','thirdResult']:
            phrase_words = set()
            for word in page.locator('#' + output).inner_text().split():
                word = re.sub(r"['’]s$", '', word.lower())
                word = re.sub('[^a-z0-9]', '', word)
                if word.endswith('ly') and len(word) > 5: word = word[:-2]
                if word and word not in common: phrase_words.add(word)
            check(f'Random round {run + 1}: {output} does not repeat earlier meaningful words', not seen.intersection(phrase_words))
            seen |= phrase_words
        # Refresh via actual controls rather than exposing private implementation state.
        page.locator('#finalButton').click()
        page.locator('#curse-and-beetlejuice').wait_for(state='visible')
        page.locator('#refresh').click()

    go(page, 'contact.html')
    check('Contact inputs have real, associated labels', page.get_by_label('Full name', exact=True).count() == 1 and page.get_by_label('Email', exact=True).get_attribute('type') == 'email' and page.get_by_label('Message', exact=True).count() == 1)
    page.locator('#fullname').fill('Test Person')
    page.locator('#email').fill('invalid-address')
    page.locator('#message').fill('Test only. Do not send.')
    page.locator('#send-message').click()
    check('Malformed email is blocked before network submission', page.locator('#email').evaluate('(el) => !el.validity.valid') and page.filename == 'contact.html')
    page.locator('#email').fill('test@example.com')
    page.evaluate("() => { window.fetch = async () => ({ok:false,json:async()=>({error:'test'})}); }")
    page.locator('#send-message').click()
    page.wait_for_function("document.querySelector('#form-status').textContent.includes('could not confirm')")
    check('Server failure preserves the message and re-enables submit', page.locator('#message').input_value() == 'Test only. Do not send.' and page.locator('#send-message').is_enabled())
    page.evaluate("() => { window.fetch = async () => {throw new Error('Network test failure')}; }")
    page.locator('#send-message').click()
    page.wait_for_function("document.querySelector('#form-status').textContent.includes('could not confirm')")
    check('Network failure preserves the message', page.locator('#message').input_value() == 'Test only. Do not send.')
    page.evaluate("() => { window.fetch = async () => ({ok:true,json:async()=>({ok:true})}); }")
    page.locator('#send-message').click()
    page.wait_for_function("window.__navigation === 'thank-you.html'")
    go(page, 'thank-you.html')
    check('Only mocked confirmed success reaches thank-you', 'sent successfully' in page.locator('#thanks-message').inner_text())
    go(page, 'thank-you.html')
    check('Direct thank-you page does not falsely claim delivery', 'sent successfully' not in page.locator('#thanks-message').inner_text())

    go(page, 'index.html')
    check('Motion control works without changing the original GIF asset path in markup', page.locator('#motion-toggle').is_visible())
    page.locator('#motion-toggle').click()
    paused = page.locator('body').evaluate("el => el.classList.contains('motion-paused')")
    go(page, 'history.html')
    check('Motion preference persists across pages', page.locator('body').evaluate("el => el.classList.contains('motion-paused')") == paused)
    check('Trailers have descriptive titles and lazy loading', page.locator('iframe[title][loading="lazy"]').count() == 3)
    check('Every trailer has a separate fallback link', page.locator('.video-thumbnails a').count() == 3)

    # No-JavaScript browsing still exposes navigation, contact and reading pages.
    nojs = browser.new_context(java_script_enabled=False, viewport={'width': 320, 'height': 800})
    nojs.route('**/*', lambda route: route.abort())
    basic = OfflinePage(nojs, errors, javascript=False)
    basic.set_viewport_size({'width':320,'height':800})
    go(basic, 'contact.html')
    check('Without JavaScript, mobile navigation remains available', basic.locator('#navbarNav').is_visible())
    check('Without JavaScript, contact still has its real POST action', basic.locator('#contact-form').get_attribute('action') == 'https://formspree.io/f/mqkvyjbw' and basic.locator('#email').get_attribute('type') == 'email')
    go(basic, 'game.html')
    check('Without JavaScript, game explains the requirement', basic.locator('noscript').is_visible())
    check('No uncaught JavaScript errors in tested journeys', not errors)
    print(json.dumps({'passed': len(results), 'checks': results, 'javascript_errors': errors, 'limitations': ['External artwork, audio, Google fonts and videos blocked.', 'Contact responses mocked; no message was sent.', 'Chromium only, not Safari or Firefox.', 'Offline documents; storage, clipboard, network and navigation boundaries mocked.']}, indent=2))
    browser.close()
