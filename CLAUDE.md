# SnapDeck AI Landing Page

Landing page + blog for the SnapDeck AI iOS app, deployed via GitHub Pages.

## Project Structure

- `index.html` — Main landing page
- `posts/<slug>.md` — **Blog source of truth**: frontmatter + markdown, one file per post
- `prompt.md` — The brief the weekly automated blog job follows (see below)
- `blog/index.html`, `blog/<slug>/index.html` — **Generated** from `posts/` by `tools/build.py`
- `privacy-policy.html` — Privacy policy
- `404.html` — Custom 404 error page
- `css/style.css` — All styles (CSS custom properties design system, light + dark)
- `js/main.js` — Scroll reveals, sticky-header state, mobile nav
- `images/` — App icon, favicons, OG image, `screenshots/<locale>/`, `blog/<slug>.png|webp`
- `tools/build.py` — Renders the blog and every file that lists posts
- `tools/reddit-topics.py` — What students are actually asking, ranked (topic research)
- `tools/make-og-image.py` — Optional local helper: branded title-card cover (needs Pillow; not used by the job)
- `tools/templates/post.html` — The post page template
- `feed.xml` — RSS feed for the blog (generated)
- `CNAME` — GitHub Pages custom domain (snapdeck.12f.dk)
- `robots.txt` / `sitemap.xml` / `llms.txt` / `llms-full.txt` — SEO + AI crawlers (blog parts generated)

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

## Adding a blog post — `posts/*.md` is the source of truth

The blog is **generated**. Write markdown in `posts/<slug>.md` and run the build;
never hand-edit `blog/<slug>/index.html`, it will be overwritten.

```bash
python3 tools/build.py --check   # validate only (schema, links, images, lengths)
python3 tools/build.py           # write everything
```

`tools/build.py` renders each post page and rewrites every derived file: the blog
index grid, the homepage teaser, `feed.xml`, the blog URLs in `sitemap.xml`, and
the `## Blog` sections of `llms.txt` and `llms-full.txt`. Generated regions inside
hand-written files are fenced with `BLOG:*:START` / `BLOG:*:END` markers — leave
them in place. The frontmatter schema is documented in `prompt.md` §5 and enforced
by the build.

Images: the cover for `<slug>` lives at `images/blog/<slug>.png`, inline photos at
`images/blog/<slug>-N.png`. The weekly job generates them on the spark's ComfyUI
with `comfy-gen` (a plain photograph — the title is rendered by the page, not
burned in) and copies them into place. See `prompt.md` §6.

`tools/make-og-image.py` is an **optional local helper** that composites a branded
title card (photo + scrim + title + tag chip, or a brand-gradient fallback) — it
needs Pillow and is **not** used by the automated job. Use it by hand if you want a
title-on-cover OG image:

```bash
python3 tools/make-og-image.py cover <slug> "<Title>" "<tag>" --bg photo.png
python3 tools/make-og-image.py cover <slug> "<Title>" "<tag>"      # gradient, no photo
python3 tools/make-og-image.py inline <slug> 1 photo.png
```

Tags in use: `study-tips`, `memory-science`, `exam-prep`.

## The weekly post writes itself

A Hermes cron job on the spark (`SnapDeck Blog Post`, Tuesdays 09:00
Europe/Copenhagen) clones this repo and publishes one post a week, generating its
visuals on the co-resident ComfyUI. **`prompt.md` is the brief it follows** —
audience, product facts, topic selection, tone and the nudge budget, factual-
accuracy rules, schema, images, publishing. The cron prompt is a thin wrapper that
only says "read prompt.md and follow it", so **change the strategy by editing
`prompt.md` here, in git** — never by editing the job. Sister setups: the same
pattern runs home-stories.12f.dk, event-stories.12f.dk and meugrana.12f.dk.

Topics come from live reader demand rather than invention:

```bash
python3 tools/reddit-topics.py          # ranked digest of what students are asking
python3 tools/reddit-topics.py --json
```

It reads ~14 student subreddits over Reddit's Atom feeds (the JSON API 403s from
both a datacenter and a home IP), filters out memes and venting, clusters the real
questions into themes, and marks the themes an existing post already covers.
Reddit rate-limits it hard, so it paces requests, backs off on 429, caches to
`.cache/` for a day and gives up gracefully — a failed scrape is expected, and
`prompt.md` falls back to a ranked topic bank.

## Deployment

Push to `main` branch → GitHub Pages auto-deploys.

## Key Notes

- Static site — no build tools, no frameworks, no dependencies
- Screenshots come from `/Users/robert/Git/SnapDeck/fastlane/screenshots/raw/<locale>/`, resized to 640px WebP in `images/screenshots/<locale>/` (only `en-US` is wired up; other locales exist upstream)
- Analytics: Umami (privacy-focused) at umami.robert-jensen.dk — the tag belongs on every page
- App Store: https://apps.apple.com/us/app/snapdeck-ai/id6759596002
- The homepage "Who it's for" section uses personas, **not** testimonials — the app has no public reviews yet. Don't invent quotes; swap in real ones when they exist.
