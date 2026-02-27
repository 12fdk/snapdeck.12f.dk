# SnapDeck AI Landing Page

Landing page for the SnapDeck AI iOS app, deployed via GitHub Pages.

## Project Structure

- `index.html` — Main landing page
- `privacy-policy.html` — Privacy policy
- `404.html` — Custom 404 error page
- `css/style.css` — All styles (CSS custom properties design system)
- `js/main.js` — Scroll animations, smooth scroll, mobile nav
- `images/` — App icon, favicons, OG image, screenshots
- `CNAME` — GitHub Pages custom domain (snapdeck.12f.dk)
- `robots.txt` / `sitemap.xml` — SEO

## Brand Colors

- **Indigo**: #4F46E5 (primary)
- **Purple**: #7C3AED (secondary)
- **Gold**: #FBBF24 (accent)
- Gradient: Indigo → Purple

## Development

No build tools needed. Serve locally:
```bash
python3 -m http.server 8000
```

## Deployment

Push to `main` branch → GitHub Pages auto-deploys.

## Key Notes

- Static site — no build tools, no frameworks, no dependencies
- Screenshots from SnapDeck app at `/Users/robert/Git/SnapDeck/fastlane/screenshots/`
- App icon generated from brand gradient (Pillow script in project history)
- Analytics: Umami (privacy-focused) at umami.robert-jensen.dk
- App Store: https://apps.apple.com/us/app/snapdeck-ai/id6759596002
