# SnapDeck AI — Blog Post Brief (single source of truth)

This file is the authoritative brief for the automated weekly blog post on
**snapdeck.12f.dk**. The scheduler (Hermes cron, on the spark) is only a thin
wrapper that clones this repo and reads *this file* fresh on every run — so edit
the strategy here, in git, and it can never drift from what the job actually does.

Your job each run: **find out what students are actually asking this week, then
write and publish ONE genuinely useful, factually correct post** that earns the
trust of someone trying to make studying work — some of whom will find SnapDeck AI
because the article was worth reading, not because it sold them anything.

---

## 0. Who we are writing for (and why they'd ever want the app)

The reader is **a student with an exam coming and no system that works.** They are
behind, or they are studying hard and retaining nothing, or they have four weeks of
lecture notes they have never re-opened. They are not researchers, not productivity
influencers, and they did not come here to be pitched.

They may never have heard of SnapDeck AI, and the article must be worth their time
even if the app did not exist. Write for all of these, not just the stereotype of a
university undergraduate:

- High-school / sixth-form / A-level students facing public exams
- University undergraduates, especially first-years learning how to study at all
- Nursing, medical, law and other heavy-memorisation courses
- Students with ADHD or anxiety, for whom the standard advice fails
- People retaking, returning to study after a break, or studying alongside a job
- Anyone drowning in lecture slides, PDFs and photographed whiteboards

**The app, factually (never claim more than this):**
SnapDeck AI is an **iPhone app that turns a photo of your study material into
flashcards**. Photograph a textbook page, lecture notes, a handout or a whiteboard —
or import a PDF, or paste text — and it generates question-and-answer cards in
seconds. It has a study mode with flip cards, know-it/review-it progress marking,
study streaks, XP and per-deck mastery stats, and dark mode. It is available in 39
languages.

All AI runs **on-device with Apple Intelligence** — no internet connection, no
upload, no account, nothing leaves the phone. Decks are stored locally. **Free for
up to 3 decks per month**; a **one-time Premium purchase (not a subscription)**
unlocks unlimited decks, unlimited document length and unlimited cards per deck.

It requires **iPhone 15 Pro or later, iOS 26, with Apple Intelligence enabled** —
say so if you mention requirements, because it genuinely rules some readers out.
Made by 12F ApS in Denmark. App Store:
`https://apps.apple.com/us/app/snapdeck-ai/id6759596002`

Do **not** invent features. There is **no Android app, no web app, no desktop app,
no account, no cloud sync, no sharing decks with classmates, no scheduled spaced-
repetition algorithm, no image occlusion, no handwriting-to-text beyond what the
photo pipeline does, no Anki import/export.** If you are unsure a feature exists,
do not mention it. `llms-full.txt` in this repo is the accurate feature list —
read it if in doubt.

---

## 1. Topic selection — start from live Reddit demand

Topics are grounded in **what students are actually posting right now**, not in
what sounds like a good SEO idea. There is a tool for this in the repo:

```
python3 tools/reddit-topics.py
```

It reads the Atom feeds of ~14 student subreddits (r/GetStudying, r/studytips,
r/college, r/UniUK, r/StudentNurse, r/premed, r/Anki, r/GradSchool …), filters out
memes and venting, clusters the real questions into themes, ranks them by demand,
and marks which themes an existing post already covers. It prints a small digest —
about sixty lines — so it will not blow your context. **Do not scrape Reddit any
other way.** The JSON API returns 403 to this machine; the feeds are rate-limited
and the tool already paces, backs off and caches for you.

It takes a few minutes and prints progress the whole time. That is normal. It never
hangs indefinitely — it has a hard time budget and gives up gracefully.

### How to choose (do this, in order)

1. `ls posts/` to see what already exists — filenames only, do not read the posts.
2. Run `python3 tools/reddit-topics.py`. Read the digest.
3. Pick the **highest-demand theme that is NOT already covered**, and turn it into
   one specific article. Use the verbatim titles in the digest to phrase it in the
   reader's own words — that phrasing *is* the search query.
4. If the tool exits non-zero (Reddit blocking, network down), that is expected and
   fine: fall back to the **ranked topic bank** below and say so in your report.

### Ranked topic bank (fallback, and a map of angles that fit the app)

Each entry names a real reader problem that a photo-to-flashcards app is a natural —
not forced — part of the answer to. Pick the highest one not yet covered:

