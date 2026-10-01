"""Responsive regression suite; no messages are sent or external videos played.

python tests/test_responsive.py --browser chromium
python tests/test_responsive.py --offline --executable /usr/bin/chromium

HTTP mode uses original local media and available Google Fonts. Offline mode
inlines original images/CSS and mocks storage/audio; it is not live-site proof.
"""
import argparse
import base64
import functools
import json
import mimetypes
import re
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'game.html', 'history.html', 'fun.html', 'contact.html', 'thank-you.html']
SIZES = [(280,653),(320,568),(360,640),(375,667),(390,844),(414,896),
         (430,932),(540,720),(600,960),(700,900),(701,900),(768,1024),
         (820,1180),(912,1368),(991,900),(992,900),(1024,768),(1280,800),
         (1366,768),(1440,900),(1920,1080),(2560,1440),(3440,1440),(3840,2160),
         (568,320),(667,375),(844,390),(932,430),(1180,820),(1280,256),(320,256)]
parser = argparse.ArgumentParser()
parser.add_argument('--browser', choices=['chromium','firefox','webkit'], default='chromium')
parser.add_argument('--offline', action='store_true')
parser.add_argument('--executable')
args = parser.parse_args()
REPORT = ROOT/'reports'/('responsive-'+args.browser+('-offline' if args.offline else ''))
REPORT.mkdir(parents=True, exist_ok=True)
checks, errors, missing, fonts = [], [], [], []
server = None
version = ''

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass

def check(label, condition):
    checks.append({'check':label, 'passed':bool(condition)})
    assert condition, label

@functools.lru_cache(maxsize=32)
def data_uri(path):
    return 'data:'+(mimetypes.guess_type(str(path))[0] or 'application/octet-stream')+';base64,'+base64.b64encode(path.read_bytes()).decode()

@functools.lru_cache(maxsize=8)
def fixture(filename):
    source = (ROOT/filename).read_text()
    source = re.sub(r'<link[^>]*>', '', source)
    source = re.sub(r'<script[^>]*src=[^>]*></script>', '', source)
    css = (ROOT/'assets/css/styles.css').read_text()
    css = re.sub(r'url\([\'\"]?([^\)\'\"]+)[\'\"]?\)', lambda m:'url("'+data_uri((ROOT/'assets/css'/m[1]).resolve())+'")', css)
    source = re.sub(r'src="(assets/images/[^"]+)"', lambda m:'src="'+data_uri(ROOT/m[1])+'"', source)
    source = re.sub(r'<iframe\b.*?</iframe>', '<iframe title="Offline video placeholder" srcdoc="Video not tested"></iframe>', source, flags=re.S)
    return source.replace('</head>', '<style>'+css+'</style></head>')

# Test for protruding content, not just a scrollbar hidden by overflow-x CSS.
FIT = """() => {
 const viewport=document.documentElement.clientWidth;
 if(document.documentElement.scrollWidth>viewport+1) return false;
 return [...document.querySelectorAll('body *')].every(el=>{
  if(el.closest('.sr-only,.skip-link')) return true;
  const r=el.getBoundingClientRect();
  return !r.width || !r.height || (r.left >= -1 && r.right <= viewport+1);
 });
}"""
TEXT_FITS = """() => [...document.querySelectorAll('button,.nav-link')].every(el=>{
 if(!el.getClientRects().length)return true;
 const box=el.getBoundingClientRect(),range=document.createRange();range.selectNodeContents(el);
 return [...range.getClientRects()].every(r=>r.left>=box.left-1 && r.right<=box.right+1 && r.top>=box.top-1 && r.bottom<=box.bottom+1);
})"""
LEGACY_MEDIA = """() => {const match=window.matchMedia.bind(window);window.matchMedia=q=>{
 const result=match(q);Object.defineProperty(result,'addEventListener',{value:undefined});return result;};}"""
OFFLINE_INIT = """() => {
 const store=()=>({getItem:k=>null,setItem:(k,v)=>{},removeItem:k=>{}});
 Object.defineProperty(window,'localStorage',{value:store(),configurable:true});
 Object.defineProperty(window,'sessionStorage',{value:store(),configurable:true});
 window.Audio=class { play(){return Promise.resolve();} pause(){} };
}"""

