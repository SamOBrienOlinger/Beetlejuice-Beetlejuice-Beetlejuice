# Responsive and browser compatibility refinement

Scope: preserve the updated Beetlejuice design, content, original artwork and game.

## Changes

- Continuous mobile-first navigation breakpoint, shared with JavaScript.
- Safe-area padding for notches/home indicators and unrestricted pinch zoom.
- Content-aware wrapping for curse steps, team cards, navigation and buttons.
- Shrinkable grid tracks for long game results and enlarged text, without hiding overflow.
- Original image dimensions reserved before loading; responsive 16:9 video wrappers.
- Scrollable, bounded reveal dialog with a short-landscape layout and `vh` fallback.
- Touch-device backgrounds use scrolling instead of fixed attachment.
- MediaQueryList.addListener fallback; unsupported native dialogs skip the animation rather than breaking the game.
- Missing fetch/AbortController/FormData leaves the existing native contact POST intact.
- Focus fallback for browsers that lack :focus-visible.

## Reproducible checks

`python tests/test_responsive.py --browser chromium` (also firefox or webkit)

Install the selected Playwright browser first. The existing UI regression workflow
runs this suite along with the original browser and offline tests. Reports and
screenshots are saved as workflow artifacts. The suite covers all six pages at
31 viewports from 280 to 3840 CSS pixels, portrait and landscape, 200% root text
scaling, custom text spacing, long names, complete/partial game states during
resizing, cancellation in short viewports, touch emulation, no JavaScript,
blocked fonts/storage, and simulated missing browser capabilities.

Local offline check: 986 assertions passed. Offline mode inlines original local
images and CSS, uses fallback fonts and mocks audio/storage. This is separate
from HTTP-served cross-browser verification; consult the actual workflow results.

## Limits

Browser-engine checks do not establish support for every historical release or
physical device. The 320px reflow case corresponds to a 1280px viewport at 400%
zoom; 200% text is tested by increasing the root font size, not by manipulating
a physical device or browser's zoom UI. Safe-area padding follows CSS env()
values but must ultimately be confirmed on physical notched devices.
Formspree responses and video frames are mocked. No messages are sent and no
claim is made about external delivery/playback or complete WCAG conformance.

## References

- WebKit safe areas: https://webkit.org/blog/7929/designing-websites-for-iphone-x/
- W3C reflow: https://www.w3.org/WAI/WCAG21/Understanding/reflow/
- Native dialog support: https://developer.mozilla.org/en-US/docs/Web/API/HTMLDialogElement/showModal
