#!/usr/bin/env python3
"""build.py — regenerate the SnapDeck AI blog from posts/*.md.

The site is hand-written static HTML with no build step, which is fine for a
landing page and hopeless for a blog: every new post has to be threaded into the
post page itself, the blog index, the homepage teaser, the RSS feed, the
sitemap, llms.txt and llms-full.txt. That is seven files of bookkeeping per
post, and the weekly post is written by an unattended agent. So the markdown in
posts/ is the source of truth and this script renders everything else.

    python3 tools/build.py            # validate, then write
    python3 tools/build.py --check    # validate only, write nothing (exit 1 on error)

Zero dependencies, stdlib only, so it runs identically on a laptop and inside
the Hermes container. Everything it writes is deterministic: run it twice and
the second run is a no-op.

Generated (do not hand-edit):
    blog/<slug>/index.html
    feed.xml
and the regions between BLOG:START / BLOG:END markers in:
    blog/index.html, index.html, sitemap.xml, llms.txt, llms-full.txt
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "posts"
BLOG_DIR = ROOT / "blog"
TEMPLATE = Path(__file__).resolve().parent / "templates" / "post.html"

SITE = "https://snapdeck.12f.dk"
TAGS = {"study-tips", "memory-science", "exam-prep"}
WORDS_PER_MINUTE = 200

MAX_TITLE = 70
MAX_DESCRIPTION = 160
MAX_EXCERPT = 220
MIN_WORDS = 700

# The direct answer that sits under the H1. Featured snippets, People Also Ask
# and voice results are all extracted from a short self-contained answer placed
# high on the page; a post that opens with narrative scene-setting has nothing
# for them to lift. 40–60 words is the band Google actually quotes.
MIN_ANSWER_WORDS = 35
MAX_ANSWER_WORDS = 70

# Every post has to phrase at least this many section headings as a real
# question. "The short version" cannot win a snippet; "How long does this
# actually take?" can.
MIN_QUESTION_HEADINGS = 2

# Who writes the blog. A named person with a page you can read beats an
# anonymous company byline: it is the difference between a source an answer
# engine paraphrases and one it cites.
AUTHOR = {
    "name": "Robert Jensen",
    "role": "Founder, 12F ApS",
    "url": f"{SITE}/about/",
}
PUBLISHER = {
    "name": "12F ApS",
    "url": "https://12f.dk/",
    "logo": f"{SITE}/images/app-icon.png",
}
# sameAs is the edge that ties the "SnapDeck AI" / "12F ApS" entity to the rest
# of the graph. Only URLs that genuinely resolve and genuinely belong to us.
SAME_AS = [
    "https://apps.apple.com/us/app/snapdeck-ai/id6759596002",
    "https://12f.dk/",
]

# Hand-written pages, listed here so build.py owns the whole sitemap. It used to
# rewrite only the fenced post block, which left / and /blog/ permanently
# claiming a lastmod of 2026-07-22 while both changed every week.
#
# lastmod None means "derive it": / and /blog/ both change whenever a post is
# published, so they take the newest post's date. The genuinely static pages
# carry an explicit date — bump it by hand when you actually edit the page.
STATIC_URLS = [
    ("/",                    None,         "monthly", "1.0"),
    ("/blog/",               None,         "weekly",  "0.8"),
    ("/about/",              "2026-08-27", "yearly",  "0.5"),
    ("/privacy-policy.html", "2026-02-24", "yearly",  "0.3"),
    ("/llms.txt",            None,         "monthly", "0.2"),
]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class BuildError(Exception):
    pass


# --- images ----------------------------------------------------------------
#
# Covers and inline photos arrive from ComfyUI as 1200px PNGs, which for a
# photograph is 700–950 KB. /blog/ was shipping 7.2 MB of them and every post
# page had an ~800 KB PNG as its LCP element. tools/optimize-images.py writes a
# WebP sibling for each one (~96% smaller) and everything below serves that
# through a <picture>, keeping the PNG as the fallback and as the og:image.
#
# Dimensions are read off the file rather than hardcoded. They used to be
# written as 1200x630 for covers and 1200x675 for figures while the actual
# images are 1200x624 and 1200x696 — wrong on every image on the site, which
# means a layout shift on every image on the site.

_PNG_SIZE_CACHE: dict[str, tuple[int, int]] = {}


def png_size(src: str) -> tuple[int, int]:
    """(width, height) straight out of the PNG IHDR chunk. Stdlib only."""
    if src in _PNG_SIZE_CACHE:
        return _PNG_SIZE_CACHE[src]
    path = ROOT / src.lstrip("/")
    try:
        head = path.read_bytes()[:24]
        if head[:8] != b"\x89PNG\r\n\x1a\n" or head[12:16] != b"IHDR":
            raise ValueError("not a PNG")
        size = (int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big"))
    except (OSError, ValueError):
        # A missing or unreadable file is already reported by validate_references
        # with a useful message; fall back so the build gets that far.
        size = (1200, 630)
    _PNG_SIZE_CACHE[src] = size
    return size


def webp_for(src: str) -> str | None:
    """The WebP sibling of a /images/... path, if it has been generated."""
    if not src.startswith("/") or not src.endswith(".png"):
        return None
    candidate = src[:-4] + ".webp"
    return candidate if (ROOT / candidate.lstrip("/")).exists() else None


def picture(src: str, alt: str, *, indent_by: int = 0, **img_attrs) -> str:
    """A <picture> serving WebP with the PNG as fallback.

    Falls back to a bare <img> when no WebP exists so a half-built checkout
    still renders; validate_references is what makes that state an error.
    """
    width, height = png_size(src)
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in img_attrs.items() if v)
    img = (f'<img src="{src}" alt="{attr(alt)}" width="{width}" height="{height}"'
           + (f" {attrs}" if attrs else "") + ">")
    webp = webp_for(src)
    if not webp:
        return indent(img, indent_by) if indent_by else img
    block = (f'<picture>\n'
             f'  <source srcset="{webp}" type="image/webp">\n'
             f'  {img}\n'
             f'</picture>')
    return indent(block, indent_by) if indent_by else block


# --- frontmatter -----------------------------------------------------------
#
# A deliberately tiny YAML subset — enough for the post schema and nothing more,
# so there is no PyYAML dependency and no surprises about what a stray colon or
# tab does. Supported: `key: scalar`, `key: [a, b]`, block scalars (`>` / `|`),
# `- item` lists, and lists of single-key mappings (the faq: block).

def _scalar(raw: str):
    raw = raw.strip()
    if not raw:
        return ""
    if raw[0] in "\"'" and raw[-1] == raw[0] and len(raw) > 1:
        return raw[1:-1].replace('\\"', '"')
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [_scalar(p) for p in inner.split(",")] if inner else []
    if raw in ("true", "false"):
        return raw == "true"
    return raw


def parse_frontmatter(text: str, where: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        raise BuildError(f"{where}: file must start with a `---` frontmatter block")
    end = text.find("\n---\n", 3)
    if end == -1:
        raise BuildError(f"{where}: frontmatter block is never closed with `---`")
    head, body = text[4:end + 1], text[end + 5:]

    data: dict = {}
    lines = head.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            raise BuildError(f"{where}: cannot parse frontmatter line {i + 1}: {line!r}")
        key, rest = m.group(1), m.group(2).strip()

        if rest in (">", "|", ">-", "|-"):            # block scalar
            i += 1
            chunk = []
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith("  ")):
                chunk.append(lines[i].strip())
                i += 1
            joined = "\n".join(chunk) if rest[0] == "|" else " ".join(c for c in chunk if c)
            data[key] = joined.strip()
            continue

        if rest == "":                                 # nested list
            i += 1
            items: list = []
            while i < len(lines) and (not lines[i].strip() or lines[i].startswith("  ")):
                item_line = lines[i]
                i += 1
                if not item_line.strip():
                    continue
                stripped = item_line.strip()
                if stripped.startswith("- "):
                    after = stripped[2:].strip()
                    sub = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", after)
                    if sub:                            # list of mappings (faq:)
                        items.append({sub.group(1): _scalar(sub.group(2))})
                    else:
                        items.append(_scalar(after))
                else:                                  # continuation of a mapping item
                    sub = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", stripped)
                    if sub and items and isinstance(items[-1], dict):
                        items[-1][sub.group(1)] = _scalar(sub.group(2))
                    else:
                        raise BuildError(f"{where}: cannot parse list item {stripped!r} under {key}:")
            data[key] = items
            continue

        data[key] = _scalar(rest)
        i += 1
    return data, body


# --- markdown --------------------------------------------------------------
#
# The subset the posts actually use. Anything outside it is a validation error
# rather than silently mangled output — a post that renders wrong is worse than
# a post that fails the build.

INLINE_CODE = re.compile(r"`([^`]+)`")
STRONG = re.compile(r"\*\*(.+?)\*\*")
EM = re.compile(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)\s]+)(?:\s+\"([^\"]*)\")?\)$")


def inline(text: str) -> str:
    """Escape, then re-introduce the handful of inline constructs we allow."""
    out = html.escape(text, quote=False)
    placeholders: list[str] = []

    def stash(markup: str) -> str:
        placeholders.append(markup)
        return f"\x00{len(placeholders) - 1}\x00"

    out = INLINE_CODE.sub(lambda m: stash(f"<code>{m.group(1)}</code>"), out)
    out = LINK.sub(lambda m: stash(f'<a href="{m.group(2)}">{m.group(1)}</a>'), out)
    out = STRONG.sub(lambda m: stash(f"<strong>{m.group(1)}</strong>"), out)
    out = EM.sub(lambda m: stash(f"<em>{m.group(1)}</em>"), out)
    for n, markup in enumerate(placeholders):
        # Nested constructs (a link inside bold) resolve on the second pass.
        markup = STRONG.sub(lambda m: f"<strong>{m.group(1)}</strong>", markup)
        markup = EM.sub(lambda m: f"<em>{m.group(1)}</em>", markup)
        markup = LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', markup)
        out = out.replace(f"\x00{n}\x00", markup)
    return out


def markdown_to_html(md: str, where: str) -> tuple[str, list[str]]:
    """Return (html, image_paths). Blocks are separated by blank lines."""
    blocks = re.split(r"\n\s*\n", md.strip())
    parts: list[str] = []
    images: list[str] = []

    for raw in blocks:
        block = raw.strip("\n")
        if not block.strip():
            continue
        lines = [ln for ln in block.split("\n")]
        first = lines[0].strip()

        if first.startswith("# "):
            raise BuildError(f"{where}: no `# ` heading in the body — the template renders "
                             f"the H1 from `title`. Use `## ` for sections.")
        if first.startswith("### "):
            parts.append(f"<h3>{inline(first[4:].strip())}</h3>")
        elif first.startswith("## "):
            parts.append(f"<h2>{inline(first[3:].strip())}</h2>")
        elif first in ("---", "***", "___"):
            parts.append("<hr>")
        elif IMAGE.match(first):
            m = IMAGE.match(first)
            alt, src, caption = m.group(1), m.group(2), m.group(3)
            if not alt.strip():
                raise BuildError(f"{where}: image {src} has no alt text")
            images.append(src)
            fig = [f'<figure class="post-figure">',
                   picture(src, alt, indent_by=2, loading="lazy", decoding="async")]
            if caption:
                fig.append(f"  <figcaption>{inline(caption)}</figcaption>")
            fig.append("</figure>")
            parts.append("\n".join(fig))
        elif first.startswith("> "):
            inner = "\n".join(ln.strip()[2:] if ln.strip().startswith("> ")
                              else ln.strip().lstrip(">").strip() for ln in lines)
            paras = "\n".join(f"  <p>{inline(p.strip())}</p>"
                              for p in re.split(r"\n\s*\n", inner) if p.strip())
            parts.append(f"<blockquote>\n{paras}\n</blockquote>")
        elif re.match(r"^[-*] ", first):
            items = _list_items(lines, r"^[-*] ", where)
            parts.append("<ul>\n" + "\n".join(f"  <li>{i}</li>" for i in items) + "\n</ul>")
        elif re.match(r"^\d+[.)] ", first):
            items = _list_items(lines, r"^\d+[.)] ", where)
            parts.append("<ol>\n" + "\n".join(f"  <li>{i}</li>" for i in items) + "\n</ol>")
        elif first.startswith("!["):
            # Looks like an image but IMAGE didn't match above — almost always a
            # missing URL (`![alt]` with no `(/path)`). One run shipped exactly
            # this: the alt text rendered as a literal paragraph and the generated
            # photo was orphaned. Never silently degrade it to text.
            raise BuildError(f"{where}: malformed image {first[:80]!r} — an image must be "
                             f"`![alt text](/images/blog/<slug>-N.png)` on its own line, "
                             f"with the path in parentheses")
        else:
            for ln in lines:
                if ln.strip().startswith(("#", ">", "- ", "* ")):
                    raise BuildError(f"{where}: block starting {first!r} mixes a paragraph "
                                     f"with {ln.strip()[:30]!r} — separate them with a blank line")
                if ln.strip().startswith("!["):
                    raise BuildError(f"{where}: image {ln.strip()[:60]!r} must be on its own "
                                     f"line, separated by blank lines")
            parts.append(f"<p>{inline(' '.join(ln.strip() for ln in lines))}</p>")

    return "\n\n".join(parts), images


def _list_items(lines: list[str], marker: str, where: str) -> list[str]:
    items: list[str] = []
    for ln in lines:
        stripped = ln.strip()
        if re.match(marker, stripped):
            items.append(inline(re.sub(marker, "", stripped, count=1)))
        elif stripped and items:
            items[-1] += " " + inline(stripped)          # wrapped list item
        elif stripped:
            raise BuildError(f"{where}: list block starts with a non-item line {stripped!r}")
    return items


# --- post model ------------------------------------------------------------

REQUIRED = ["title", "description", "lede", "answer", "excerpt", "tag", "date",
            "summary", "keywords"]


class Post:
    def __init__(self, path: Path):
        self.path = path
        self.slug = path.stem
        where = f"posts/{path.name}"
        self.where = where
        meta, body_md = parse_frontmatter(path.read_text(encoding="utf-8"), where)
        self.meta = meta
        self.draft = bool(meta.get("draft", False))

        missing = [k for k in REQUIRED if not str(meta.get(k, "")).strip()]
        if missing:
            raise BuildError(f"{where}: missing frontmatter field(s): {', '.join(missing)}")

        self.title = str(meta["title"]).strip()
        self.description = str(meta["description"]).strip()
        self.lede = str(meta["lede"]).strip()
        self.excerpt = str(meta["excerpt"]).strip()
        # The homepage teaser cards are narrower than the blog index cards.
        self.teaser_excerpt = str(meta.get("teaserExcerpt") or self.lede).strip()
        self.summary = str(meta["summary"]).strip()
        self.keywords = str(meta["keywords"]).strip()
        self.tag = str(meta["tag"]).strip()
        self.meta_title = str(meta.get("metaTitle") or f"{self.title} | SnapDeck AI").strip()
        self.og_title = str(meta.get("ogTitle") or self.title).strip()
        self.og_description = str(meta.get("ogDescription") or self.description).strip()
        self.twitter_description = str(meta.get("twitterDescription") or self.og_description).strip()
        self.cover_alt = str(meta.get("coverAlt", "")).strip()
        self.hero = bool(meta.get("hero", False))
        self.related = [str(s).strip() for s in (meta.get("related") or [])]
        self.faq = [f for f in (meta.get("faq") or []) if isinstance(f, dict)]
        # The 40–60 word extractable answer that sits under the H1.
        self.answer = str(meta["answer"]).strip()
        # Primary sources behind the memory-science claims. Answer engines
        # preferentially cite pages that themselves cite something.
        self.sources = [s for s in (meta.get("sources") or []) if isinstance(s, dict)]
        # Optional: posts that really are a numbered procedure get HowTo schema.
        self.howto = [s for s in (meta.get("howto") or []) if isinstance(s, dict)]
        self.howto_name = str(meta.get("howtoName", "")).strip()

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", self.slug):
            raise BuildError(f"{where}: filename must be a lowercase-kebab slug")
        if self.tag not in TAGS:
            raise BuildError(f"{where}: tag {self.tag!r} is not one of {sorted(TAGS)}")
        try:
            self.date = datetime.strptime(str(meta["date"]).strip(), "%Y-%m-%d").date()
        except ValueError:
            raise BuildError(f"{where}: date must be YYYY-MM-DD, got {meta['date']!r}")
        modified = str(meta.get("modified", "")).strip()
        if modified:
            try:
                self.modified = datetime.strptime(modified, "%Y-%m-%d").date()
            except ValueError:
                raise BuildError(f"{where}: modified must be YYYY-MM-DD, got {modified!r}")
        else:
            self.modified = self.date

        if len(self.title) > MAX_TITLE:
            raise BuildError(f"{where}: title is {len(self.title)} chars, max {MAX_TITLE}")
        if len(self.description) > MAX_DESCRIPTION:
            raise BuildError(f"{where}: description is {len(self.description)} chars, "
                             f"max {MAX_DESCRIPTION}")
        if len(self.excerpt) > MAX_EXCERPT:
            raise BuildError(f"{where}: excerpt is {len(self.excerpt)} chars, max {MAX_EXCERPT}")
        answer_words = len(re.findall(r"\b[\w'’-]+\b", self.answer))
        if not (MIN_ANSWER_WORDS <= answer_words <= MAX_ANSWER_WORDS):
            raise BuildError(
                f"{where}: answer is {answer_words} words, needs {MIN_ANSWER_WORDS}–"
                f"{MAX_ANSWER_WORDS}. It is the block directly under the H1 and the only "
                f"thing a featured snippet or a voice assistant can lift — one self-contained "
                f"paragraph that answers the title, no scene-setting (see prompt.md §5)")
        if self.answer.rstrip()[-1:] not in ".!?":
            raise BuildError(f"{where}: answer must be a complete sentence ending in punctuation")

        for s in self.sources:
            if set(s) != {"title", "url"}:
                raise BuildError(f"{where}: each sources entry needs exactly `title:` and `url:`")
            if not str(s["url"]).startswith("https://"):
                raise BuildError(f"{where}: source url {s['url']!r} must be an https:// link "
                                 f"to the primary source, not a paraphrase of it")
        if self.howto and not self.howto_name:
            raise BuildError(f"{where}: howto: needs a howtoName: — the name of the procedure, "
                             f"which is what HowTo schema puts in the result")
        for s in self.howto:
            if set(s) != {"name", "text"}:
                raise BuildError(f"{where}: each howto step needs exactly `name:` and `text:`")

        for f in self.faq:
            if set(f) != {"question", "answer"}:
                raise BuildError(f"{where}: each faq entry needs exactly `question:` and `answer:`")
            # The whole answer is a YAML double-quoted scalar, so a straight `"`
            # inside it is asking for trouble — models write `to"you can…"` with
            # no surrounding space and it renders (and lands in the FAQ schema)
            # looking broken. Require single/curly quotes instead.
            for k in ("question", "answer"):
                if '"' in str(f[k]):
                    raise BuildError(
                        f"{where}: faq {k} contains a straight double-quote (\") — "
                        f"use single quotes 'like this' or curly quotes for any quoted "
                        f"phrase, so the rendered FAQ and its schema stay clean")

        self.body_html, self.images = markdown_to_html(body_md, where)
        self.word_count = len(re.findall(r"\b[\w'’-]+\b", re.sub(r"<[^>]+>", " ", self.body_html)))
        self.reading_time = max(1, round(self.word_count / WORDS_PER_MINUTE))

    # image paths are conventional, not configurable — the generator owns them
    @property
    def cover(self) -> str:
        return f"/images/blog/{self.slug}.png"

    @property
    def all_images(self) -> list[str]:
        """Cover plus every inline image — everything needing a WebP sibling."""
        return [self.cover] + [s for s in self.images if s.startswith("/")]

    @property
    def url(self) -> str:
        return f"{SITE}/blog/{self.slug}/"

    @property
    def date_long(self) -> str:
        return f"{self.date.day} {MONTHS[self.date.month - 1]} {self.date.year}"

    @property
    def date_short(self) -> str:
        return f"{self.date.day} {MONTHS[self.date.month - 1][:3]} {self.date.year}"

    @property
    def rfc822(self) -> str:
        d = self.date
        wd = WEEKDAYS[datetime(d.year, d.month, d.day).weekday()]
        return f"{wd}, {d.day:02d} {MONTHS[d.month - 1][:3]} {d.year} 08:00:00 +0000"


def load_posts() -> list[Post]:
    if not POSTS_DIR.is_dir():
        raise BuildError("posts/ directory not found")
    posts = [Post(p) for p in sorted(POSTS_DIR.glob("*.md"))]
    live = [p for p in posts if not p.draft]
    if not live:
        raise BuildError("no publishable posts found in posts/")
    seen: dict[str, str] = {}
    for p in live:
        key = p.title.lower()
        if key in seen:
            raise BuildError(f"{p.where}: duplicate title, already used by {seen[key]}")
        seen[key] = p.where
    live.sort(key=lambda p: (p.date, p.slug), reverse=True)
    return live


def validate_references(posts: list[Post]) -> list[str]:
    """Cross-post checks: images on disk, related slugs, internal links."""
    problems: list[str] = []
    slugs = {p.slug for p in posts}
    for p in posts:
        if not (ROOT / p.cover.lstrip("/")).exists():
            problems.append(f"{p.where}: cover image {p.cover} does not exist — generate it "
                            f"with comfy-gen and copy it there (see prompt.md §6)")
        for src in p.images:
            if src.startswith("/") and not (ROOT / src.lstrip("/")).exists():
                problems.append(f"{p.where}: inline image {src} does not exist")
        # Every image has to have its WebP sibling, or the page silently goes
        # back to serving an ~800 KB PNG to every visitor.
        for src in p.all_images:
            if (ROOT / src.lstrip("/")).exists() and not webp_for(src):
                problems.append(f"{p.where}: {src} has no .webp sibling — run "
                                f"`python3 tools/optimize-images.py` (see prompt.md §6)")
        for slug in p.related:
            if slug not in slugs:
                problems.append(f"{p.where}: related slug {slug!r} is not a published post")
            if slug == p.slug:
                problems.append(f"{p.where}: related lists the post itself")
        internal_links = 0
        for href in re.findall(r'href="([^"]*)"', p.body_html):
            # Anchors, mail, and full external URLs are fine as-is.
            if href.startswith(("#", "mailto:", "https://", "http://")):
                continue
            # Everything else must be an absolute in-site path. A link like
            # `@blog/…/` or `blog/…/` (a missing or mistyped leading slash) is a
            # broken internal link the old check skipped because it only looked
            # at hrefs already starting with `/` — one shipped exactly that.
            if not href.startswith("/"):
                problems.append(f"{p.where}: link href {href!r} is neither an absolute in-site "
                                f"path (/…) nor a full URL — likely a typo (e.g. `@blog/…` or a "
                                f"missing leading slash); use /blog/<slug>/")
                continue
            m = re.fullmatch(r"/blog/([a-z0-9-]+)/", href)
            if m and m.group(1) not in slugs:
                problems.append(f"{p.where}: links to /blog/{m.group(1)}/ which does not exist")
            elif not m and href != "/" and not (ROOT / href.lstrip("/").split("#")[0]).exists():
                problems.append(f"{p.where}: links to {href} which is not a file in this site")
            if m and m.group(1) in slugs and m.group(1) != p.slug:
                internal_links += 1
        # Every post must earn its place in the cluster: link to a sibling post
        # in the body, not only via the auto "Keep reading" cards. One run shipped
        # with zero inline links — cheap to require, real SEO + reader value.
        if len(posts) > 1 and internal_links < 1:
            problems.append(f"{p.where}: no inline link to another post in the body — link to at "
                            f"least one related /blog/<slug>/ where it's genuinely relevant (§4)")
        # The soft nudge has to actually exist: at least one natural in-body
        # mention of the app, and no more than two (the template adds the CTA).
        mentions = len(re.findall(r"SnapDeck", re.sub(r"<[^>]+>", "", p.body_html)))
        if mentions < 1:
            problems.append(f"{p.where}: the body never mentions SnapDeck AI — include exactly one "
                            f"natural mention where the app is the honest tool for the job (§2)")
        elif mentions > 2:
            problems.append(f"{p.where}: SnapDeck AI is mentioned {mentions}x in the body — the "
                            f"nudge budget is one (two at the very most); trim it (§2)")
        if p.word_count < MIN_WORDS:
            problems.append(f"{p.where}: only {p.word_count} words (minimum {MIN_WORDS})")
        # Snippets and People Also Ask boxes are won by a heading that asks the
        # question the reader typed, answered directly underneath it. A body of
        # headings like "The short version" cannot compete for either.
        headings = re.findall(r"<h2>(.*?)</h2>", p.body_html, re.S)
        questions = [h for h in headings if h.strip().endswith("?")]
        if len(questions) < MIN_QUESTION_HEADINGS:
            problems.append(
                f"{p.where}: only {len(questions)} of {len(headings)} H2s are phrased as a "
                f"question (need {MIN_QUESTION_HEADINGS}) — rewrite the sections that answer "
                f"a real question so the heading asks it (§4)")
        # A post that cites nothing is a post an answer engine paraphrases
        # instead of citing.
        if not p.sources:
            problems.append(f"{p.where}: no sources: block — link the primary research behind "
                            f"the claims about memory, attention or habit (§4)")
        if p.hero and not p.cover_alt:
            problems.append(f"{p.where}: hero: true needs coverAlt — the image is shown in the "
                            f"article and screen readers read that text aloud")
    return problems


# --- rendering -------------------------------------------------------------

def attr(text: str) -> str:
    """Escape for an attribute value or for text content.

    Deliberately not html.escape(quote=True): that turns every apostrophe into
    &#x27;, which is correct but makes the source of a page full of contractions
    unreadable. Attributes here are always double-quoted, so escaping `"` is
    enough.
    """
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))


def indent(block: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + ln if ln.strip() else "" for ln in block.split("\n"))


def card(p: Post, heading: str, extra_class: str = "", excerpt: str | None = None,
         more: bool = False) -> str:
    cls = f"post-card {extra_class}".strip()
    body = [
        f'<article class="{cls}">',
        '  <div class="post-card-media">',
        picture(p.cover, "", indent_by=4, loading="lazy"),
        '  </div>',
        '  <div class="post-card-body">',
        f'    <p class="post-meta"><span class="tag">{p.tag}</span>'
        f'<time datetime="{p.date.isoformat()}">{p.date_short}</time>'
        f'<span class="dot" aria-hidden="true"></span>{p.reading_time} min read</p>',
        f'    <{heading} class="post-card-title">'
        f'<a href="/blog/{p.slug}/">{attr(p.title)}</a></{heading}>',
        f'    <p class="post-card-excerpt">{attr(excerpt if excerpt is not None else p.excerpt)}</p>',
    ]
    if more:
        body.append('    <span class="post-card-more">Read it →</span>')
    body += ['  </div>', '</article>']
    return "\n".join(body)


def faq_html(p: Post) -> str:
    if not p.faq:
        return ""
    rows = ["", '        <section class="post-faq">',
            '          <h2>Common questions</h2>']
    for entry in p.faq:
        rows.append('          <details class="post-faq-item">')
        rows.append(f'            <summary>{attr(entry["question"])}</summary>')
        rows.append(f'            <p>{inline(entry["answer"])}</p>')
        rows.append('          </details>')
    rows.append('        </section>')
    return "\n".join(rows) + "\n"


def faq_jsonld(p: Post) -> str:
    if not p.faq:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": e["question"],
             "acceptedAnswer": {"@type": "Answer", "text": e["answer"]}}
            for e in p.faq
        ],
    }
    body = json.dumps(data, indent=2, ensure_ascii=False)
    return ('\n  <script type="application/ld+json">\n'
            + indent(body, 2) + "\n  </script>\n")


def answer_html(p: Post) -> str:
    """The extractable answer, directly under the H1 and above the fold."""
    return (f'<div class="answer">\n'
            f'            <p><strong>Short answer:</strong> {inline(p.answer)}</p>\n'
            f'          </div>')


def sources_html(p: Post) -> str:
    if not p.sources:
        return ""
    rows = ["", '        <section class="post-sources">',
            '          <h2>Sources</h2>', '          <ul>']
    for s in p.sources:
        rows.append(f'            <li><a href="{attr(str(s["url"]))}" rel="noopener" '
                    f'target="_blank">{attr(str(s["title"]))}</a></li>')
    rows += ['          </ul>', '        </section>']
    return "\n".join(rows) + "\n"


def howto_jsonld(p: Post) -> str:
    if not p.howto:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": p.howto_name,
        "description": p.answer,
        "step": [{"@type": "HowToStep", "position": i, "name": s["name"], "text": s["text"]}
                 for i, s in enumerate(p.howto, start=1)],
    }
    return ('\n  <script type="application/ld+json">\n'
            + indent(json.dumps(data, indent=2, ensure_ascii=False), 2) + "\n  </script>\n")


def author_jsonld() -> str:
    """The Person block, shared by the Article author and the About page."""
    return json.dumps({
        "@type": "Person",
        "name": AUTHOR["name"],
        "jobTitle": AUTHOR["role"],
        "url": AUTHOR["url"],
        "worksFor": {"@type": "Organization", "name": PUBLISHER["name"],
                     "url": PUBLISHER["url"], "sameAs": SAME_AS},
    }, indent=2, ensure_ascii=False)


def publisher_jsonld() -> str:
    return json.dumps({
        "@type": "Organization",
        "name": PUBLISHER["name"],
        "url": PUBLISHER["url"],
        "sameAs": SAME_AS,
        "logo": {"@type": "ImageObject", "url": PUBLISHER["logo"]},
    }, indent=2, ensure_ascii=False)


def citation_jsonld(p: Post) -> str:
    """`citation` on the Article — the machine-readable half of the Sources list."""
    if not p.sources:
        return "[]"
    return json.dumps(
        [{"@type": "CreativeWork", "name": s["title"], "url": s["url"]} for s in p.sources],
        indent=2, ensure_ascii=False)


def hero_html(p: Post) -> str:
    if not p.hero:
        return ""
    # fetchpriority="high" is right for the LCP element — but only now that it
    # points at a ~30 KB WebP instead of an ~800 KB PNG.
    return ("\n        <figure class=\"article-hero\">\n"
            + picture(p.cover, p.cover_alt, indent_by=10,
                      fetchpriority="high", decoding="async") + "\n"
            "        </figure>\n")


def render_post(p: Post, posts: list[Post], template: str) -> str:
    related = [q for q in posts if q.slug in p.related]
    if not related:                                   # default: the newest others
        related = [q for q in posts if q.slug != p.slug][:2]
    cards = "\n\n".join(indent(card(q, "h3", excerpt=q.teaser_excerpt), 12)
                        for q in related[:2])

    values = {
        "META_TITLE": attr(p.meta_title),
        "DESCRIPTION": attr(p.description),
        "URL": p.url,
        "SITE": SITE,
        "COVER": p.cover,
        "OG_TITLE": attr(p.og_title),
        "OG_DESCRIPTION": attr(p.og_description),
        "TWITTER_DESCRIPTION": attr(p.twitter_description),
        "DATE": p.date.isoformat(),
        "DATE_MODIFIED": p.modified.isoformat(),
        "DATE_LONG": p.date_long,
        "TAG": p.tag,
        "TITLE": attr(p.title),
        "LEDE": inline(p.lede),
        "READING_TIME": str(p.reading_time),
        "WORD_COUNT": str(p.word_count),
        "JSON_TITLE": json.dumps(p.title, ensure_ascii=False),
        "JSON_DESCRIPTION": json.dumps(p.description, ensure_ascii=False),
        "JSON_KEYWORDS": json.dumps(p.keywords, ensure_ascii=False),
        "BODY": indent(p.body_html, 10),
        "HERO": hero_html(p),
        "ANSWER": answer_html(p),
        "JSON_ANSWER": json.dumps(p.answer, ensure_ascii=False),
        "SOURCES_HTML": sources_html(p),
        "CITATION_JSONLD": indent(citation_jsonld(p), 4).lstrip(),
        "HOWTO_JSONLD": howto_jsonld(p),
        "AUTHOR_JSONLD": indent(author_jsonld(), 4).lstrip(),
        "PUBLISHER_JSONLD": indent(publisher_jsonld(), 4).lstrip(),
        "AUTHOR_NAME": attr(AUTHOR["name"]),
        "AUTHOR_ROLE": attr(AUTHOR["role"]),
        "AUTHOR_URL": AUTHOR["url"],
        "FAQ_HTML": faq_html(p),
        "FAQ_JSONLD": faq_jsonld(p),
        "RELATED": cards,
    }
    out = template
    for key, value in values.items():
        out = out.replace("{{" + key + "}}", value)
    leftover = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if leftover:
        raise BuildError(f"template placeholder(s) never filled: {sorted(set(leftover))}")
    return out


# --- marker-delimited regions ---------------------------------------------

def replace_region(path: Path, name: str, new_body: str) -> str:
    text = path.read_text(encoding="utf-8")
    start, end = f"BLOG:{name}:START", f"BLOG:{name}:END"
    pattern = re.compile(
        rf"(^[^\n]*{re.escape(start)}[^\n]*\n)(.*?)(^[^\n]*{re.escape(end)}[^\n]*$)",
        re.S | re.M)
    m = pattern.search(text)
    if not m:
        raise BuildError(f"{path.relative_to(ROOT)}: missing {start} / {end} markers")
    return text[:m.start(2)] + new_body + text[m.end(2):]


def replace_section(path: Path, heading: str, new_body: str) -> str:
    """Replace everything under a markdown heading, up to the next same-level one.

    Used for llms.txt / llms-full.txt, where an HTML comment marker would be
    visible to the very readers those files exist for.
    """
    text = path.read_text(encoding="utf-8")
    level = len(heading) - len(heading.lstrip("#"))
    pattern = re.compile(rf"(^{re.escape(heading)}[^\n]*\n)(.*?)(?=^#{{1,{level}}} |\Z)",
                         re.S | re.M)
    m = pattern.search(text)
    if not m:
        raise BuildError(f"{path.relative_to(ROOT)}: no {heading!r} section found")
    return text[:m.start(2)] + new_body + text[m.end(2):]


def write(path: Path, content: str, check: bool, changed: list[str]) -> None:
    rel = str(path.relative_to(ROOT))
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return
    changed.append(rel)
    if not check:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# --- the derived files -----------------------------------------------------

def build_feed(posts: list[Post]) -> str:
    items = []
    for p in posts:
        items.append(f"""    <item>
      <title>{attr(p.title)}</title>
      <link>{p.url}</link>
      <guid isPermaLink="true">{p.url}</guid>
      <pubDate>{p.rfc822}</pubDate>
      <category>{p.tag}</category>
      <description>{attr(p.description)}</description>
    </item>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>SnapDeck AI Blog</title>
    <link>{SITE}/blog/</link>
    <description>Study tips, memory science and exam prep for students — from the team behind SnapDeck AI.</description>
    <language>en</language>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>{posts[0].rfc822}</lastBuildDate>