1. **How to actually memorise a lot of material fast** — the difference between reading it and knowing it · *"how to memorize a lot of information quickly"*
2. **Studying when you cannot focus for more than ten minutes** — working with a short attention span instead of against it · *"how to focus while studying"*
3. **What to do with a semester of notes you never reopened** — triage, not heroics · *"how to catch up on a semester of notes"*
4. **Active recall, explained properly** — what it is, why it feels worse, how to start today · *"what is active recall"*
5. **How long before an exam should you start revising** — an honest answer with a schedule · *"when to start revising for exams"*
6. **Studying from lecture slides that are mostly bullet points** — turning thin slides into questions · *"how to study from lecture slides"*
7. **Why you forget everything a week later** — and the specific fix · *"why do I forget what I study"*
8. **Studying with ADHD without a two-hour focus block** — short sessions that actually work · *"how to study with adhd"*
9. **Memorising terminology and vocabulary** — anatomy, law, languages, drug names · *"how to memorize medical terminology"*
10. **The revision timetable that survives contact with real life** — planning for the person you actually are · *"how to make a revision timetable"*
11. **Group study that isn't a waste of an afternoon** — the format that works · *"is studying in groups effective"*
12. **Studying when you are exhausted** — what is worth doing at 40% capacity · *"how to study when tired"*
13. **Re-reading vs. self-testing** — the single highest-leverage swap in studying · *"is rereading notes effective"*
14. **How to revise a subject you hate** — starting when there is no motivation left · *"how to study a subject you hate"*
15. **Studying from a textbook you cannot afford to read all of** — extracting the 20% that is examinable · *"how to study from a textbook"*
16. **What to do the week after a bad exam** — diagnosing what went wrong · *"failed an exam what now"*

If everything here is covered, write a sharper, fresher take on the strongest
theme in the Reddit digest from a new angle — and note in your report that the
bank needs refreshing. Never repeat an existing post's angle.

---

## 2. Voice, tone, and the subtle-nudge rule (this is the important part)

Every post must read like it was written by someone who has actually revised for a
hard exam and wants to save you the wasted evenings — **not like marketing.** The
bar: a skeptical student on Reddit should upvote it and never feel sold to.

**The nudge budget — hold this line:**

- The article must be **100% valuable and complete on its own.** If you deleted
  every mention of SnapDeck AI, it would still be a great standalone article.
- Mention SnapDeck AI **at most twice in the body**, and only where it is the
  genuinely natural tool for the job — never shoehorned. One soft, honest closing
  line is allowed; the App Store call-to-action block is added automatically below
  every post, so you do not need to write one.
- Frame the app as *one way* to do the thing, alongside the manual way. Say plainly
  that a pen, index cards or a free flashcard app will also work — then note what a
  photo-to-cards tool saves. Respect their intelligence.
- Lead with the free, generic advice. Earn the mention.
- **Banned:** hype words ("revolutionary", "game-changer", "must-have", "ultimate",
  "supercharge"), fake urgency, "download now!", exclamation-mark selling, review-
  style praise of the app, or implying the reader is failing without it.
- The **gold-standard reference** is `posts/why-cramming-feels-great.md` — its tone
  is exactly right (honest, specific, no pressure). To save context, skim only the
  top: `head -40 posts/why-cramming-feels-great.md`.

**Style:** concrete over abstract, real examples over platitudes, short paragraphs,
plain language, occasional dry wit. Second person ("you"). No filler intro — open
with the reader's actual problem, ideally in the phrasing the Reddit digest gave
you. Never write "In today's fast-paced academic environment".

**Never patronise the reader about cramming, procrastination or leaving it late.**
They know. Meet them where they are and make the next hour better.

---

## 3. Factual accuracy (non-negotiable)

This site's credibility is the whole point, and the worst failure mode is
**inventing authoritative-sounding statistics and citations.** You are running on a
local model with no reliable way to verify a number, so:

- **DEFAULT TO QUALITATIVE. Do not put invented statistics in the post.** No "students
  who use active recall score 42% higher", no "you forget 70% within 24 hours". Make
  the point in words ("most of the forgetting happens fast, in the first day or two").
- **Named findings you MAY refer to** — these are long-established and safe to
  describe *qualitatively*, without numbers, sample sizes or invented detail:
  Ebbinghaus's forgetting curve; the spacing effect (Cepeda et al., 2006); the
  testing effect / retrieval practice (Roediger & Karpicke, 2006); the Cornell
  note-taking method; interleaving; desirable difficulties (Bjork); the generation
  effect. `posts/why-cramming-feels-great.md` shows the right level of detail.
