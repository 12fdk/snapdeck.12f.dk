# SnapDeck AI — Marketing Plan (living doc)

Owner: Robert · Maintained by: Hermes (social pipeline agent) · Last updated: 2026-10-28 (built Nov 2 #3 carousel snapdeck-nov2-3, post 6ae204c5a80dd396a885, scheduled 2026-11-05T17:00Z; §7 review not due — no published post in the 7–13 day window)

## 1. What this is & how it's updated

- Hermes owns this file and runs every step in it. Robert reviews it and owns
  the decisions marked *Robert* in §9.
- Pipeline (Appwrite db `marketing`, app slug `snapdeck`, on app.12f.dk):
  - Nightly job (`snapdeck-social-content`, shared `social-post` template,
    channel platform, spark#140): builds the next due §6 row — media rendered on
    the spark (`comfy-gen`, `motion-render`), created with `marketing-post` as
    `status=ready` at the time it picks (Hermes owns the schedule, marketing#97);
    `publish-social` publishes it then.
  - Before it picks a row, the job removes §6 plan rows whose post is published
    (`plan_prune.py`, spark#138). History lives in §8 and in Appwrite, not in §6.
  - Function `publish-social` (every 15 min) publishes to IG and FB; enforces a
    20h minimum gap between feed posts of the app.
  - Function `collect-metrics` (every 2h) writes IG/FB engagement into the post docs.
  - Function `optimize-guidelines` (monthly) — **dormant**.
- The nightly job also runs the §7 review and appends rows to §8.
- This file is separate from `prompt.md` (the weekly blog brief). The blog and
  the social posts share the product facts; nothing else.
- Editing rules for this file:
  - Append-only to §8: never delete or rewrite past log rows.
  - Plan changes go in §6, plus a §8 row that says why.
  - §3 and §4 change only on Robert's say-so.
  - Update the `Last updated` line on every edit.
  - Never put secrets, API keys or tokens in this file.

## 2. Product & funnel

- Product (LIVE iPhone app; on the App Store since 2026-02-27, current version
  1.2.2 from 2026-09-30, free — App Store lookup 2026-10-15): turns a photo of
  study material into question-and-answer flashcards with on-device AI. Input:
  photos of textbook pages, lecture notes, handouts, whiteboards and projector
  slides; PDF import; typed or pasted text. Study mode: flip cards, mark "Know
  it" or "Review", cards you miss come back, percent mastered per deck and per
  week, one deck per subject, dark mode. Edit any generated card. All AI runs
  on the iPhone with Apple Intelligence: works offline (airplane mode), no
  account, nothing uploaded. App in 39 languages. Free: 3 new decks every
  month; Premium is a one-time purchase (no subscription) for unlimited decks,
  document length and cards per deck. Sources: homepage, `llms.txt`,
  `llms-full.txt` (live = repo, read 2026-10-15). Feature wording for posts:
  the §5 claim sheet.
- Requirements (site wording): "iPhone 15 Pro or later, running iOS 26" with
  Apple Intelligence enabled. It rules some readers out, so captions say it
  (§3). The App Store lists a lower minimum iOS — see §9.
- App Store id6759596002:
  `https://apps.apple.com/us/app/snapdeck-ai/id6759596002`. 0 ratings
  (2026-10-15), so posts never mention ratings or reviews.
- Instagram: `@snapdeckai_app` (app record).
- Funnel today: profile bio → (link not confirmed, §9) → landing page
  `https://snapdeck.12f.dk/` → App Store tap (Umami event `appstore-click`,
  property `placement` = `nav` / `cta` / `footer`) → App Store.
- There is **no `/go/?src=` hop** on this site yet, so social traffic shows only
  as referrers (instagram.com, l.instagram.com, facebook.com, m.facebook.com,
  lm.facebook.com) in Umami site `c00b28ce-d663-4166-8b80-6260f0f30d6f`.
  Funnel report: `python3 /opt/data/scripts/social_funnel_report.py --app snapdeck`.
- Downloads are counted in App Store Connect, not Umami. Numbers come from the
  `app-store` skill (Appwrite `analytics`), never from a new ASC pull.

## 3. Content rules

- Text-slide colours: background #3730a3 · text #ffffff · accent #fbbf24
  (carousel text slides; `marketing-post --colors-from` reads this line, so
  keep its format and keep it the only line of its kind in this file. The
  site's own tokens: `--indigo-dark`, white, `--gold` — the gold of the
  highlighter marker on the homepage. Contrast: text 9.9:1, accent 6.0:1 on
  the background. Set 2026-10-15, spark#140.)
- **The SnapDeck look — "desk level, one gold mark".** Every post must look
  like SnapDeck and like no other 12F app:
  - The study material is the hero: pages, card stacks, whiteboards, folders,
    notebooks. Camera at desk height or straight overhead, 35–50 mm feel,
    shallow depth of field.
  - **One gold-yellow element in every photo**: a highlighter, sticky notes, a
    pencil, a lamp glow, a mug, a safety line. It echoes the gold marker on
    the site and ties the feed together.
  - **Indigo in the shadows**: a blue-hour window, a violet dusk, a cool
    fluorescent fill against the warm gold. Do not default to the app
    record's cream-and-amber flat-lay; it is one option, not the house look.
  - Real student places, rotated: dorm desks and floors, library carrels and
    basements, lecture halls after class, seminar rooms, campus cafés, night
    buses, trains, planes, labs, break rooms, a parent's kitchen table.
  - Light follows the academic year: golden autumn (Oct), early dark and blue
    hour (Nov), 1 a.m. lamp pools and first snow (finals, Dec), crisp white
    winter mornings (new semester, Jan), grey-lilac (Feb).
- Real-looking photography and footage only (never illustration), shot fresh
  for every post: new stills/clips generated for that post (`comfy-gen`, LTX),
  never reused from an earlier post (Robert, spark#133).
- **No legible words in any generated image.** Pages, slides, whiteboards,
  menus and book spines are out of focus, at an angle or smudged — generated
  text is gibberish, and the job forbids text in images.
- Never AI-generated faces. No people in focus: at most a hand at the frame
  edge or a figure from behind.
- No phone screens, and never app UI in generated images; phones face-down,
  in a pocket or out of frame.
- **Real app footage:** none is in `12fdk/motion` today (checked 2026-10-15).
  The real App Preview walkthrough exists only in the app repo (§9). If
  `/workspace/motion/assets/snapdeck/footage-walkthrough.mp4` exists, a reel
  may use a moment of it (a different moment from recent reels, cut around new
  b-roll); it is the only place app UI may appear. Until then, reels show no
  UI at all.
- Every post looks new: a different setting, light, colour mood and composition
  from the app's recent posts (`marketing-post looks --app snapdeck`); for a
  reel also the other reel look and the next music variant. §6's Look column
  gives each row its own scene as a starting point.
- One product message per post; one clear takeaway (brand tone).
- The hook names **a concrete piece of study material or a concrete exam AND a
  concrete problem** ("Midterm Friday. An 80-page PDF just landed."). Never a
  generic exam-season pep talk (§5 baseline). No emoji in the hook; at most one
  emoji in a caption.
- Voice (app record): "your study buddy who figured out a shortcut" — a fellow
  student, casual, contractions, empathetic about finals panic and
  procrastination, never shaming. Dry humour is welcome (20% of posts).
- **No gamification language**: never "streak", "XP", "level up" or "don't
  break the chain" (app record rule; see §9 for the conflict with the site).
- Science angle (app record's top-post formula): name a finding qualitatively
  — the testing effect / retrieval practice (Roediger & Karpicke, 2006), the
  spacing effect (Cepeda et al., 2006), Ebbinghaus's forgetting curve,
  interleaving, desirable difficulties (Bjork), the generation effect. No
  percentages, sample sizes or other studies — the same rule as `prompt.md` §3.
- Never name a competitor (Anki, Quizlet, Brainscape, …) in a post.
- CTA (the app is live), verbatim from the app record's ctaOptions:
  - Default on every post: "Download free on the App Store".
  - Allowed in its place on reels: "Try SnapDeck AI free" or "Turn your notes
    into flashcards".
  - Carousels may add "Save this for exam season".
  - Finals rows (Nov 23 – Dec 14) may add "Tag a friend who needs this for
    finals"; group-study rows may add "Share to your study group".
  - Not used until the bio link is set (§9): "Link in bio". Not used:
    "Start studying smarter today" (generic).
- Requirement line: every caption ends, before the hashtags, with one short
  line from the site: "Needs an iPhone 15 Pro or later with Apple
  Intelligence." Never on a slide or in a reel frame.
- At most 5 hashtags per post, always including `#SnapDeckAI`. The rest come
  from the brand list (`#AIFlashcards`, `#Flashcards`, `#StudentLife`,
  `#ExamPrep`, `#StudyTips`, `#StudyGram`, `#StudyMotivation`, `#StudyNotes`,
  `#StudySmarter`) plus at most one tag for the §6 calendar moment (e.g.
  `#FinalsWeek`, `#Midterms`, `#NewSemester`).
- One video per episode.
- **Reel looks** — two SnapDeck skins on motion's reel looks, alternating reel by
  reel (never `editorial`, which is Event Stories' skin):
  - **Highlighter** = `look: "bold"`, `accent: "#FBBF24"`, `ink: "#16151F"`,
    `bg: "#16151F"`: Anton caps in gold highlight bars. For hooks, countdowns,
    ranked lists.
  - **Lamp** = `look: "clean"`, `accent: "#FBBF24"`, `ink: "#FFFFFF"`,
    `bg: "#3730A3"`: Bricolage over a dark scrim. For calm, late-night and
    privacy reels.
  - No `font` override: the site uses the system font, so the look's own face
    stays.
  - End card: the CTA, sub "Free on the App Store", and the real app icon
    (`images/app-icon.png` from this repo, copied to
    `/workspace/motion/assets/snapdeck/app-icon.png`). Never an AI-made icon.
- **Music**: `audio: {"bed": "music", "variant": n, "clips": true}` — a music
  bed with the clips' own room sound under it (page turns, rain, a train). Keep
  any clip sound low with the scene `volume`. Rotate the 6 variants in the
  SnapDeck order **v3 e-min → v4 d-major → v1 a-major → v5 c-min → v0 c-major →
  v2 g-min**, so no variant repeats within 6 consecutive reels. §6's Music
  column carries the order.
- Use copy verbatim from the live site where possible, e.g. "Point your camera
  at your textbook, lecture slides or messy handwriting — SnapDeck AI turns them
  into flashcards in seconds." The §5 claim sheet lists what each feature may say.
- A post that breaks any rule is not published: set it back from `ready` and
  log why in §8.

## 4. Cadence

- Set 2026-10-15 for the academic year (spark#140); a student audience peaks
  around exams, so the cadence follows the exam calendar instead of a flat
  ramp.

  | Week of | Posts | Why |
  |---|---|---|
  | Oct 19 | 2 | restart after six weeks without posts |
  | Oct 26 – Nov 23 | 3–4 | midterms tail, reading week, Thanksgiving |
  | Nov 30 – Dec 7 | 5 | finals peak |
  | Dec 14 | 4 | last finals |
  | Dec 21 – Dec 28 | 3 | winter break (floor) |
  | Jan 4 | 4 | UK January exams |
  | Jan 11 – Jan 18 | 5 | new semester, new decks |
  | From Jan 25 | 4 | steady (2 reels + 2 carousels) |

- Floor: never below 3/week. Consistency beats bursts: if a week can't be
  filled, spread posts out instead of batching.
- Mix: about half reels (reach) and half carousels (saves).
- Slots: evening for both the UK and the US East Coast, 17:00–20:00 UTC.
  Prefer Thursday and Sunday when a week has a free slot. (The app record's
  `[Auto-observed 2026-08]` data shows Thu/Sun and 17:00 UTC as active; it is
  a hint, not a rule.)
- The 20h gap allows ~8 posts/week, so 5 fits. Avoid FB link posts.

## 5. Format playbook

| Format | Job | Evidence | Rules |
|---|---|---|---|
| Reel (15–30 s) | Reach to non-followers | App record: "Reels 15-30s (highest reach)"; SnapDeck has never posted one | 4–6 shots of 2–4 s; hook on screen at 0 s; ≤ 5 LTX clips; Highlighter/Lamp skin (§3); next music variant; end card with the real icon |
| Carousel (5–8 slides) | Saves | App record: "Carousels 5-8 slides (highest saves)" | Slide 1 = the hook (material/exam + problem); photo slides at 2 and in the middle; one idea per slide; last slide = CTA |
| Stories | Polls, quizzes, exam countdowns | App record wants them daily; 57 were posted Apr–Sep 2026, 7 expired unpublished | Pipeline is feed-only today — decision in §9 |
| Single image | Announcements only | All 57 measured posts were single images (baseline below) | Not in the steady mix |

Series (each §6 row names one; rotate so no series runs twice in a row):

| Series | Format | What it is |
|---|---|---|
| **Snap it** | Reel | one real piece of material (PDF, slides, whiteboard, handout, vocab page) + its deadline → a deck |
| **Countdown** | Reel / carousel | a concrete exam N days out + what to do each day |
| **Ranked** | Carousel | study methods ranked worst → best, with the reason |
| **By hand vs SnapDeck** | Carousel | one row of the site's comparison table, made concrete |
| **No signal** | Reel | a real place with no connection (basement, tunnel, plane) + an exam |
| **Science, no numbers** | Carousel | one named finding (§3), explained plainly, ends on an A/B question |
| **One deck per subject** | Carousel / reel | one course with a volume problem (pharmacology, contract law, vocab) |
| **1 a.m.** | Reel | relatable student humour, dark mode, last-minute |
| **Yours only** | Reel / carousel | privacy: no account, no upload (5% of posts) |

App-record pillar split: study productivity tips 35%, app features in action
25%, relatable student humour 20%, exam season 15%, privacy/tech 5%.
Audience: students 16–28 (US and UK college/university first; STEM, pre-med,
law, language learners; then AP/IB, A-level and board-exam students), iPhone
users, privacy-conscious.

Baseline (platform posts 2026-04-06 – 2026-09-03: 101 feed posts published,
57 with metrics, all single images; the 32 carousels have no metrics, see §9;
median reach 0, best reach 3; zero saves and shares; read 2026-10-15):

- **Best** — reach 2–3: "That 80-page PDF your professor 'just emailed
  over'?" (reach 3), "Study habits, ranked worst to best:", "The 25/5 study
  hack that actually sticks:", "The science is brutal:".
- **Worst** — reach 0: generic exam-season openers ("Spring midterms hit
  different.", "2 weeks until exams. You've got this 💪", "Finals week is
  closer than you think 📚") and feature-first lines ("Stop retyping your
  notes into flashcards.").
- **Read:** a specific piece of material with a specific size or deadline
  wins; ranked lists and science come next. Banned opener: an exam season or
  a pep talk with no concrete material and no concrete problem, or the app
  name first.
- Weak signal (reach 0–3), but it is the only data. The first reels ever and
  the new look are the test.

### Claim sheet — what each §6 feature may say (added 2026-10-15)

Verbatim from the live site (homepage, `llms.txt`, `llms-full.txt`, read
2026-10-15). Use these lines, not paraphrased numbers or promises. If a line
here and the site disagree, the site wins.

| §6 feature | Verbatim line(s) |
|---|---|
| Photo → deck | "Point your camera at your textbook, lecture slides or messy handwriting — SnapDeck AI turns them into flashcards in seconds." · "Take a photo of your textbook, lecture notes, or handout. SnapDeck AI reads the content and generates a complete flashcard deck in seconds." · "A textbook page, a lecture slide, your own scribbles. Take the photo and you have a deck before you've found a pen." |
| Photos of slides / whiteboards | "Photos & slides — pages, whiteboards, projector shots" |
| PDF import | "PDF import — drop in a handout or reading list" · "PDFs and lecture handouts" → "Import it straight in" |
| Typed text | "Type it yourself — when you already have the text" |
| Edit any card | "Not quite right? Edit any card in a tap." |
| Handwriting (honest) | "Usually. Clear handwriting in decent light works well; a rushed page photographed in a dark room is harder." Never promise it reads any handwriting. |
| Study mode | "Flip, answer, mark it Know it or Review. SnapDeck keeps score so you stop re-reading the stuff you already know." · "Cards you miss come back." · "Due cards surface first." |
| Progress | "Percent mastered per deck and per week — not \"time spent studying\"." · "Progress stats — see what's mastered, honestly" |
| A deck per subject | "A deck per subject — Biology, Spanish, whatever Thursday's exam is." |
| Volume problem | "Med, bio, law — hundreds of terms per module and no realistic way to hand-write cards for all of them." |
| Vocab / languages | "A page of new words, a menu, a slide from class. Snap it and you have a vocab deck for the bus ride home — no signal needed" · "it builds decks from material in the language you're studying" · "39 languages — study in the one you think in" |
| Works offline | "Airplane mode — the AI doesn't need a connection" · "making decks and studying both work in a basement seminar room, on a train, or in airplane mode." |
| Privacy | "No sign-up, no email, no upload. Your notes stay yours — which also means nobody can lose them for you." · "No account, ever" · "Your study materials never leave your device." |
| Dark mode | "Dark mode — built for the 1 a.m. session" |
| By hand vs SnapDeck (site table) | "Building a deck from one chapter: 20–40 minutes of copying" vs "Seconds" · "Getting text off a photo: You retype all of it" vs "Read for you" · "Studying with no signal: Fine — if you brought the cards" vs "Everything runs offline" · "Knowing what you've mastered: Two piles and a feeling" vs "Tracked card by card" · "Losing them the week before finals: Genuinely possible" vs "They're on your phone" · "What it costs: Index cards, pens, your evening" vs "Free to start" |
| Finals rescue | "It's Tuesday, the exam is Thursday, and the notes are a mess. Turn what you have into questions tonight and spend Wednesday finding out what you don't know yet." |
| Price | "Free to start" · "3 new decks every month" · Premium "One-time. Buy it once, keep it. No subscription." Never quote a price (the storefront sets it). |
| Requirements | "iPhone 15 Pro or later, running iOS 26" · "Requires iOS 26 and Apple Intelligence" |

Never claim: an Android, iPad, Mac or web version; cloud sync or backup;
sharing decks with classmates; a spaced-repetition algorithm or scheduling
(say "cards you miss come back", nothing more); image occlusion; Anki or
Quizlet import/export; a perfect or percentage accuracy; better grades or any
score improvement; any user count, rating, review or testimonial (0 ratings,
and the homepage personas are not testimonials); streaks or XP as a selling
point (§3); that the app has no streaks (it has them — §9).

## 6. Content plan (week of Oct 19, 2026 – week of Feb 15, 2027)

### Calendar hooks — the academic year this plan rides (added 2026-10-15)

A study app wins in the weeks BEFORE an exam, when the notes pile up — not on
exam day. Post 1–3 weeks before the exam crunch, and let the hook name the
material or exam AND a concrete problem ("Finals are coming!" alone is the
banned generic opener, §5). The moment also gives the post its look (season,
light, place), which keeps every post new. Most academic moments are patterns
that vary by school: never state a date or a statistic for them.

| Moment | Date | Post by | Angle | §6 rows |
|---|---|---|---|---|
| **Fall midterms** (US) | pattern: mid-Oct – early Nov | now | the PDF / slides that landed before the midterm; ranked methods | Oct 19 #1–#2, Oct 26 #1, Nov 2 #1–#2, #4, Nov 9 #1 |
| **Clocks go back** | Sun Oct 25, 2026 (UK/EU); Sun Nov 1, 2026 (US) | Oct 26 | dark by 5 pm, the 1 a.m. session, dark mode | Oct 26 #1 |
| **Halloween** | Sat Oct 31, 2026 | Oct 29 | humour: the scariest thing is the whiteboard about to be wiped | Oct 26 #3 |
| **UK reading week** | pattern: early Nov, varies by university | Nov 2 | catch up on five modules of notes | Nov 2 #3 |
| **US Thanksgiving break** | Thu Nov 26, 2026; travel the days before | Nov 23 | the flight home in airplane mode; finals the week after | Nov 23 #1–#3 |
| **Fall finals** (US) | pattern: early – mid Dec, varies by school | Nov 16 (3-week countdown) | countdowns, due cards first, the Tuesday-before-Thursday rescue, tag a friend | Nov 16 #1–#2, Nov 23 #2, #4, Nov 30 #1–#5, Dec 7 #2–#5, Dec 14 #1, #3 |
| **End of term, winter break** | pattern: mid-Dec – early Jan | Dec 7 | the train home, keeping it fresh over break | Dec 7 #1, Dec 14 #3, Dec 21 #1–#3, Dec 28 #1 |
| **UK January exams and mocks** (uni exams, A-level/GCSE mocks) | pattern: January, varies by school | Dec 21 | exam in 3 weeks and it's Christmas; notes from September | Dec 21 #1, #3, Dec 28 #1, Jan 4 #1, #4 |
| **New year, new semester** | Jan 1, 2027; US spring semester starts mid-Jan (pattern) | Dec 28 | one deck per subject from day one; syllabus week; resolutions without gamification | Dec 28 #2–#3, Jan 4 #3, Jan 11 #1–#2, #4, Jan 18 #2–#3, #5 |
| **Board-exam prep** (MCAT, LSAT, GRE, bar) | year-round; test dates per exam (not verified) | Jan 11 | one deck per subject for the long haul | Jan 11 #5 |
| **First quizzes of the semester** | pattern: late Jan – early Feb | Jan 25 | a 7-day plan, the whiteboard before it's wiped | Jan 25 #1–#4 |
| **Valentine's Day** | Sun Feb 14, 2027 | Feb 8 | humour: you, a coffee and 120 anatomy terms | Feb 8 #1 |
| **Spring midterms** | pattern: late Feb – March | Feb 1 | space it out now; 2-week and 5-day countdowns | Feb 1 #4, Feb 8 #2, Feb 15 #1, #3–#4 |
| **Spring finals, AP/IB exams** | pattern: May | next plan (from Apr) | — | — |

Dates checked 2026-10-15: Halloween, Valentine's Day and New Year are fixed;
clock changes are computed from the rules (last Sunday of October in the
UK/EU, first Sunday of November in the US); Thanksgiving = 4th Thursday of
November. Everything else is a pattern, not a date: hooks say "finals in 3
weeks", never "finals on Dec 7".

### The plan

| Week of | # | Format | Series | Feature / message | Hook (first 1–2 s) | Reel look · music | Look / scene (start point; must differ from recent looks) | Status |
|---|---|---|---|---|---|---|---|---|
| Nov 2 | 3 | Carousel | One deck per subject | A deck per subject | "Reading week: five modules, five piles of notes. Start here." | — | five coloured folders stacked on a student-flat floor, low autumn sun across floorboards | built 2026-10-28 6ae204c5a80dd396a885 |
| Nov 2 | 4 | Reel | Snap it | Projector slides | "Lecturer flew through 40 slides in 50 minutes. You got photos of 12." | Highlighter · v0 c-major | empty lecture hall from the back row, projector beam with dust, blank screen glow | queued |
| Nov 9 | 1 | Reel | Snap it | Vocab decks (39 languages) | "Spanish quiz Monday. One page of new vocab and a bus ride home." | Lamp · v2 g-min | night bus window, city-light bokeh, notebook on a knee, yellow grab pole | queued |
| Nov 9 | 2 | Carousel | Ranked | Study mode | "Highlighting vs re-writing notes vs flashcards: ranked for exam day." | — | overhead white desk, three gold highlighters, a blurred textbook page, hard noon light | queued |
| Nov 9 | 3 | Reel | Yours only | Nothing leaves your phone | "Photographing your lecture notes shouldn't mean uploading them." | Highlighter · v3 e-min | notebook held shut by an elastic band, rain on a café window, warm gold interior | queued |
| Nov 9 | 4 | Carousel | One deck per subject | Volume problem (med/nursing) | "Pharmacology block exam: 200 drug names and no evenings left." | — | hospital break-room table, folded scrubs, clipboard, cool fluorescent with a gold tea tin | queued |
| Nov 16 | 1 | Reel | Countdown | Know it / Review + progress | "Finals in 3 weeks. Which chapters do you actually know?" | Lamp · v4 d-major | three stacked textbooks with gold page tabs, evening desk, indigo window | queued |
| Nov 16 | 2 | Carousel | Science, no numbers | Spacing effect | "Cram the night before, or 15 minutes a day for 3 weeks?" | — | frosty campus quad at sunrise, empty bench, takeaway cup with a gold lid | queued |
| Nov 16 | 3 | Carousel | By hand vs SnapDeck | PDF import | "Law reading list: 6 PDFs, 1 week. Print and copy — or import?" | — | law library long tables, green-shaded lamps, stacked casebooks, deep wood | queued |
| Nov 16 | 4 | Reel | Snap it | Handwriting + edit any card | "Notes in handwriting only you can read?" | Highlighter · v1 a-major | spiral notebook macro under a gold lamp, pencil shavings, unreadable scrawl | queued |
| Nov 23 | 1 | Reel | No signal | Airplane mode | "Flying home for Thanksgiving, finals the week after. Airplane mode, still studying." | Lamp · v5 c-min | tray table at a window seat, wing at sunset, notebook and pencil, phone face-down | queued |
| Nov 23 | 2 | Carousel | Countdown | Photo → deck + study mode | "Back from Thanksgiving break, finals in 10 days: the plan." | — | family kitchen table, half-eaten pie dish, notebooks, warm tungsten | queued |
| Nov 23 | 3 | Reel | 1 a.m. | Photo → deck | "Sunday night after break: six lectures to catch up on." | Highlighter · v0 c-major | half-unpacked suitcase on a dorm floor, notes spilling out, gold fairy lights | queued |
| Nov 23 | 4 | Carousel | One deck per subject | A deck per subject | "History final: 60 names and dates across 4 lectures." | — | old hardback books stacked under a brass lamp, dusk, dark green and gold | queued |
| Nov 30 | 1 | Reel | Countdown | Cards you miss come back | "Finals week: 4 exams in 5 days. Study what you don't know yet." | Lamp · v2 g-min | 24-hour library at night, rows of empty desks, one lamp on, first snow outside | queued |
| Nov 30 | 2 | Carousel | Ranked | Self-testing | "Finals week, ranked: all-nighter last, self-testing first." | — | dawn through tall library windows, a row of gold coffee cups, cold blue | queued |
| Nov 30 | 3 | Reel | Snap it | Photo → deck | "It's Tuesday, the exam is Thursday, and the notes are a mess." | Highlighter · v3 e-min | dorm bed covered in loose notes, gold string lights, night | queued |
| Nov 30 | 4 | Carousel | Science, no numbers | Forgetting curve | "Learned it Monday, gone by Wednesday? The forgetting curve." | — | rain on a window, steaming tea, closed notebook, grey-violet light | queued |
| Nov 30 | 5 | Reel | 1 a.m. | Dark mode | "1 a.m., roommate asleep, anatomy final at 9." | Lamp · v4 d-major | dark dorm room, one clip-on book light, curtain divider, deep indigo | queued |
| Dec 7 | 1 | Reel | No signal | Works offline | "Train home for the holidays, tunnels all the way, exam in January." | Highlighter · v1 a-major | train table seat, snowy fields blurred past the glass, gold reading light | queued |
| Dec 7 | 2 | Carousel | Countdown | Study mode | "Final in 72 hours: the last-three-days plan." | — | kitchen counter at dawn, toast, a rubber-banded card stack, bright cold light | queued |
| Dec 7 | 3 | Reel | Snap it | Photo → deck | "Study guide posted: 14 pages. Exam tomorrow." | Lamp · v5 c-min | campus computer lab, printer tray with fresh pages, cool blue with one gold lamp | queued |
| Dec 7 | 4 | Carousel | By hand vs SnapDeck | Decks on your phone | "Losing your flashcards the week before finals? 'Genuinely possible.'" | — | index cards spilled under lecture-hall seats, a dropped wool scarf | queued |
| Dec 7 | 5 | Carousel | Science, no numbers | Self-testing in a group | "Group study for finals: quiz each other, don't re-read together." | — | café table with two mugs and two card stacks, no people, steamy window, gold pastries | queued |
| Dec 14 | 1 | Reel | Countdown | Progress stats | "Last final on Friday. See what's mastered, honestly." | Highlighter · v0 c-major | snowy campus path at dusk, gold lamp posts | queued |
| Dec 14 | 2 | Carousel | Science, no numbers | Interleaving | "Six hours of chemistry, then nothing else? Try mixing subjects." | — | three different textbooks open on a big table, overhead, warm | queued |
| Dec 14 | 3 | Reel | 1 a.m. | Decks on your phone | "Last exam done. The 300 index cards on your floor: also done." | Lamp · v2 g-min | dorm floor with index cards and a broom, low morning sun | queued |
| Dec 14 | 4 | Carousel | Yours only | No account, no upload | "No account, no email, no upload: what that means for your notes." | — | closed notebook on a frosty windowsill, clean white light | queued |
| Dec 21 | 1 | Carousel | Ranked | Short daily study | "Winter break, January exams: 4 ways to keep it fresh, ranked." | — | cottage table by a fire, card stack, gold mug, snow outside | queued |
| Dec 21 | 2 | Reel | Snap it | Vocab from anywhere | "Christmas-market menu in German? That's a vocab deck." | Highlighter · v3 e-min | wooden market stall counter, steaming mug, light bokeh, menu card far out of focus | queued |
| Dec 21 | 3 | Carousel | Countdown | Study mode | "January exam in 3 weeks, and it's Christmas: a 20-minute-a-day plan." | — | sofa arm with a notebook, tree lights far out of focus | queued |
| Dec 28 | 1 | Reel | No signal | Works offline | "Cabin, no wifi, mocks in January." | Lamp · v4 d-major | snowy cabin window, wood-stove glow, notebook on a blanket | queued |
| Dec 28 | 2 | Carousel | One deck per subject | A deck per subject | "New semester, new modules: one deck per subject from day one." | — | crisp white desk, new notebooks still in wrap, January light | queued |
| Dec 28 | 3 | Carousel | Science, no numbers | Testing effect | "New year, four modules: test yourself, don't re-read." | — | sunrise over a city skyline from a student flat, gold | queued |
| Jan 4 | 1 | Reel | Countdown | Photo → deck | "January exams next week. Three modules, notes from September." | Highlighter · v1 a-major | frosty bike rack outside a library at dawn, warm lit windows | queued |
| Jan 4 | 2 | Carousel | By hand vs SnapDeck | Full site comparison | "Building a deck from one chapter: by hand vs with SnapDeck." | — | flat-lay of pens, blank index cards and a rubber band on cream paper | queued |
| Jan 4 | 3 | Reel | Snap it | Textbook page → deck | "30-page chapter, first lecture tomorrow." | Lamp · v5 c-min | campus bookstore aisle, spines blurred, paper bag on the floor | queued |
| Jan 4 | 4 | Carousel | One deck per subject | Volume problem (law) | "Contract law: 40 cases, one deck per topic." | — | stacked yellow legal pads, brass lamp, dark wood | queued |
| Jan 11 | 1 | Reel | Snap it | Lecture slides | "Syllabus week, and the slides are already 60 pages." | Highlighter · v0 c-major | lecture-hall seat view, closed laptop, slide glow, January blue | queued |
| Jan 11 | 2 | Carousel | Ranked | Short daily study | "Spring semester habits, ranked: from 'next week' to 10 minutes a day." | — | sunny dorm desk, a plant, gold lamp, morning | queued |
| Jan 11 | 3 | Reel | Yours only | Nothing leaves your phone | "Exam notes full of your own mistakes. Nobody else's business." | Lamp · v2 g-min | notebook in a coat pocket on a snowy bench | queued |
| Jan 11 | 4 | Carousel | Science, no numbers | Desirable difficulties | "Anatomy cards feel harder than re-reading the chapter? That's the point." | — | close-up of a card stack with a gold clip, grey morning | queued |
| Jan 11 | 5 | Carousel | One deck per subject | A deck per subject (boards) | "MCAT prep starting this month: one deck per subject." | — | medical library, review books with blurred spines, cool light | queued |
| Jan 18 | 1 | Reel | No signal | Works offline | "40 minutes underground, zero signal, quiz on Friday." | Highlighter · v3 e-min | empty subway platform, tiles, train blur, yellow safety line | queued |
| Jan 18 | 2 | Carousel | One deck per subject | Decks in the language you study | "Learning Japanese? Turn this week's textbook page into a deck." | — | cup of green tea, blurred textbook page, washi-paper texture, morning | queued |
| Jan 18 | 3 | Reel | Snap it | Handout → deck | "Lab handout: 6 pages of terms before Thursday's practical." | Lamp · v4 d-major | empty lab bench, safety goggles, glassware, cool white with a gold lamp | queued |
| Jan 18 | 4 | Carousel | By hand vs SnapDeck | Works offline | "Index cards or your phone in a library basement with no wifi?" | — | basement book stacks, low ceiling, single warm bulb | queued |
| Jan 18 | 5 | Reel | 1 a.m. | Photo → deck | "Week 2, and four chapters to catch up on already." | Highlighter · v1 a-major | beanbag in a dorm, laundry pile, loose notes, late-night lamp | queued |
| Jan 25 | 1 | Carousel | Science, no numbers | Testing effect (A/B) | "Two ways to study the same chapter. Only one shows up in the exam." | — | two coffee cups side by side in split warm/cool light | queued |
| Jan 25 | 2 | Reel | Snap it | Photos of whiteboards | "Study group filled the whiteboard. Someone's about to wipe it." | Lamp · v5 c-min | glass-walled group study room, gold marker on the ledge, smudged board | queued |
| Jan 25 | 3 | Carousel | Countdown | Study mode | "First quiz in a week: a 7-day plan from the slides you have." | — | weekday desk at sunrise, pale gold | queued |
| Jan 25 | 4 | Reel | One deck per subject | Volume problem (nursing) | "Nursing: 120 terms before the first anatomy quiz." | Highlighter · v0 c-major | skills-lab bed with a folded blanket, stethoscope, cool blue | queued |
| Feb 1 | 1 | Reel | Yours only | No sign-up, no upload | "Quiz in an hour, and the app wants an account first? Not this one." | Lamp · v2 g-min | café window seat in the rain, gold lamp | queued |
| Feb 1 | 2 | Carousel | Ranked | Photo → deck | "Ways to make flashcards, ranked by time: by hand to one photo." | — | overhead stationery spread: scissors, card, pens, on indigo paper | queued |
| Feb 1 | 3 | Reel | No signal | Works offline | "Library wifi down again, quiz at 2. The deck still works." | Highlighter · v3 e-min | library atrium in winter sun, gold banister, long shadows | queued |
| Feb 1 | 4 | Carousel | Science, no numbers | Spacing effect | "Midterms in 3 weeks, four chapters each: space it out now." | — | February park bench with thin snow, notebook, grey-lilac | queued |
| Feb 8 | 1 | Reel | 1 a.m. | A deck per subject | "Valentine's plans: you, a coffee, and 120 anatomy terms." | Lamp · v4 d-major | café table, pink-and-gold light, latte, closed notebook | queued |
| Feb 8 | 2 | Carousel | Countdown | Study mode | "Spring midterms in 2 weeks: what to do each day." | — | early-spring window, snowdrops in a jar, notebook | queued |
| Feb 8 | 3 | Reel | Snap it | Edit any card | "Bio deck from Tuesday's lecture, one card came out wrong? Fix it in a tap." | Highlighter · v1 a-major | pencil eraser shavings macro, gold pencil, grey morning | queued |
| Feb 8 | 4 | Carousel | One deck per subject | A deck per subject | "Psych 101: 50 key terms, one photo per page." | — | lecture-hall stairs with a backpack, late-afternoon light | queued |
| Feb 15 | 1 | Reel | Countdown | Cards you miss come back | "Midterm in 5 days. Start with the cards you missed." | Lamp · v5 c-min | dusk campus, lilac sky, lit library windows | queued |
| Feb 15 | 2 | Carousel | By hand vs SnapDeck | Price (free to start) | "What it costs: index cards, pens, your evening — or free to start." | — | stationery-shop shelf far out of focus, a tin of gold paper clips, warm | queued |
| Feb 15 | 3 | Reel | No signal | Works offline | "Field-trip coach, two hours, no signal, test on Monday." | Highlighter · v0 c-major | coach window, early-spring countryside, notebook | queued |
| Feb 15 | 4 | Carousel | Science, no numbers | Generation effect | "Today's lecture notes: turn them into questions tonight." | — | gold sticky notes on a window grid, evening city | queued |

Plan totals (by week-of month): 71 posts — Oct 5, Nov 21, Dec 15, Jan 18,
Feb 12. Reels 35, carousels 36. All `queued`.

- Reel look · music: the reel looks alternate Highlighter / Lamp, and the music
  runs in the SnapDeck order v3, v4, v1, v5, v0, v2 (§3). If a row is swapped
  or skipped, keep both sequences going from the last reel actually built, and
  check the last 6 reels in `marketing-post looks`.
- Every post ends with "Download free on the App Store" (or a §3 alternative);
  carousels may add "Save this for exam season".
- The Look column is a starting point, not a script: the nightly job still
  checks `marketing-post looks` and changes anything that repeats a recent
  post. Every scene keeps the §3 house look (one gold element, indigo in the
  shadows, no legible words). Hooks may be tightened; the material/exam +
  problem must stay.
- Hooks name dates only when the date is fixed in the calendar hooks table.
  Numbers in hooks (80 pages, 200 drug names, 4 exams in 5 days) are the
  scenario, not a statistic; never present them as facts about users.
- Science rows name one finding from §3, qualitatively, and end on an A/B or
  open question (the app record's top-post formula).
- The nightly job may swap a row only per a §7 verdict, and must log the swap
  in §8.
- **Status** (spark#136): `queued` → `built <date> <postId>` (created,
  scheduled) → `posted <date> <postId>`. The nightly job builds the first
  `queued` row whose week starts within 7 days, one row per night, and writes
  its status here. Rows leave this table once their post is published
  (spark#138).
- Extend the plan by ~4 weeks when fewer than 4 weeks of `queued` rows remain
  (next: late Feb – March 2027 — spring midterms, spring break, then spring
  finals and AP/IB exams in May), using the calendar hooks table; log it in §8.

## 7. 7-day review procedure

1. Every Monday, select posts with `status=published` published 7–13 days ago
   that do not yet have a §8 learnings-log row (Appwrite db `marketing`, posts
   collection, appId `snapdeck`). The 1-day grace covers posts published on
   other weekdays.
2. For each post, read the metrics `collect-metrics` wrote into the post doc:
   reach, likes, comments, saves, shares (IG and FB). Note the doc's
   `metricsUpdatedAt`.
3. Read Umami (site `c00b28ce-d663-4166-8b80-6260f0f30d6f`) for the 7 days
   after publish: referrers from instagram.com / facebook.com (and their `l.`,
   `lm.`, `m.` hosts) and `appstore-click` by `placement`. There is no `/go`
   hop (§2), so this is funnel context only — not tied to a single post.
   Weekly context: `python3 /opt/data/scripts/social_funnel_report.py --app snapdeck`.
4. Compute **reach = IG reach + FB reach** and
   **eng = likes + comments + saves + shares** (summed across both platforms).
5. Verdict:
   - **PASS**: reach ≥ 5, or saves ≥ 1, or shares ≥ 1.
   - **FAIL**: reach ≤ 1 and eng = 0.
   - **HOLD**: anything else.
   - **NO-DATA**: metrics missing, or `metricsUpdatedAt` > 24h old. Rerun next
     week; do not judge the post.
6. Actions:
   - PASS: keep the series + format; add one more post of the same series (new
     subject or material) to §6 within 2 weeks.
   - HOLD: no change.
   - FAIL: rewrite the next planned §6 row with the same failure pattern
     (e.g. generic exam-season opener) to name concrete material and a
     concrete problem.
   - Rotate out: a series+format combo that FAILs 2 reviews in a row is
     replaced in next week's plan by the best PASS combo.
   - Reels vs carousels: after 4 reviewed posts of each, note in §8 which
     format leads on reach and which on saves; propose a §4 mix change in §9.
   - The §4 cadence floor always holds.
7. Re-baseline: when the median reach of the last 8 reviewed posts is ≥ 20,
   propose new thresholds in §9 for Robert. Do not change them without his
   approval.
8. Append one row per post to §8, using this template:

   ```
   | YYYY-MM-DD | <post id> "<hook>" (<format>, <series>) | IG r/l/c/s/sh · FB r/l/c/s/sh · Umami 7d IG/FB referrer visits, appstore-click | PASS/HOLD/FAIL/NO-DATA | <change made, or "none"> |
   ```

## 8. Learnings log

Append-only. Newest at bottom. Never edit or delete rows.

| Date | Post | Numbers | Verdict | Change |
|---|---|---|---|---|
| 2026-10-26 | 6ad0f5e90cad8c24dd40 "Midterm Friday. An 80-page PDF just landed." (reel, Snap it) | IG r/l/c/s/sh n/a · FB r/l/c/s/sh n/a (collect-metrics wrote nothing; metricsUpdatedAt null, issue #27) · Umami 7d (10-15→10-22): IG/FB referrer visits 0, appstore-click 0 | NO-DATA | none — re-judge once collect-metrics fills metrics |
| 2026-10-26 | 6ad2255a1c51d71b6804 "Midterm chapter re-read twice and still blank on the practice questions?" (carousel, Ranked) | IG r/l/c/s/sh n/a · FB r/l/c/s/sh n/a (collect-metrics wrote nothing; metricsUpdatedAt null, issue #27) · Umami 7d (10-19→10-26): IG/FB referrer visits 0, appstore-click 0 | NO-DATA | none — re-judge once collect-metrics fills metrics; also the §9 first-new-carousel check (still no metrics, #27) |
| 2026-10-26 | 6ad627f9c0baa0c35667 "Clocks went back. Dark by 5. Three bio chapters left before Thursday." (reel, 1 a.m.) | IG r/l/c/s/sh n/a · FB r/l/c/s/sh n/a (collect-metrics wrote nothing; metricsUpdatedAt null, issue #27) · Umami 7d (10-19→10-26): IG/FB referrer visits 0, appstore-click 0 | NO-DATA | none — re-judge once collect-metrics fills metrics; doc still carries errorMessage "Failed on: instagram" despite status published |

- 2026-10-15 — file created (spark#140): the SnapDeck nightly social job reads
  this file. Own look set in §3: indigo/white/gold text slides from the site
  tokens, the "desk level, one gold mark" photo style, Highlighter/Lamp reel
  skins and the SnapDeck music order. Baseline in §5 (101 feed posts Apr–Sep
  2026, median reach 0). §6: 71 rows, week of Oct 19, 2026 – week of Feb 15,
  2027, all `queued`.
- 2026-10-15 — built `snapdeck-oct19-1` (post 6ad0f5e90cad8c24dd40), §6 Oct 19 #1
  “Midterm Friday. An 80-page PDF just landed.” (reel, Snap it). First reel
  ever; Highlighter skin, music v3 e-min, PDF import; scheduled 2026-10-22T18:00Z.
  Audio: the v3 bed + frame-0 hit rendered to +0.7 dBTP (sibling reels -0.1 to
  -1.8); delivered MP4 limited with a two-pass loudnorm to -13.9 LUFS / -1.3 dBTP.
  Production note: Flux ignores negative prompts, so several stills had injected
  laptops/phones/half-legible letters and were re-shot; compositions were anchored
  to plain-wall / no-electronics scenes to keep §3 clean.

- 2026-10-16 — built `snapdeck-oct19-2` (post 6ad2255a1c51d71b6804), §6 Oct 19 #2
  "Midterm chapter re-read twice, still blank?" (carousel, Ranked). Study mode
  (Know it / Review); 8 slides, 2 fresh photos (library carrel desk-level with
  brass lamp, straight-overhead cards + yellow pencil), rust-and-gold autumn sun
  with indigo shadows; scheduled 2026-10-22T18:00Z. Product-focused, per the
  funnel (0 social-attributed visits, 0 App Store taps). Ranking runs 4 → 1,
  re-reading worst; the Nov 9 #2 and Nov 30 #2 rows reuse these methods —
  reword them when their turn comes.

- 2026-10-19 — built `snapdeck-oct26-1` (post 6ad627f9c0baa0c35667), §6 Oct 26 #1
  "Clocks went back. Dark by 5. Three bio chapters left before Thursday." (reel,
  1 a.m.). Dark mode + study mode support copy (Know it / Review, cards you miss
  come back, keeps score); Lamp skin (clean — alternating the 10-15 reel's
  Highlighter), music v4 d-major (next after v3 in the SnapDeck order); CTA
  "Try SnapDeck AI free"; scheduled 2026-11-01T18:00Z (Sun) — the Thursday slot
  is kept for the Halloween row (Oct 26 #3, "post by Oct 29"); the clock-change
  hook is fresh for the US (Nov 1) and already true for the UK/EU (Oct 25).
  Fresh window-seat shoot (prefix sd-social-20261019): blue hour, white-enamel
  lamp pool, gold mug as the single gold, indigo shadows; still retakes s2 t2,
  s3 t2, s5 t3 (first takes rendered brass/banker's lamps), each still
  vision-checked (no legible text, no electronics, no faces, one gold object).
  LTX: only 1 of the designed 3 clips survived — c3 (first + last frame
  checked clean); the c1/c5 window-seat clips drifted on both takes (melting
  lamp, vanishing book/mug, hard camera zoom) and failed frame QA twice each,
  so shots 1 and 5 run as stills with the template's slow push-in. Render WARN:
  the 15.5 s end-card hit was hard-clipped at full scale (template true-peak
  limiter missed it; render check 0.2 dBTP / 4.0 dB). Delivered MP4 (video
  untouched, audio AAC 192k) applies a targeted 4 dB dip on 15.40–15.95 s →
  −1.2 dBTP, ≈ −14 LUFS (evidence: out/snapdeck-oct26-1/delivered-ebur128-check.txt).
  Motion repo commit db0c0bd; NAS /nas/spark/videos/snapdeck-oct26-1/.

- 2026-10-20 — built `snapdeck-oct26-2` (post 6ad779edecf862f50594), §6 Oct 26 #2
  "One chapter of anatomy notes. 20–40 minutes of copying. Or seconds?" (carousel,
  By hand vs SnapDeck). Makes the site comparison row "building a deck from one
  chapter: 20–40 minutes of copying" vs "Seconds" concrete with one anatomy chapter.
  8 slides, photo-led (4 fresh photos + 4 short text slides), order T P T P T P P T;
  kitchen table in flat grey overcast daylight, cool blue-grey light with deep indigo
  shadows, one pad of yellow sticky notes as the only gold (index cards in a rubber
  band, an overhead card fan, a face-down phone over the page, a cleared table).
  Product-focused per the flat funnel (0 attributed visits, 0 App Store taps). CTA
  "Download free on the App Store" + "Save this for exam season"; 5 hashtags
  (#SnapDeckAI #AIFlashcards #Flashcards #StudyNotes #StudyTips); scheduled
  2026-10-28T18:00:00Z (Wed) — Thursday kept for the Halloween row (Oct 26 #3).
  Fresh shoot (prefix sd-social-20261020); all 4 photos vision-QA'd and re-shot:
  s2 hero fixed to index cards in a rubber band + indigo; s4 injected laptop removed
  + indigo; s6 (3rd take) two mid-frame hands and a COBRA logo/text on the phone back
  removed (plain featureless back, screen hidden); s7 fixed to exactly one gold
  (yellow pad) with a clear rubber band + indigo. Slide 1 hook restructured to a
  3-line material headline (number moved to the body) after the 5-line wrap split
  "20–40 / minutes". Claude review: items 1–12 PASS; slide 1 wrap fixed, P4
  top-left confirmed zero-legibility (blurred diagram), P6 anatomy labels accepted as
  unreadable.

- 2026-10-21 — built `snapdeck-oct26-3` (post 6ad8c4ef09aef52c3f91), §6 Oct 26 #3
  "Scariest thing this Halloween: the whiteboard your TA is about to wipe." (reel,
  Snap it). Photos of whiteboards: whiteboard → deck, Halloween humour frame;
  product-focused per the flat funnel (0 attributed visits, 0 App Store taps).
  Highlighter skin (alternating the 10-19 reel's Lamp), music v1 a-major (next
  after v3, v4 in the SnapDeck order); CTA "Download free on the App Store" (end
  card + sub "Free on the App Store" + real icon, hash-verified 2026-10-21);
  scheduled 2026-10-29T17:00:00Z (Thu) — Thursday per §4 and the Halloween row's
  "post by Oct 29"; 20 h gap checked against the schedule (no upcoming posts;
  latest published 2026-10-20T14:31Z). Fresh shoot (prefix sd-social-20261021):
  5 stills + 2 LTX clips. Retakes: s2 t1 (Flux injected a piece of black chalk,
  no gold object → t2 yellow marker in the tray); c1 t1 and c4 t1 (push-in too
  deep — window/pumpkin and marker out of the last frame, c4 grew a scratch →
  t2 with a "stay fully in frame" anchor; the thin line on c4 is the source
  still's faint smudge, consistent across the clip — not drift). All stills and
  both clips' first/last frames vision-QA'd (no legible text, no electronics,
  no faces, exactly one gold object — pumpkin s1/s5, yellow marker s2/s4,
  highlighter s3 — indigo shadows, white whiteboard). Render: all checks PASS;
  true peak +0.1 dBTP at the end-card hit (same as 10-19) → targeted 4 dB dip on
  15.35–16.35 s of the delivered MP4 (video untouched, AAC 192k) → −1.4 dBTP,
  −14.1 LUFS (evidence: out/snapdeck-oct26-3/delivered-ebur128-check.txt).
  Claude review: round 1 FAIL (FB emoji on the hook line — moved to the
  body; repo edits pending) → round 2 PASS after the §8/§6 updates; the
  reviewer withdrew the round-1 complaint about the pruned Oct 26 #2 row. Motion repo commit
  d1de557; NAS /nas/spark/videos/snapdeck-oct26-3/.

- 2026-10-22 — no row due tonight: the first `queued` §6 row is Nov 2 #1 and its
  week starts Nov 2 (11 days out); §7 review not due (not Monday; the oldest
  published post, 6ad0f5e90cad8c24dd40, went out 2026-10-15T19:31Z — outside the
  7–13 day window). Pruned the §6 Oct 26 #3 row (6ad8c4ef09aef52c3f91, published
  2026-10-21T14:30Z). Observations from the platform read: (a) all five built
  posts (Oct 19 #1–#2, Oct 26 #1–#3) published earlier than the slots the §8
  build rows record (e.g. Oct 26 #1: published 2026-10-19T17:00Z against the
  recorded 2026-11-01T18:00Z slot); in four docs `publishedAt` is days before
  `scheduledAt` and the `scheduledAt` is still future, and two carry
  `errorMessage: Failed on: instagram` despite `status: published` — whatever the
  publish path was, it did not follow the recorded slots; next builds should
  record the actual publish path, not only the intended slot. (b) All five have
  every metrics field and `metricsUpdatedAt` null 3–7 days after publish —
  collect-metrics (every 2 h) has written nothing; the §9 check (first new
  carousel 6ad2255a1c51d71b6804, 3 days old) fails; opened
  12fdk/snapdeck.12f.dk#27. The stuck `publishing` post 6a0ab5e70017d53c950c
  (since 2026-05-30) still sits in the schedule (§9, owner Robert).

- 2026-10-26 — built `snapdeck-nov2-1` (post 6adf67ec442d20ba79bc), §6 Nov 2 #1
  "Basement seminar room, zero bars, quiz in 20 minutes." (reel, No signal).
  Works offline; product-focused per the flat funnel (0 social-attributed
  visits, 0 App Store taps 7d). Lamp skin (alternating the 10-21 reel's
  Highlighter), music v5 c-min (next after v3, v4, v1 in the SnapDeck order);
  CTA "Download free on the App Store" (end card + sub "Free on the App Store"
  + real icon, hash-verified 2026-10-26); scheduled 2026-11-05T17:00:00Z (Thu)
  — inside the row's week (Nov 2–8), 20 h gap checked (latest published
  2026-10-21T14:30Z; only the stuck 2026-05-30 `publishing` post in the
  schedule, §9 owner Robert). Fresh shoot (prefix sd-social-20261026): 5 stills
  + 2 LTX clips (c1 slow dolly down the corridor, c4 near-static gold rail);
  all first takes passed vision QA (every still + first/last/mid clip frame:
  no legible text, no screens, no faces, one gold element); no retakes.
  Render: all machine checks PASS (19.0 s, hook at 0 s, −13.9 LUFS,
  −1.4 dBTP — no targeted dip needed). Frame-0 headline uses the design's
  trimmed "Zero bars. Quiz in 20 minutes." (≤ 6 words); the full row hook
  opens the IG caption. Watch: the platform published the five earlier posts
  before their recorded slots (§8 2026-10-22); record this post's actual
  publish path when it goes out. Motion repo commit 9dcd224; NAS
  /nas/spark/videos/snapdeck-nov2-1/.

- 2026-10-28 — built `snapdeck-nov2-3` (post 6ae204c5a80dd396a885), §6 Nov 2 #3
  "Reading week: five modules, five piles of notes. Start here." (carousel, One deck
  per subject). A deck per subject + photo → deck + study mode (Know it / Review,
  cards you miss come back); product-focused per the flat funnel (0 profile taps,
  0 site landings, 1 site visit, 0 App Store taps 7d). 7 slides T P T P T T T:
  slide 1 the hook, 2 fresh photos, 5 text, 7 the CTA. CTA "Download free on the
  App Store" + allowed carousel addition "Save this for exam season"; 5 hashtags
  (#SnapDeckAI #AIFlashcards #StudyNotes #StudyTips #ReadingWeek); requirement
  line before the hashtags; FB caption rewritten story-driven with the inline App
  Store link and 3 hashtags. Honest framing: the hook says "five modules" but the
  free tier is "3 new decks every month" — captions and slides say "a deck per
  pile" / "a deck per subject", never "five decks". Scheduled
  2026-11-05T17:00:00Z (Thu) — inside the row's week (Nov 2–8), §4 preferred day,
  20 h gap checked (latest published 2026-10-27T14:31Z; the next scheduled post
  sits at 2026-11-08T17:00Z, 72 h away; only the stuck 2026-05-30 `publishing`
  post in the schedule, §9 owner Robert). Watch: the platform published the
  earlier posts before their recorded slots (§8 2026-10-22); record this post's
  actual publish path when it goes out. Fresh shoot (prefix
  sd-social-20261028 / sd-social-20261028b): photo A five muted hardcover
  binders (teal, grey, cream, plum) with one gold-yellow stacked loose on oak
  floorboards, floor-level 35 mm, low late-afternoon amber autumn sun, long deep
  indigo shadows (t4 after t1/t2 rendered books and t3 notebook pads — vision-QA
  retakes); photo B close floor-level 50 mm, the gold binder's corner in sharp
  focus with muted indigo/slate binders blurred behind, amber sun streak, deep
  indigo shadows (t2 after t1 rendered legible cursive names). Both finals
  vision-QA'd: no legible text, no screens, no faces, exactly one gold object,
  indigo shadows, real floorboards. Look: student-flat floor at floor level,
  muted binder stack with one gold-yellow under low amber autumn sun, deep indigo
  shadows — distinct from all recent looks (not the 10-27 pre-dawn grey desk,
  not the 10-20 overcast kitchen, no carrel, no window seat, no corridor, no
  seminar room). Claude review: round 1 FAIL (expected — post not yet created and
  marketing.md not yet edited) → round 2 after creation and the §6/§8 edits.

- 2026-10-27 — built `snapdeck-nov2-2` (post 6ae0b2e04070d4eed057), §6 Nov 2 #2
  "Read your notes three times and still blanked? That's the testing effect."
  (carousel, Science, no numbers). Testing effect named qualitatively
  (Roediger & Karpicke, 2006 — the only citation, no numbers, no other
  studies); product-focused per the flat funnel (0 attributed social visits,
  0 App Store taps 7d): photo → deck → study mode (Know it / Review, cards you
  miss come back). 7 slides T P T P T T T: slide 1 the hook, 2 fresh photos,
  5 text, 7 the CTA. CTA "Download free on the App Store" + allowed carousel
  addition "Save this for exam season"; 5 hashtags (#SnapDeckAI #AIFlashcards
  #ExamPrep #StudyTips #Midterms); requirement line before the hashtags; both
  captions end on the A/B question (re-reading vs quizzing first); FB caption
  rewritten story-driven with the inline App Store link and 3 hashtags.
  Scheduled 2026-11-08T17:00:00Z (Sun) — inside the row's week (Nov 2–8), 20 h
  gap checked (latest published 2026-10-26T15:01Z; only the stuck 2026-05-30
  `publishing` post in the schedule, §9 owner Robert). Watch: the platform
  published the earlier posts before their recorded slots (§8 2026-10-22);
  record the actual publish path when this one goes out (deployed
  publish-social posts in the first 15-min cycle once the 20 h gap is met,
  ≈ 2026-10-28T11:00Z). Fresh shoot (prefix sd-social-20261027): 2 stills,
  desk-level side-on under a sloping roof window (closed face-down booklet,
  gold pencil, white tea mug, steam) and a tight macro (pencil tip at the
  paper edge, smudged marks); both first takes passed vision QA (no legible
  text, no screens, no faces, exactly one gold object, indigo shadows); no
  retakes. Look: top-floor student room desk under a sloping roof window,
  pre-dawn steel-blue grey with first pale light and deep indigo shadows, one
  gold pencil on a closed face-down exam booklet, tea steam backlit by the
  window — distinct from all six recent looks (not the 10-20 overcast
  kitchen: no sticky pad, no index cards, no overhead fan). Claude review:
  round 1 FAIL (expected — post not yet created and marketing.md not yet
  edited) → round 2 after creation and the §6/§8 edits above.


## 9. Open questions & watch items

- **iOS requirement mismatch** (owner: Robert) — the site, `llms-full.txt`
  and `prompt.md` say iPhone 15 Pro or later with iOS 26; the App Store
  listing reports `minimumOsVersion` 18.1 (lookup 2026-10-15), and the app
  record says "iOS 18.1+ required". Posts follow the site. Confirm which is
  right and update the other.
- **Streaks & XP vs the brand rule** (owner: Robert) — the site sells "Streaks
  & XP"; the app record says "Never use gamification language"; an earlier
  post (2026-05-17) said "SnapDeck doesn't have streaks.", which the site
  contradicts. §3 follows the app record (no streak/XP talk, never claim there
  are none). Decide whether that stays.
- **Real app footage** (owner: Robert) — the en-US App Preview walkthrough
  (27.8 s, 1320×2868, real UI recorded with idb) is at
  `/Users/robert/Git/SnapDeck/fastlane/previews/en-US/IPHONE_67/walkthrough.mp4`
  on the Mac, not in `12fdk/motion`. The app record wants "screen recordings
  of photo-to-flashcard flow" in reels. Decide whether to copy it to
  `assets/snapdeck/footage-walkthrough.mp4` in the motion repo; §3 then lets
  reels use it.
- **No `/go` hop, bio link unknown** (owner: Robert) — the site has no
  `/go/?src=` hop (social shows only as referrers), and the bio link of
  `@snapdeckai_app` is not confirmed. Set the bio link (landing page or App
  Store); then "Link in bio" can join the §3 CTAs. A `/go` hop like the
  Event/Travel Stories sites would give per-source numbers.
- **Stuck post** (owner: Robert) — `6a0ab5e70017d53c950c` ("Group study
  energy check", image) has been `publishing` since 2026-05-30. Fail or delete
  it so the schedule is clean.
- **Carousels have no metrics** (owner: Hermes) — none of the 32 published
  carousels (Apr–Sep 2026) has metrics; all 57 measured posts are single
  images. Check after the first new carousel that `collect-metrics` fills it;
  if not, open an issue — §7 cannot judge carousels without it.
- **Look ledger empty** (owner: Hermes) — `marketing-post looks --app
  snapdeck` was empty on 2026-10-15. Run `marketing-post ledger-backfill --app
  snapdeck` once (spark#140 checklist).
- **Schedule owner** (owner: Robert) — set `apps.scheduleOwner = hermes` for
  snapdeck on the platform (spark#140 checklist), or `schedule-posts` re-times
  the posts. `marketing-post schedule` said "schedule owner: platform" on
  2026-10-15.
- **Languages** — the site says 39 languages; the App Store lookup lists 47
  language codes. Posts say 39 (the site), or no number.
- **Stories decision** (owner: Robert) — the app record wants daily stories
  (polls, quizzes, countdowns); 57 were posted Apr–Sep 2026 and 7 expired
  unpublished. The pipeline is feed-only today.
- **Audience markets unknown** (owner: Robert) — the plan mixes US (midterms,
  Thanksgiving, finals, MCAT) and UK (reading week, January exams, mocks)
  moments, per the app record's "US and UK" audience. Check the IG/FB audience
  by country and swap rows if it sits elsewhere.
- **Pattern moments have no date** — midterms, finals, reading week, January
  exams, semester start and board-exam dates vary by school. Posts never state
  a date or a statistic for them.
- **More CTAs** (owner: Robert) — "Start studying smarter today" and "Link in
  bio" are in ctaOptions but not used (§3). Decide whether to add them.
- **`optimize-guidelines` is dormant** (owner: Robert): decide whether to
  enable it once §8 has ≥ 4 weeks of logs.