{chr(10).join(items)}

  </channel>
</rss>
"""


def build_sitemap(posts: list[Post]) -> str:
    """The whole sitemap, not just the post block.

    It used to be a fenced region inside a hand-written file, which meant / and
    /blog/ kept a lastmod of 2026-07-22 for a month while the homepage teaser
    and the blog index changed with every post. Both are derived from the post
    set, so both are generated now.
    """
    newest = max(p.modified for p in posts).isoformat()

    def row(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
        return (f"  <url>\n    <loc>{SITE}{loc}</loc>\n"
                f"    <lastmod>{lastmod}</lastmod>\n"
                f"    <changefreq>{changefreq}</changefreq>\n"
                f"    <priority>{priority}</priority>\n  </url>\n")

    rows = []
    for loc, lastmod, changefreq, priority in STATIC_URLS:
        rows.append(row(loc, lastmod or newest, changefreq, priority))
        if loc == "/blog/":
            for p in posts:
                rows.append(row(f"/blog/{p.slug}/", p.modified.isoformat(), "yearly", "0.7"))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!-- Generated by tools/build.py — do not hand-edit. '
            'Add hand-written pages to STATIC_URLS there. -->\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(rows) + "</urlset>\n")


LLMS_BLOG_INTRO = (
    "\nStudy advice for students, published at {SITE}/blog/ "
    "(RSS: {SITE}/feed.xml).\n\n")
LLMS_FULL_BLOG_INTRO = (
    "\nThe SnapDeck AI blog publishes practical study advice for students at {SITE}/blog/ "
    "(RSS feed: {SITE}/feed.xml). Posts are tagged `study-tips`, `memory-science` or "
    "`exam-prep`.\n\n")


def build_llms_region(posts: list[Post]) -> str:
    # llms.txt is the index — one line per post. The full summary belongs in
    # llms-full.txt, so take only the opening sentence here.
    rows = [f"- [{p.title}]({p.url}) — {p.tag}, {p.date.isoformat()}. "
            f"{p.summary.split('. ')[0].rstrip('.')}."
            for p in posts]
    return LLMS_BLOG_INTRO.format(SITE=SITE) + "\n".join(rows) + "\n\n"


def build_llms_full_region(posts: list[Post]) -> str:
    rows = [f"### {p.title} ({p.date.isoformat()}, {p.tag})\n{p.url}\n{p.summary}\n"
            for p in posts]
    return LLMS_FULL_BLOG_INTRO.format(SITE=SITE) + "\n".join(rows) + "\n"


def build_blog_index_region(posts: list[Post]) -> str:
    return "\n\n".join(indent(card(p, "h2", "fade-in", more=True), 10) for p in posts) + "\n"


def build_blog_schema_region(posts: list[Post]) -> str:
    """The Blog / blogPost JSON-LD on the index. Regenerated so it can never
    drift from the actual post set (it listed deleted posts, and never picked up
    ones the weekly job added)."""
    items = ",\n".join(
        f"""      {{
        "@type": "BlogPosting",
        "headline": {json.dumps(p.title, ensure_ascii=False)},
        "url": "{p.url}",
        "datePublished": "{p.date.isoformat()}",
        "dateModified": "{p.modified.isoformat()}",
        "author": {{ "@type": "Person", "name": {json.dumps(AUTHOR["name"])},
                     "url": "{AUTHOR["url"]}" }},
        "image": "{SITE}{p.cover}"
      }}""" for p in posts)
    return f"""  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Blog",
    "name": "SnapDeck AI Blog",
    "description": "Study tips, memory science and exam prep for students.",
    "url": "{SITE}/blog/",
    "author": {indent(author_jsonld(), 4).lstrip()},
    "publisher": {indent(publisher_jsonld(), 4).lstrip()},
    "blogPost": [
{items}
    ]
  }}
  </script>