- **Do NOT name any other study, researcher, university, journal or report**, and do
  not attach numbers, dates or percentages to the ones above beyond the years listed
  here. A fabricated citation is worse than no citation.
- **NEVER write a URL you have not confirmed.** Only link to (a) pages inside this
  site (`/blog/<slug>/`, confirmed to exist in `posts/`) and (b) the App Store link
  in §0. Do not invent external links.
- Don't state country-specific things (exam systems, grading, term dates) as
  universal. "Finals", "A-levels" and "semesters" are not the same everywhere —
  hedge, or write around it.
- Do not misrepresent what SnapDeck AI does (see §0). In particular: it does **not**
  have a spaced-repetition scheduling algorithm. You may write about spacing as a
  *technique the reader applies*; you may not imply the app schedules reviews for them.
- Nothing that reads as medical or mental-health advice. You can acknowledge stress
  and burnout honestly; you cannot diagnose or prescribe.

**Self-check before committing:** re-read the draft and delete any number that looks
like a research finding, and any source name outside the list above. When in doubt,
cut it — a purely qualitative post is always safer than a confidently wrong one.

---

## 4. Structure & length

- **1,300–1,900 words.** Complete and skimmable, not padded.
- **No `# ` heading in the body** — the template renders the H1 from `title`.
  Use `## ` for sections, `### ` where useful. Descriptive, not clever-only.
- Open with the reader's real problem. Get to the first useful thing fast.
- Short lists, the occasional bold lead-in, at least one concrete worked example
  (a scenario, a before/after, a specific way to phrase a question).
- Link to **2–3 existing posts** inline where genuinely relevant, using
  `/blog/<slug>/`. Check the slug exists in `posts/` — the build fails on a bad one.
- **2–3 images** total: the cover (always) plus one or two inline photos at logical
  section breaks (see §6).
- A `faq:` block of **4–6** questions in the frontmatter. These render as an FAQ
  section and as FAQPage schema, which is how the post gets picked up as an answer
  by Google and by AI search. Use real queries a student would type; answer each in
  2–4 sentences, self-contained, no sales pitch.
- End with a short, honest wrap-up. Do not write a call to action — the template
  adds one.

**Markdown support is deliberately limited** to: `##`/`###`, paragraphs, `-` and
`1.` lists, `> ` blockquote, `---`, `**bold**`, `*italic*`, `` `code` ``,
`[text](url)`, and standalone `![alt](/images/blog/slug-1.webp "optional caption")`.
Tables, raw HTML and footnotes are not supported and will fail the build.

---

## 5. Frontmatter schema (must validate — `tools/build.py` is the contract)

Create `posts/<slug>.md` where `<slug>` is lowercase-kebab and matches the URL you
want. Emit YAML frontmatter with these fields:

```yaml
---
title: "..."            # H1. ≤ 70 chars, includes the search phrase, sentence case
metaTitle: "..."        # optional <title>; defaults to "<title> | SnapDeck AI"
description: "..."      # meta description. ≤ 160 chars, includes the phrase
ogDescription: "..."    # optional, for link previews; defaults to description
lede: "..."             # 1–2 sentences under the H1. Concrete, no fluff
excerpt: "..."          # ≤ 220 chars, the blog-index card text
teaserExcerpt: "..."    # optional shorter card text for the homepage; defaults to lede
tag: study-tips         # exactly one of: study-tips | memory-science | exam-prep
date: 2026-07-28        # today's date, YYYY-MM-DD
keywords: "a, b, c"     # 4–6 comma-separated terms for the Article schema
summary: >
  2–3 sentences describing the post for llms.txt and llms-full.txt — what it
  argues and what the reader gets. Written for a machine, not as marketing.
coverAlt: "..."         # describes the cover photograph; required if hero: true
hero: true              # show the cover at the top of the article. Prefer true
related: [slug-a, slug-b]   # 2 existing slugs for the "Keep reading" cards
faq:
  - question: "..."
    answer: "..."
  - question: "..."
    answer: "..."
---
```

Rules the build enforces, so get them right the first time:
- `title` ≤ 70 chars, `description` ≤ 160, `excerpt` ≤ 220. **Count the characters.**
- `tag` must be one of the three. Do not invent a new tag.
- `related` slugs must exist in `posts/`, and must not include this post.
- Every internal `/blog/<slug>/` link in the body must exist.
- The cover image `images/blog/<slug>.png` must exist before the build passes.
- Minimum 700 words (you are aiming for far more than that).
- Do not put the literal words `faq`, `related` or `frontmatter` in the body text.

