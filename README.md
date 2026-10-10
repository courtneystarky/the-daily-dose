# The Daily Dose — morning edition

A public, free static website with publisher-linked news and rotating daily learning.

## Daily publishing
GitHub Actions fetches public BBC News, BBC Sport and ESPN RSS headlines and deploys a fresh content.json plus the website. Runs begin at 5:17 and 5:47 AM America/New_York, with a 6:17 AM backup. Target reading time: 6 AM Eastern, beginning October 10, 2026. GitHub can delay scheduled jobs; this is not a guaranteed delivery service. Manual runs are available in Actions > The Daily Dose morning edition > Run workflow.

Headlines keep their source wording, attribution, links and publication dates. Entries older than 3 days are omitted. Missing feeds display unavailable; if every feed fails, publication stops and the previous deployment remains. The page shows the actual edition date and a pending notice when it is stale.

Portuguese lessons rotate through a 14-day foundations/review cycle. Checklist prompts, career exercises, reflections and sourced trivia rotate weekly. Market quote and official fixture links open at their sources; numeric quotes and personal fantasy data are not imported.

## Privacy
No iCloud calendar connection, personal calendar events, private credentials, tracking, paid AI API or subscriptions. Checklist selections stay in browser-local storage. Audio uses the device's speech support when available.

## Files
- index.html: original visual design and page structure
- daily.js: edition rendering, lessons and local checklist
- update_daily.py: fetch and validate public RSS feeds
- content.json: seed edition (workflow replaces this in deployment artifacts)
- .github/workflows/daily-dose.yml: cloud schedule and Pages deployment

The cloud build publishes only index.html, daily.js and content.json. It does not need your Mac to be awake.
