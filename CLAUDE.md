# SnapDeck AI Landing Page

Landing page + blog for the SnapDeck AI iOS app, deployed via GitHub Pages.

## Project Structure

- `index.html` — Main landing page
- `blog/index.html` — Blog index (card grid)
- `blog/<slug>/index.html` — One folder per post, hand-written HTML
- `privacy-policy.html` — Privacy policy
- `404.html` — Custom 404 error page
- `css/style.css` — All styles (CSS custom properties design system, light + dark)
- `js/main.js` — Scroll reveals, sticky-header state, mobile nav
- `images/` — App icon, favicons, OG image, `screenshots/<locale>/`, `blog/<slug>.png|webp`
- `tools/make-og-image.py` — Generates a post's OG/featured image (gradient + title). Not a build step.
- `feed.xml` — RSS feed for the blog (hand-maintained)
- `CNAME` — GitHub Pages custom domain (snapdeck.12f.dk)
- `robots.txt` / `sitemap.xml` / `llms.txt` / `llms-full.txt` — SEO + AI crawlers

## Brand Colors

- **Indigo**: #4F46E5 (primary)
- **Purple**: #7C3AED (secondary)
- **Gold**: #FBBF24 (accent — highlighter marker, tag chips, premium CTA)
- Gradient: Indigo → Purple

## Development

No build tools needed. Serve locally:
```bash
python3 -m http.server 8000
```

Use absolute paths (`/css/style.css`, `/images/...`) so blog subfolders resolve.

## Adding a blog post

1. `python3 tools/make-og-image.py <slug> "<Title>" "<tag>"` — writes `images/blog/<slug>.png` and `.webp`
2. Copy an existing `blog/<slug>/index.html` as the template; update meta, Article + BreadcrumbList JSON-LD, and the "Keep reading" cards
3. Add the post to `blog/index.html`, the homepage blog teaser, `feed.xml`, `sitemap.xml`, `llms.txt` and `llms-full.txt`

Tags in use: `study-tips`, `memory-science`, `exam-prep`.

## Deployment

Push to `main` branch → GitHub Pages auto-deploys.

## Key Notes

- Static site — no build tools, no frameworks, no dependencies
- Screenshots come from `/Users/robert/Git/SnapDeck/fastlane/screenshots/raw/<locale>/`, resized to 640px WebP in `images/screenshots/<locale>/` (only `en-US` is wired up; other locales exist upstream)
- Analytics: Umami (privacy-focused) at umami.robert-jensen.dk — the tag belongs on every page
- App Store: https://apps.apple.com/us/app/snapdeck-ai/id6759596002
- The homepage "Who it's for" section uses personas, **not** testimonials — the app has no public reviews yet. Don't invent quotes; swap in real ones when they exist.