try:
    if not args.offline:
        server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        base='http://127.0.0.1:'+str(server.server_port)+'/'
    with sync_playwright() as pw:
        browser=getattr(pw,args.browser).launch(executable_path=args.executable)
        version=browser.version
        def context(**kw):
            c=browser.new_context(reduced_motion='reduce', **kw)
            c.route('https://formspree.io/**',lambda r:r.fulfill(status=503,content_type='application/json',body='{"error":"Mock. Nothing sent."}'))
            c.route('https://www.youtube-nocookie.com/**',lambda r:r.fulfill(status=200,content_type='text/html',body='<p>Video playback not tested.</p>'))
            if args.offline: c.route('**/*',lambda r:r.abort())
            c.on('page',lambda page:page.on('pageerror',lambda e:errors.append(str(e))))
            return c
        c=context()
        def go(filename, viewport=(390,844), c=c, init=None):
            page=c.new_page();page.set_viewport_size({'width':viewport[0],'height':viewport[1]})
            page.set_default_timeout(12000)
            if args.offline:
                page.set_content(fixture(filename),wait_until='domcontentloaded')
                page.evaluate(OFFLINE_INIT)
                if init:page.evaluate(init)
                page.add_script_tag(content=(ROOT/'assets/js/script.js').read_text())
            else:
                if init:page.add_init_script('('+init+')()')
                page.on('response',lambda r:missing.append(r.url) if r.url.startswith(base) and r.status>=400 else None)
                page.goto(base+filename,wait_until='load')
                page.evaluate('document.fonts.ready')
            page.wait_for_function("[...document.images].filter(i=>i.loading!=='lazy').every(i=>i.complete&&i.naturalWidth>0)")
            return page
        def finish_game(page, name='Sam'):
            page.locator('#name').fill(name)
            for id in ['firstButton','secondButton','thirdButton']:page.locator('#'+id).click()
            page.locator('#finalButton').click()
            page.locator('#curse-and-beetlejuice').wait_for(state='visible')
        for size in SIZES:
            for filename in PAGES:
                page=go(filename,size);tag=f'{filename} {size[0]}x{size[1]}'
                check(tag+' fits without hidden horizontal overflow',page.evaluate(FIT))
                check(tag+' controls contain their labels',page.evaluate(TEXT_FITS))
                check(tag+' original eager images rendered',page.evaluate("[...document.images].filter(i=>i.loading!=='lazy').every(i=>i.complete&&i.naturalWidth>0)"))
                if size[0]<992:
                    page.locator('.navbar-toggler').click()
                    check(tag+' expanded navigation fits',page.locator('#navbarNav').is_visible() and page.evaluate(FIT))
                    page.keyboard.press('Escape')
                    check(tag+' menu focus restored',page.locator('.navbar-toggler').evaluate('(e)=>e===document.activeElement'))
                if filename=='history.html':
                    check(tag+' all trailers preserve 16:9',page.locator('.video-frame').evaluate_all('(els)=>els.length===3&&els.every(e=>Math.abs(e.clientWidth/e.clientHeight-16/9)<.035)'))
                if filename in ['index.html','contact.html','game.html'] and size in [(320,568),(844,390),(1440,900)]:
                    page.screenshot(path=str(REPORT/f'{filename[:-5]}-{size[0]}x{size[1]}.png'),full_page=True)
                if size==(1440,900):fonts.append({'page':filename,'fonts':page.evaluate('[...document.fonts].map(f=>({family:f.family,status:f.status}))')})
                page.close()
        # Enlarged text + reflow; root scaling is explicit, not a claim of browser UI zoom.
        for width in [320,390,600,768,1024,1440]:
            for filename in PAGES:
                page=go(filename,(width,900))
                page.evaluate("document.documentElement.style.fontSize='200%'")
                check(f'{filename} at {width}px with 200% root text fits',page.evaluate(FIT) and page.evaluate(TEXT_FITS))
                if width<992:
                    page.locator('.navbar-toggler').click()
                    check(f'{filename} 200% text navigation at {width}px fits',page.evaluate(FIT) and page.evaluate(TEXT_FITS))
                page.close()
        for filename in PAGES:
            page=go(filename,(320,568))
            page.add_style_tag(content='* {line-height:1.5!important;letter-spacing:.12em!important;word-spacing:.16em!important} p{margin-bottom:2em!important}')
            check(filename+' custom text spacing reflows',page.evaluate(FIT) and page.evaluate(TEXT_FITS))
            page.close()
        # All result states, including long unbroken user text and orientation changes.
        page=go('game.html')
        finish_game(page,'W'*60)
        curse=page.locator('#finalResult').inner_text()
        for size in SIZES:
            page.set_viewport_size({'width':size[0],'height':size[1]})
            check(f'Long-name result fits {size}',page.evaluate(FIT) and page.evaluate(TEXT_FITS))
            check(f'Resizing preserves result {size}',page.locator('#finalResult').inner_text()==curse)
        page.set_viewport_size({'width':320,'height':568})
        page.evaluate("document.documentElement.style.fontSize='200%'")
        check('Long-name result reflows with 200% text',page.evaluate(FIT) and page.evaluate(TEXT_FITS))
        page.screenshot(path=str(REPORT/'result-320-text200.png'),full_page=True)
        page.locator('#refresh').click()
        check('Replay after resizing resets state',page.locator('#name').input_value()=='' and page.locator('#firstButton').is_disabled())
        page.close()
        page=go('game.html',(390,844))
        page.locator('#name').fill('Orientation test');page.locator('#firstButton').click()
        part=page.locator('#firstResult').inner_text()
        for size in [(844,390),(992,700),(991,700),(390,844)]:
            page.set_viewport_size({'width':size[0],'height':size[1]})
            check(f'Partial game survives orientation and breakpoint {size}',page.locator('#firstResult').inner_text()==part and page.locator('#secondButton').is_enabled())
        page.close()
        # Loading cancellation stays usable in short landscape and zoom-equivalent windows.
        for size in [(568,320),(844,390),(1280,256),(320,256)]:
            page=go('game.html',size)
            page.locator('#motion-toggle').click()
            page.locator('#name').fill('Landscape')
            for id in ['firstButton','secondButton','thirdButton']:page.locator('#'+id).click()
            page.locator('#finalButton').click()
            check(f'Dialog bounded within short viewport {size}',page.locator('#loading-panel').evaluate('(e)=>{let r=e.getBoundingClientRect();return r.top>=-1&&r.bottom<=innerHeight+1&&r.left>=-1&&r.right<=innerWidth+1}'))
            page.locator('#cancel-curse').click()
            check(f'Cancellation preserves progress {size}',page.locator('#finalButton').is_enabled())
            page.close()
        # Specific capability fallbacks, not claimed tests of old browser releases.
        page=go('game.html',init=LEGACY_MEDIA)
        finish_game(page)
        check('Legacy MediaQueryList.addListener still permits complete gameplay',page.locator('#curse-and-beetlejuice').is_visible())
        page.close()
        page=go('game.html')
        page.evaluate("document.querySelector('#loading-panel').showModal=undefined")
        finish_game(page)
        check('Missing native dialog skips animation, not the result',page.locator('#curse-and-beetlejuice').is_visible())
        page.locator('#refresh').click()
        check('Replay still works without native dialog',page.locator('#name').input_value()=='')
        page.close()
        for api in ['fetch','AbortController','FormData']:
            page=go('contact.html',init=f'() => {{window.{api}=undefined}}')
            native=page.evaluate("""()=>{const f=document.querySelector('form');let unhandled=false;
                f.addEventListener('submit',e=>{unhandled=!e.defaultPrevented;e.preventDefault()});
                f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));return unhandled;}""")
            check(f'Missing {api} leaves native contact POST available without submitting',native)
            page.close()
        if not args.offline:
            # Emulated touch input in phone and tablet contexts (not physical devices).
            for size in [(390,844),(844,390),(1024,1366)]:
                mobile=context(has_touch=True,device_scale_factor=2)
                page=go('game.html',size,c=mobile)
                check(f'Touch background scrolls at {size}',page.evaluate("getComputedStyle(document.body).backgroundAttachment==='scroll'"))
                if size[0]<992:page.locator('.navbar-toggler').tap();page.keyboard.press('Escape')
                page.locator('#name').fill('Touch')
                for id in ['firstButton','secondButton','thirdButton','finalButton']:page.locator('#'+id).tap()
                page.locator('#curse-and-beetlejuice').wait_for(state='visible')
                check(f'Touch taps complete game at {size}',page.locator('#finalResult').inner_text().startswith('Touch '))
                mobile.close()
            # No JavaScript, external fonts unavailable, and denied local storage.
            basic=context(java_script_enabled=False)
            page=basic.new_page()
            page.set_viewport_size({'width':320,'height':568});page.goto(base+'contact.html')
            check('No-JavaScript mobile navigation remains visible',page.locator('#navbarNav').is_visible())
            check('No-JavaScript contact remains native POST',page.locator('form').get_attribute('method')=='POST')
            basic.close()
        fallback=context()
        fallback.route('https://fonts.googleapis.com/**',lambda r:r.abort())
        fallback.route('https://fonts.gstatic.com/**',lambda r:r.abort())
        for filename in PAGES:
            page=go(filename,(320,568),c=fallback)
            check(filename+' works with fallback fonts',page.evaluate(FIT) and page.evaluate(TEXT_FITS));page.close()
        fallback.close()
        page=go('game.html',init="""()=>{for(const key of ['localStorage','sessionStorage'])Object.defineProperty(window,key,{configurable:true,get(){throw new Error('Storage denied in test')}})}""")
        finish_game(page)
        check('Denied storage does not stop gameplay',page.locator('#curse-and-beetlejuice').is_visible());page.close()
        check('No missing local assets',not missing)
        check('No uncaught JavaScript errors',not errors)
        browser.close()
finally:
    if server:server.shutdown()
    summary={'browser':args.browser,'version':version,'mode':'offline fixtures' if args.offline else 'HTTP original-media',
             'viewports':SIZES,'passed':sum(c['passed'] for c in checks),'total':len(checks),'checks':checks,
             'javascript_errors':errors,'missing_local_assets':missing,'fonts':fonts,
             'limits':['No physical devices or historical browser versions tested.',
                       '200% root text scaling; 320 CSS-pixel reflow is a 400%-zoom equivalent, not an actual browser UI zoom command.',
                       'External videos and contact responses mocked; no messages sent.',
                       'Not complete WCAG conformance testing.',
                       'Offline mode mocks storage and audio and uses fallback fonts; HTTP mode loads local assets.']}
    (REPORT/'results.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps({'browser':args.browser,'passed':summary['passed'],'total':len(checks),'report':str(REPORT/'results.json')}))