"""


def build_teaser_region(posts: list[Post]) -> str:
    return "\n\n".join(indent(card(p, "h3", "fade-in", excerpt=p.teaser_excerpt, more=True), 10)
                       for p in posts[:3]) + "\n"


# --- main ------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true",
                    help="validate and report what would change; write nothing")
    args = ap.parse_args()

    try:
        posts = load_posts()
    except BuildError as e:
        print(f"ERROR  {e}", file=sys.stderr)
        return 1

    problems = validate_references(posts)
    if problems:
        for p in problems:
            print(f"ERROR  {p}", file=sys.stderr)
        return 1

    template = TEMPLATE.read_text(encoding="utf-8")
    changed: list[str] = []
    try:
        for p in posts:
            write(BLOG_DIR / p.slug / "index.html", render_post(p, posts, template),
                  args.check, changed)
        write(ROOT / "feed.xml", build_feed(posts), args.check, changed)
        write(BLOG_DIR / "index.html",
              replace_region(BLOG_DIR / "index.html", "CARDS", build_blog_index_region(posts)),
              args.check, changed)
        write(BLOG_DIR / "index.html",
              replace_region(BLOG_DIR / "index.html", "SCHEMA", build_blog_schema_region(posts)),
              args.check, changed)
        write(ROOT / "index.html",
              replace_region(ROOT / "index.html", "TEASER", build_teaser_region(posts)),
              args.check, changed)
        write(ROOT / "sitemap.xml", build_sitemap(posts), args.check, changed)
        write(ROOT / "llms.txt",
              replace_section(ROOT / "llms.txt", "## Blog", build_llms_region(posts)),
              args.check, changed)
        write(ROOT / "llms-full.txt",
              replace_section(ROOT / "llms-full.txt", "## Blog", build_llms_full_region(posts)),
              args.check, changed)
    except BuildError as e:
        print(f"ERROR  {e}", file=sys.stderr)
        return 1

    stale = {d.name for d in BLOG_DIR.iterdir() if d.is_dir()} - {p.slug for p in posts}
    for slug in sorted(stale):
        print(f"WARN   blog/{slug}/ has no posts/{slug}.md — delete it or restore the source")

    verb = "would change" if args.check else "wrote"
    if changed:
        for rel in changed:
            print(f"  {verb}  {rel}")
    print(f"BUILD OK — {len(posts)} post(s), {len(changed)} file(s) {verb}"
          + (" (check only)" if args.check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
