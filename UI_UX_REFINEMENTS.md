# UI and UX refinements

## What stays familiar

The original purple, green, black and white identity, Amatic SC and Neucha fonts,
moon-and-bats background, logo, welcome GIF, spinning head, character image,
tattoo artwork, history article, three-part curse wording, six team members and
existing contact service are retained. No original image, audio or credits file
has been replaced or deleted. The five existing pages keep their URLs.

The supporting thank-you page is new. It only claims successful delivery after
a confirmed Formspree response; opening that URL directly does not claim a
message was sent.

## Changes

- Shared responsive navigation with a consistent set of links, current-page
  indication, larger targets, keyboard focus, Escape handling and a no-JavaScript
  fallback. The logo still links home.
- More legible green panels, balanced widths, responsive images and trailers,
  properly wrapping content, clearer button states and a compact credited footer.
- Real disabled game buttons, trimmed name validation, three-part progress,
  safe text output, duplicate-click protection, a cancellable spinning-head
  reveal, replay without reloading, and copying with a permission-denied fallback.
- Original phrase sets and the no-repeated-meaningful-words rule are retained.
- Opt-in-by-interaction sound effects use the existing audio file. Sound can be
  switched off. Reduced-motion preferences are respected, with an animation
  control and a still-frame alternative for the original GIF.
- Contact labels, appropriate input types, autocomplete, inline validation,
  sending state, error recovery without losing a message, and a genuine
  confirmation path. The existing native POST action remains usable without JS.
- Descriptive video titles, deferred video loading, direct YouTube fallback
  links, a full-size tattoo-image link, and consistent external-link notices.
- Removed unused Bootstrap/Popper/jQuery and icon-library downloads. Responsive
  layout and navigation now use the project's own CSS and JavaScript. The two
  existing Google Fonts remain the only external style dependency.

## Checks run

`node --check assets/js/script.js`

`python tests/test_ui.py`

The offline Chromium suite passed 271 assertions, including six pages at
320, 375, 390, 768, 1024 and 1440 CSS-pixel widths, mobile-menu behavior,
game gating, cancel/reveal/replay, safe names, repeated phrase generation,
copy success/failure, and simulated contact errors/success. No uncaught
JavaScript exceptions occurred in those checks.

Install Python Playwright and its Chromium browser to run the test script.
It also accepts a `CHROMIUM_EXECUTABLE` environment variable for an existing
Chromium executable. Tests render the local files directly, without a server.

### Verification limits

Network access and browser navigation were restricted in the implementation
environment. The suite renders offline document fixtures. Storage, clipboard,
Formspree responses and the final navigation boundary are mocked. External
artwork, audio, fonts and videos are not loaded. No contact message was sent.
Screenshots were used only to inspect layout with fallback fonts and missing
media. These checks do not establish final live artwork rendering, media
playback, Formspree delivery, Safari/Firefox behavior or complete accessibility
conformance. A live check with the original assets is still needed.

## Content intentionally not changed

The existing displayed contact phone number and email address have not been
verified. Confirm them with the project owner before treating them as contact
routes. Historical article claims and third-party video availability have not
been re-verified as part of this UI/UX-only update.
