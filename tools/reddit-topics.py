#!/usr/bin/env python3
"""reddit-topics.py — what students are actually asking, right now.

Feeds the weekly blog job (see prompt.md) with real reader demand instead of
whatever the model imagines students worry about.

    python3 tools/reddit-topics.py                 # ranked digest, ~60 lines
    python3 tools/reddit-topics.py --json          # same data, machine-readable
    python3 tools/reddit-topics.py --refresh       # ignore the cache

WHY RSS AND NOT THE JSON API: reddit.com/r/<sub>/top.json returns 403 to both a
datacenter IP and a home IP now — it is the reason the sister sites (home-stories,
event-stories) gave up on live scraping and baked a static topic bank instead.
The Atom feed at /r/<sub>/top/.rss is still served, so that is what this uses.
It is rate-limited though: hammer it and you get 429s, which is why requests are
paced, retried with backoff, and cached to .cache/ for a day.

WHY A SCRIPT AND NOT A FEW CURL COMMANDS IN THE BRIEF: the Hermes agent's
terminal blocks `-c` / `-e` flags, so `python3 -c '...'` and clever one-liners
fail at runtime with BLOCKED. And raw feeds are ~50 KB each — twenty of them
would bury the model's context. A plain command that prints a small digest
survives both constraints.

Failure is not fatal: if every feed fails, this exits 2 having printed a clear
message, and the brief falls back to the ranked topic bank in prompt.md.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "reddit-topics"

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
ATOM = {"a": "http://www.w3.org/2005/Atom"}

# Where students ask study questions. Ordered roughly by signal-to-noise: the
# first few are almost entirely "how do I study" questions, the later ones are
# broader communities where study posts are a subset.
SUBREDDITS = [
    "GetStudying", "studytips", "StudyMotivation", "college", "UniUK",
    "Students", "GradSchool", "StudentNurse", "premed", "APStudents",
    "Anki", "medicalschool", "productivity", "GetMotivated",
]
WINDOWS = ["month", "year"]

# Theme buckets. A title can land in several; each is counted once per theme.
# Keep these lowercase and substring-matched — cheap, and good enough to rank.
THEMES: dict[str, tuple[str, list[str]]] = {
    "focus-and-distraction": ("Focus, attention span and phone distraction", [
        "focus", "concentrat", "distract", "attention span", "phone", "zone out",
        "wandering", "stay on task", "doomscroll", "social media"]),
    "procrastination": ("Procrastination and not being able to start", [
        "procrastinat", "cant start", "can't start", "keep putting", "put off",
        "avoid studying", "lazy", "get myself to", "force myself"]),
    "motivation-and-burnout": ("Motivation, discipline and burnout", [
        "motivat", "burnout", "burn out", "discipline", "give up", "no energy",
        "exhaust", "lost interest", "dont care", "don't care", "consistent"]),
    "memory-and-retention": ("Remembering things and forgetting them again", [
        "memoriz", "memoris", "remember", "forget", "forgot", "retain",
        "retention", "recall", "long term memory", "sticks"]),
    "flashcards-and-srs": ("Flashcards, Anki and spaced repetition", [
        "flashcard", "anki", "quizlet", "spaced repetition", "srs"]),
    "note-taking": ("Note-taking systems and what to do with notes", [
        "notes", "note taking", "note-taking", "cornell", "obsidian", "notion",
        "handwritten", "ipad", "goodnotes", "annotat"]),
    "exam-prep": ("Exam revision, finals and the last stretch", [
        "exam", "final", "midterm", "revision", "revise", "test prep",
        "study for a test", "mock"]),
    "cramming-and-deadlines": ("Cramming, all-nighters and running out of time", [
        "cram", "all nighter", "all-nighter", "last minute", "one day",
        "tomorrow", "night before", "behind on", "catch up"]),
    "planning-and-time": ("Planning, schedules and time management", [
        "schedule", "timetable", "time management", "plan", "pomodoro",
        "routine", "how many hours", "study plan", "balance"]),
    "study-technique": ("Which study method actually works", [
        "technique", "method", "how to study", "study smarter", "feynman",
        "highlight", "rereading", "re-reading", "passive", "efficient",
        "active recall", "self-test", "self test", "quiz myself"]),
    "reading-and-textbooks": ("Textbooks, readings and lecture material", [
        "textbook", "reading", "chapter", "slides", "lecture note", "pdf",
        "syllabus", "handout"]),
    "anxiety-and-overwhelm": ("Stress, exam anxiety and overwhelm", [
        "anxiety", "anxious", "stress", "panic", "overwhelm", "mental health",
        "depress", "pressure", "scared"]),
    "sleep-and-health": ("Sleep, caffeine and studying while wrecked", [
        "sleep", "tired", "caffeine", "coffee", "nap", "insomnia", "energy",
        "eating", "exercise"]),
    "grades-and-failing": ("Grades, failing and recovering from a bad one", [
        "gpa", "grade", "failed", "failing", "flunk", "pass", "retake",
        "dropped", "bad marks"]),
    "ai-and-tools": ("AI tools and study apps", [
        "chatgpt", " ai ", "ai to", "using ai", "app", "tool", "software",
        "notebooklm"]),
    "environment-and-habits": ("Study space, habits and consistency", [
        "habit", "environment", "desk", "study space", "library", "at home",
        "setup", "every day", "streak"]),
    "hard-subjects": ("Maths, science and other brick-wall subjects", [
        "math", "calculus", "physics", "chemistry", "formula", "problem set",
        "coding", "statistic", "anatomy", "organic"]),
    "language-and-vocab": ("Vocabulary, languages and terminology", [
        "vocabulary", "vocab", "language", "kanji", "conjugat", "terminology",
        "definitions"]),
    "group-study": ("Studying with other people", [
        "study group", "study partner", "study buddy", "together", "teach someone",
        "explain to"]),
}

# Titles that are jokes, screenshots, progress-pics or venting. They dominate
# /top and tell us nothing about what to write.
NOISE = [
    "haha", "lol", "lmao", "meme", "rate my", "my setup", "study with me",
    "day in the life", "just graduated", "i did it", "finally done", "passed!",
    "wish me luck", "guess the", "who else", "relatable", "me when", "pov",
    "study vlog", "progress", "aesthetic", "desk tour", "before and after",
]
QUESTION_WORDS = [
    "how", "what", "why", "when", "which", "anyone", "does", "do you", "should",
    "tips", "advice", "help", "is it", "can i", "any way", "best way", "struggl",
    "cant", "can't", "trouble", "problem", "recommend",
]


def cache_path(sub: str, window: str) -> Path:
    return CACHE / f"{sub}-{window}.xml"


def read_cache(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def save_cache(path: Path, body: str, verbose: bool) -> None:
    """Best effort. A read-only checkout must not cost us a fetched feed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    except OSError as e:
        if verbose:
            print(f"  (cache not written: {e.__class__.__name__})", file=sys.stderr)


