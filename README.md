# THE DAILY DOSE — V1 website

**Status:** Design prototype only. All news/market/sports text is placeholder or evergreen, not a live feed. The calendar is **not** connected; no scheduling, sending, or background updates are configured.

## Run it now
Open `index.html` in a browser. The Portuguese quiz works. The checklist saves only in this browser using local storage.

## Free hosting (optional)
1. Make a free GitHub account/repository if you do not already have one. Upload `index.html` at the root of a public repository. **Do not upload real calendar details.**
2. On GitHub, select **Settings > Pages**, choose **Deploy from a branch**, `main`, root (`/`), and save.
3. GitHub gives you a website address after Pages is published. Public GitHub Pages sites and public repositories are accessible to others, so keep private data out.

Alternatively, deploy this static folder on a free static hosting service that allows personal use. Hosting availability/conditions can change.

## Future build phases
- V2: editorial design feedback and richer lessons/reviews.
- V3: reliable daily data feed with verified sources and date stamps; don't publish invented headlines.
- V4: private Apple Shortcuts export to a private endpoint/authenticated website. **Do not put iCloud calendar events into this public static site.**
- V5: scheduled morning publishing/notification only after approval.

## Personal data and limitations
No account, backend, analytics, API keys, or calendar data are included in this version. External Google Fonts are requested if online, with system font fallback. Opening `index.html` displays the current date but **does not** update the content.
