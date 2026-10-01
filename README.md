# Beetlejuice · Curse Generator

A Halloween hackathon website combining a playful curse generator with Beetlejuice-themed stories, imagery and sound.

**HTML · CSS · JavaScript**

[Visit the website](https://samobrienolinger.github.io/Beetlejuice-Beetlejuice-Beetlejuice/) · [Getting started](#getting-started) · [Repository guide](#repository-guide) · [Checks](#checks-and-review) · [Credits](#credits-and-reuse)

## What you can explore

- A personalised three-part curse generator.
- History, fun and contact pages.
- Audio effects and themed visual assets.

> **Project notes:** An unofficial fan project. Film imagery, branding, audio and other third-party material retain their respective ownership and attribution requirements.

## Getting started

Requires Git, a browser and a local HTTP server. Python 3 provides one without installing application packages.

```bash
git clone https://github.com/SamOBrienOlinger/Beetlejuice-Beetlejuice-Beetlejuice.git
cd Beetlejuice-Beetlejuice-Beetlejuice
python3 -m http.server 8000 --bind 127.0.0.1
```

Open [localhost:8000](http://localhost:8000). Serve the repository over HTTP so relative assets and page links resolve correctly.

## Repository guide

| Path | Purpose |
| --- | --- |
| [index.html](index.html) | Primary browser entry point |
| [assets/](assets/) | Project styles, scripts, data and imagery |
| [tests/test_ui.py](tests/test_ui.py) | Offline Chromium interaction and layout checks |
| [UI_UX_REFINEMENTS.md](UI_UX_REFINEMENTS.md) | Refinements, preserved features and verification limits |

## Checks and review

```bash
node --check assets/js/script.js
python tests/test_ui.py
```

The Python checks require Playwright and Chromium. They render local document fixtures without a server. Contact responses and other browser boundaries are mocked; no message is sent. External images, fonts, audio and videos are not loaded. See [verification limits](UI_UX_REFINEMENTS.md#verification-limits).

For a live review, follow the main user journey, check keyboard navigation and narrow-screen layouts with the original media loaded, and inspect the browser console for missing assets or failed requests. Verify real contact delivery separately.

## Deployment

A GitHub Pages site is configured for this repository. Its published URL is linked at the top of this README.

## Credits and reuse

Design decisions, original feature notes, historical testing evidence and detailed acknowledgements remain available in the preserved project record:

- [README.md · original project record](https://github.com/SamOBrienOlinger/Beetlejuice-Beetlejuice-Beetlejuice/blob/d382c7777419839d755a5c5e2a43f5721127d803/README.md)

Learning resources and starter material: [Code Institute](https://codeinstitute.net/).

No repository-level licence file is present in this snapshot. This README does not grant additional reuse permissions. Check with the relevant rights holders before reusing code, written content or assets.

## Support

Repository maintained in [Sam O’Brien-Olinger’s GitHub account](https://github.com/SamOBrienOlinger). For a problem or suggested improvement, [open an issue](https://github.com/SamOBrienOlinger/Beetlejuice-Beetlejuice-Beetlejuice/issues) with the affected page or command, steps to reproduce, and expected behaviour.

[Back to top](#beetlejuice--curse-generator)