def fetch(sub: str, window: str, pace: float, ttl: int, refresh: bool,
          verbose: bool, deadline: float) -> tuple[str | None, bool]:
    """Return (xml, from_cache). None means this feed is unavailable.

    Reddit rate-limits anonymous RSS hard — 429 is the normal response to any
    enthusiasm — so requests are paced, backed off, and finally given up on.
    Progress goes to stderr on every feed: a scheduled run is killed after 600s
    of silence, and the backoffs alone can exceed that.
    """
    path = cache_path(sub, window)
    if not refresh and path.exists() and (time.time() - path.stat().st_mtime) < ttl:
        cached = read_cache(path)
        if cached:
            if verbose:
                print(f"  r/{sub:<16} [{window}] cached", file=sys.stderr)
            return cached, True

    url = f"https://www.reddit.com/r/{sub}/top/.rss?t={window}"
    for attempt in range(4):
        if time.time() > deadline:
            if verbose:
                print(f"  r/{sub:<16} [{window}] skipped (time budget spent)", file=sys.stderr)
            break
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA,
                                                       "Accept": "application/atom+xml"})
            with urllib.request.urlopen(req, timeout=25) as r:
                body = r.read().decode("utf-8", "replace")
            save_cache(path, body, verbose)
            if verbose:
                print(f"  r/{sub:<16} [{window}] ok", file=sys.stderr)
            time.sleep(pace)
            return body, False
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                wait = 30 * (attempt + 1)
                if verbose:
                    print(f"  r/{sub:<16} [{window}] {e.code} — waiting {wait}s",
                          file=sys.stderr)
                time.sleep(min(wait, max(0.0, deadline - time.time())))
                continue
            if verbose:
                print(f"  r/{sub:<16} [{window}] unavailable (HTTP {e.code})", file=sys.stderr)
            break
        except Exception as e:                                    # network, DNS, timeout
            if verbose:
                print(f"  r/{sub:<16} [{window}] unavailable ({type(e).__name__})",
                      file=sys.stderr)
            break

    stale = read_cache(path) if path.exists() else None            # stale beats nothing
    if stale:
        if verbose:
            print(f"  r/{sub:<16} [{window}] using stale cache", file=sys.stderr)
        return stale, True
    return None, False


def titles_from(xml: str) -> list[str]:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:
        return []
    out = []
    for entry in root.findall("a:entry", ATOM):
        node = entry.find("a:title", ATOM)
        if node is not None and node.text:
            out.append(re.sub(r"\s+", " ", node.text).strip())
    return out


def is_useful(title: str) -> bool:
    low = title.lower()
    if len(title) < 20:
        return False
    if any(n in low for n in NOISE):
        return False
    # Emoji-and-caps venting posts carry no query intent.
    if sum(c.isupper() for c in title) > len(title) * 0.6:
        return False
    return any(w in low for w in QUESTION_WORDS) or "?" in title


def themes_of(title: str) -> list[str]:
    low = f" {title.lower()} "
    return [key for key, (_, words) in THEMES.items() if any(w in low for w in words)]