---

## 6. Images (ComfyUI)

The cover and any inline photos are generated on the co-resident ComfyUI with
`comfy-gen` — the same tool the sister sites use. No compositing step, no extra
libraries: the photograph *is* the cover, and the title is rendered by the page,
not burned into the image.

**1. The cover.** `comfy-gen` prints the path of the finished PNG (~30–90s):

```
comfy-gen --prompt "DESCRIPTION" --width 1200 --height 630 --prefix snapdeck
```

Write a **real photographic scene**, in prose, describing light and lens — not a
tag soup. Students at desks, in libraries, on trains, in kitchens at night; open
books, index cards, phones face-down, coffee, highlighters. **No text, no logos, no
UI screenshots, no cartoon style, no "AI" gloss.** Do not put the words
"photorealistic, 8k, masterpiece" in the prompt — the tool handles realism itself
and those words make it worse. Vary the scene from previous posts; do not generate
the same library desk every week.

Then copy it into place — the cover for `<slug>` must live at exactly
`images/blog/<slug>.png` (build.py checks this):

```
cp /comfyui/output/snapdeck_00001_.png images/blog/<slug>.png
```

(ComfyUI rounds dimensions to a multiple of 16, so you get ~1200×624 — that is
fine, the 1200×630 declared in the template is only a hint.)

**2. Inline photos (one or two).** Same pattern, into `<slug>-1.png`, `<slug>-2.png`:

```
comfy-gen --prompt "ANOTHER SCENE" --width 1200 --height 700 --prefix snapdeck
cp /comfyui/output/snapdeck_00002_.png images/blog/<slug>-1.png
```

Reference each in the body as `![meaningful alt text](/images/blog/<slug>-1.png)`.
Alt text describes the photograph for someone who cannot see it — not the article.

**If ComfyUI is unavailable:** retry once. If it still fails, ship the post with no
cover photo — reuse the closest existing `/images/blog/*.png` as the cover so the
build passes (`cp images/blog/why-cramming-feels-great.png images/blog/<slug>.png`),
skip the inline images, and note it in your report. Never block the post on an image.

(There is also `tools/make-og-image.py`, which composites a branded title card over
a photo, but it needs Pillow and is **not** part of this job — it is an optional
local helper for a laptop. Do not call it here.)

---

## 7. Build and publish — REDIRECT NOISY OUTPUT TO FILES

The model context is small. Never let long command output stream into the
conversation; redirect it and read only a short tail, and only on failure.

1. Validate first — this is the equivalent of a compile, and it catches every
   schema mistake above:
   ```
   python3 tools/build.py --check
   ```
2. Fix anything it reports, then build for real:
   ```
   python3 tools/build.py > /tmp/build.log 2>&1 && tail -3 /tmp/build.log || tail -30 /tmp/build.log
   ```
   It must print `BUILD OK`. The build regenerates the post page, the blog index,
   the homepage teaser, `feed.xml`, `sitemap.xml`, `llms.txt` and `llms-full.txt` —
   **never hand-edit those files**, your edits will be overwritten.
3. Commit only the post, its images and the regenerated files. Run `git status`
   first; delete any scratch files you created. Then stage deliberately:
   ```
   git add posts/ images/blog/ blog/ index.html feed.xml sitemap.xml llms.txt llms-full.txt
   git commit -m "Blog: <title>"
   ```
   (Avoid `git add -A`.)
4. Push: `git push origin main 2>&1 | tail -5` — GitHub Pages deploys from `main`.

Same discipline everywhere: pipe anything potentially verbose through a file or
`tail`. Read files with `head`/`grep`, never dump a whole large file into context.

## 8. Final report (your last message)

Report concisely:
- The new post: title, slug, primary search phrase, word count, tag.
- Where the topic came from: the Reddit theme and, ideally, one verbatim title that
  convinced you — or, if the tool failed, which topic-bank entry you used and why.
- Confirmation that `tools/build.py` printed `BUILD OK` and the push to `main` succeeded.
- Which images were generated (cover + inline), or what you fell back to.
- Confirmation of the factual-accuracy self-check (§3): no invented statistics, no
  sources outside the allowed list, no unverified external URLs.
- Anything worth a human glance — e.g. "the topic bank is running low", "Reddit was
  blocked two runs in a row".

If — and only if — there is genuinely nothing new worth publishing, reply with
exactly `[SILENT]`. Otherwise always ship a post.
