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

- Shared responsive navigation with consistent links, current-page indication,
  larger targets, keyboard focus, Escape handling and a no-JavaScript fallback.
- More legible green panels, balanced widths, responsive images and trailers,
  properly wrapping content, clearer button states and a compact credited footer.
- Real disabled game buttons, trimmed name validation, three-part progress,
  safe text output, duplicate-click protection, a cancellable spinning-head
  reveal, replay without reloading, and copying with a permission-denied fallback.
- Original phrase sets and the no-repeated-meaningful-words rule retained.
- Existing sound effects play only after interaction and can be switched off.
  Reduced-motion preferences and a persistent animation control are supported.
- Contact labels, appropriate input types, autocomplete, inline validation,
  sending state and recovery without losing a message. The existing native
  Formspree POST action remains usable without JavaScript.
- Descriptive video titles, lazy video loading, direct YouTube fallback links,
  a full-size tattoo-image link and external-link notices.
- Removed unused Bootstrap, Popper, jQuery and icon-library downloads. Layout
  and navigation now use the project's own CSS and JavaScript.

## Verification

Run syntax and offline checks:

```sh
node --check assets/js/script.js
python tests/test_ui.py
```

Run the HTTP-served site checks with local media:

```sh
python tests/test_browser.py --browser chromium
python tests/test_browser.py --browser firefox
python tests/test_browser.py --browser webkit
```

Install Python Playwright and the relevant browsers first. GitHub Actions
runs these checks and attaches JSON results and screenshots to each run.
The offline suite mocks storage, clipboard, network and navigation boundaries.
The HTTP suite uses the actual HTML, CSS, JavaScript and local artwork.
Contact responses and third-party video frames are mocked: no message is sent.
A WebKit engine check is not a physical iPhone or Safari-device test.
A passing run does not certify all-browser behavior or full accessibility
conformance. Consult the recorded results rather than assuming tests passed.

## Content intentionally not changed

The existing displayed phone number and email address remain unverified.
Confirm them with the project owner before relying on them as contact routes.
Historical article claims and third-party video availability were not changed
or fact-checked as part of this UI/UX-only update. Real Formspree delivery must
be verified separately by the owner.