def covered_themes() -> dict[str, list[str]]:
    """Map theme -> [slugs] for themes an existing post already addresses.

    Matched against the title and keywords only. Matching the whole frontmatter
    was tried first and marked nearly every theme as covered — a summary that
    mentions sleep in passing is not a post about sleep, and suppressing a good
    topic on that basis is the expensive mistake here.
    """
    out: dict[str, list[str]] = {}
    posts_dir = ROOT / "posts"
    if not posts_dir.is_dir():
        return out
    for path in sorted(posts_dir.glob("*.md")):
        head = path.read_text(encoding="utf-8")[:3000].split("\n---", 1)[0]
        subject = " ".join(
            line.split(":", 1)[1] for line in head.split("\n")
            if line.split(":", 1)[0].strip() in ("title", "keywords") and ":" in line
        )
        for key in themes_of(f"{subject} {path.stem.replace('-', ' ')}"):
            out.setdefault(key, []).append(path.stem)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--subs", help="comma-separated subreddits (default: the student set)")
    ap.add_argument("--windows", default=",".join(WINDOWS), help="top windows: month,year")
    ap.add_argument("--pace", type=float, default=8.0, help="seconds between requests")
    ap.add_argument("--max-seconds", type=float, default=600.0,
                    help="total time budget; stops fetching and reports what it has")
    ap.add_argument("--ttl", type=int, default=20 * 3600, help="cache lifetime in seconds")
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    ap.add_argument("--themes", type=int, default=8, help="how many themes to report")
    ap.add_argument("--examples", type=int, default=3, help="example titles per theme")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--quiet", action="store_true", help="no progress on stderr")
    a = ap.parse_args()

    subs = [s.strip() for s in (a.subs.split(",") if a.subs else SUBREDDITS) if s.strip()]
    windows = [w.strip() for w in a.windows.split(",") if w.strip()]
    verbose = not a.quiet

    if verbose:
        print(f"Reading {len(subs)} subreddits x {len(windows)} windows "
              f"(~{a.pace:.0f}s apart, cached {a.ttl // 3600}h, "
              f"{a.max_seconds:.0f}s budget)...", file=sys.stderr)

    deadline = time.time() + a.max_seconds
    seen: set[str] = set()
    entries: list[tuple[str, str, int]] = []          # (title, sub, rank)
    ok = cached = failed = 0
    for sub in subs:
        for window in windows:
            xml, from_cache = fetch(sub, window, a.pace, a.ttl, a.refresh, verbose, deadline)
            if xml is None:
                failed += 1
                continue
            ok += 1
            cached += 1 if from_cache else 0
            for rank, title in enumerate(titles_from(xml)):
                key = re.sub(r"[^a-z0-9]+", "", title.lower())[:60]
                if key in seen:
                    continue
                seen.add(key)
                entries.append((title, sub, rank))

    if not entries:
        print("reddit-topics: every feed failed (Reddit is blocking or offline).\n"
              "Fall back to the ranked topic bank in prompt.md — that is expected "
              "and fine.", file=sys.stderr)
        return 2

    useful = [(t, s, r) for t, s, r in entries if is_useful(t)]
    covered = covered_themes()

    buckets: dict[str, dict] = {}
    for title, sub, rank in useful:
        for key in themes_of(title):
            b = buckets.setdefault(key, {"key": key, "label": THEMES[key][0],
                                         "count": 0, "weight": 0.0,
                                         "titles": [], "covered_by": covered.get(key, [])})
            b["count"] += 1
            b["weight"] += 1.0 / (rank + 3)           # higher in /top = stronger demand
            b["titles"].append(title)

    ranked = sorted(buckets.values(), key=lambda b: (b["weight"], b["count"]), reverse=True)
    for b in ranked:
        b["weight"] = round(b["weight"], 2)
        b["titles"] = sorted(b["titles"], key=len)[-a.examples * 3:][::-1][:a.examples]

    fresh_themes = [b for b in ranked if not b["covered_by"]]
    done_themes = [b for b in ranked if b["covered_by"]]

    if a.as_json:
        print(json.dumps({
            "feeds_ok": ok, "feeds_failed": failed, "feeds_from_cache": cached,
            "posts_seen": len(entries), "posts_useful": len(useful),
            "themes": ranked,
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"REDDIT DEMAND — {ok} feeds ({cached} cached, {failed} unavailable), "
          f"{len(entries)} posts, {len(useful)} carrying a real question")
    print()
    print(f"UNCOVERED THEMES — strongest demand first")
    if not fresh_themes:
        print("  (every theme is already covered — write a fresher angle on a top one)")
    for i, b in enumerate(fresh_themes[:a.themes], 1):
        print(f"{i:2}. {b['label']}  [{b['key']}]  {b['count']} posts, weight {b['weight']}")
        for t in b["titles"]:
            print(f"      · {t[:110]}")
    print()
    print("ALREADY COVERED")
    for b in done_themes[:8]:
        print(f"  - {b['label']} ({b['count']}) → {', '.join(sorted(set(b['covered_by'])))}")
    print()
    print("TOP QUESTION TITLES VERBATIM — the reader's own words, use them")
    on_topic = [e for e in useful if themes_of(e[0])]
    for title, sub, rank in sorted(on_topic, key=lambda e: e[2])[:15]:
        print(f"  · [r/{sub}] {title[:110]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
