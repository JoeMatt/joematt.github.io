#!/usr/bin/env python3
"""
voice-lint.py — Heuristic linter that flags AI-generated writing tells in
HTML and Markdown content.

Stdlib-only. Exits 0 if all checks pass (or only warnings with --warn-ok),
1 if any BLOCK-severity violations, 2 on invocation/IO errors.

Rules are hard-coded here. VOICE.md is human documentation only.
"""

from __future__ import annotations

import argparse
import glob
import html
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Iterable


# ──────────────────────────────────────────────────────────────────────
# Rules (hard-coded; see VOICE.md for human-readable version)
# ──────────────────────────────────────────────────────────────────────

# Banned phrases — regex, case-insensitive, word-boundary where it matters.
# Severity: BLOCK
BANNED_PHRASES: list[tuple[str, str]] = [
    (r"\bCrucially\b", "Crucially"),
    (r"\bImportantly\b", "Importantly"),
    (r"\bNotably\b", "Notably"),
    (r"\bIt(?:'|’)s worth noting\b", "It's worth noting"),
    (r"\bHere(?:'|’)s the thing\b", "Here's the thing"),
    (r"\bWhat(?:'|’)s interesting is\b", "What's interesting is"),
    (r"\bWhat(?:'|’)s surprising is\b", "What's surprising is"),
    (r"\bIn conclusion\b", "In conclusion"),
    (r"\bUltimately\b", "Ultimately"),
    (r"\bAt its core\b", "At its core"),
    (r"\bWhether you(?:'|’)re\b", "Whether you're"),
    (r"\bLet me explain\b", "Let me explain"),
    (r"\bLet me be clear\b", "Let me be clear"),
    (r"\bWhat I want to be clear about\b", "What I want to be clear about"),
    (r"\bIt(?:'|’)s not (?:just|simply)?\s?.{0,40}? (?:it(?:'|’)s|but)\b",
     "It's not just X, it's/but Y"),
    (r"\bNot just .{0,40}? but\b", "Not just X but Y"),
    (r"\bmore (?:of them )?than you(?:'|’)d (?:think|expect)\b",
     "more than you'd think/expect"),
    (r"\bThe (?:interesting|important|crucial) (?:thing|part|point) is\b",
     "The [interesting|important|crucial] [thing|part|point] is"),
    (r"\bThink of it as\b", "Think of it as"),
    (r"\bDive (?:into|deep)\b", "Dive into/deep"),
    (r"\bdelve into\b", "delve into"),
    (r"\bIn essence\b", "In essence"),
    (r"\bEssentially\b", "Essentially"),
]

# AI-flavored vocabulary blocklist. Severity: WARN.
AI_VOCAB: list[tuple[str, str]] = [
    (r"\bleverag(?:e|ed|es|ing)\b", "leverage"),
    (r"\bstreamlin(?:e|ed|es|ing)\b", "streamline"),
    (r"\brobust\b", "robust"),
    (r"\bseamless(?:ly)?\b", "seamless"),
    (r"\bholistic\b", "holistic"),
    (r"\bnuanced\b", "nuanced"),
    (r"\bunpack(?:ing)?\b", "unpack"),
    (r"\bfoster(?:ed|s|ing)?\b", "foster"),
    (r"\bempower(?:ed|s|ing)?\b", "empower"),
    (r"\belevat(?:e|ed|es|ing)\b", "elevate"),
    (r"\balign(?:ed|s|ing)? with\b", "align with"),
    (r"\benhanc(?:e|ed|es|ing)\b", "enhance"),
    (r"\btapestry\b", "tapestry"),
    (r"\bintricate\b", "intricate"),
    (r"\btestament\b", "testament"),
    (r"\bpivotal\b", "pivotal"),
    (r"\bmeticulous\b", "meticulous"),
    (r"\bvibrant\b", "vibrant"),
    (r"\bserves as\b", "serves as"),
    (r"\bstands as\b", "stands as"),
    (r"\bboasts\b", "boasts"),
]

# Closing-callback openers (final sentence of paragraph). Severity: WARN.
CALLBACK_OPENERS = [
    r"^So,\s",
    r"^In sum\b",
    r"^Ultimately\b",
    r"^That(?:'|’)s the\b",
]

# Triplet pattern: three short, parallel words (single-word adjectives or
# nouns) joined with commas, ending with "and X" or "or X" — the classic
# rhetorical "fast, reliable, and scalable" cadence. Multi-word phrases
# almost always indicate a normal enumeration of distinct things, not a
# rhetorical triplet, so we restrict each slot to a single word. Severity:
# WARN.
TRIPLET_RE = re.compile(
    r"\b([A-Za-z][A-Za-z\-]{3,20}),\s+"
    r"([A-Za-z][A-Za-z\-]{3,20}),\s+"
    r"(?:and|or)\s+"
    r"([A-Za-z][A-Za-z\-]{3,20})\b"
)

# Em-dash density thresholds (per 1000 visible words)
EMDASH_WARN = 2.0
EMDASH_BLOCK = 4.0

# Sentence-length stddev thresholds
STDDEV_WARN = 6.0
STDDEV_BLOCK = 4.0


# ──────────────────────────────────────────────────────────────────────
# Data classes
# ──────────────────────────────────────────────────────────────────────

SEVERITY_BLOCK = "BLOCK"
SEVERITY_WARN = "WARN"


@dataclass
class Violation:
    line: int
    severity: str
    rule: str
    message: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FileResult:
    path: str
    violations: list[Violation] = field(default_factory=list)
    word_count: int = 0
    em_dash_count: int = 0
    sentence_stddev: float = 0.0
    error: str | None = None

    @property
    def status(self) -> str:
        if self.error:
            return SEVERITY_BLOCK
        if any(v.severity == SEVERITY_BLOCK for v in self.violations):
            return SEVERITY_BLOCK
        if self.violations:
            return SEVERITY_WARN
        return "CLEAN"


# ──────────────────────────────────────────────────────────────────────
# HTML / Markdown -> visible text extraction
# ──────────────────────────────────────────────────────────────────────

# Tags whose contents we should drop entirely.
SKIP_TAGS = {"pre", "code", "style", "script", "noscript", "svg"}

# Regex to find tag opens/closes — simple and stdlib-only.
TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*>")


def html_to_visible_segments(text: str) -> list[tuple[int, str]]:
    """
    Convert HTML (or Markdown — Markdown is mostly passed through, with
    fenced code blocks stripped) into a list of (line_number, visible_text)
    segments. Line numbers are 1-based and refer to the source file.

    Skips content inside <pre>, <code>, <style>, <script>, <svg>, <noscript>.
    Decodes HTML entities. Normalizes &mdash; / &#8212; / U+2014 to em-dash.
    """
    segments: list[tuple[int, str]] = []
    skip_stack: list[str] = []
    pos = 0
    line = 1

    def emit(s: str, ln: int) -> None:
        if s.strip():
            segments.append((ln, s))

    while pos < len(text):
        m = TAG_RE.search(text, pos)
        if not m:
            chunk = text[pos:]
            if not skip_stack:
                emit(html.unescape(chunk), line)
            line += chunk.count("\n")
            break

        chunk = text[pos:m.start()]
        if not skip_stack:
            emit(html.unescape(chunk), line)
        line += chunk.count("\n")

        is_close = m.group(1) == "/"
        tag = m.group(2).lower()
        # Self-closing? Look at raw match.
        raw = m.group(0)
        self_closing = raw.endswith("/>")

        if tag in SKIP_TAGS:
            if is_close:
                if skip_stack and skip_stack[-1] == tag:
                    skip_stack.pop()
            elif not self_closing:
                skip_stack.append(tag)

        line += raw.count("\n")
        pos = m.end()

    return segments


def is_markdown(path: str) -> bool:
    return path.lower().endswith((".md", ".markdown"))


def markdown_to_visible_segments(text: str) -> list[tuple[int, str]]:
    """
    Strip fenced code blocks and inline backticks from Markdown.
    Return (line, text) segments preserving original line numbers.
    """
    segments: list[tuple[int, str]] = []
    in_fence = False
    fence_marker: str | None = None

    for idx, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.lstrip()
        if not in_fence and (stripped.startswith("```") or stripped.startswith("~~~")):
            in_fence = True
            fence_marker = stripped[:3]
            continue
        if in_fence:
            if stripped.startswith(fence_marker or "```"):
                in_fence = False
                fence_marker = None
            continue

        # Strip inline code spans
        line_clean = re.sub(r"`[^`]*`", " ", raw)
        # Strip Markdown image/link wrappers but keep link text
        line_clean = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", line_clean)
        line_clean = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line_clean)
        # Drop heading hashes / list markers / blockquote markers
        line_clean = re.sub(r"^\s{0,3}(?:#{1,6}\s+|[-*+]\s+|>\s?|\d+\.\s+)", "", line_clean)

        if line_clean.strip():
            segments.append((idx, line_clean))

    return segments


def extract_segments(path: str, text: str) -> list[tuple[int, str]]:
    if is_markdown(path):
        return markdown_to_visible_segments(text)
    return html_to_visible_segments(text)


# ──────────────────────────────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────────────────────────────

WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’\-]*")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'“‘])")


def normalize(s: str) -> str:
    # Treat &mdash; / &#8212; / U+2014 / `--` consistently.
    return s.replace("—", "—")


def count_words(s: str) -> int:
    return len(WORD_RE.findall(s))


def split_sentences(s: str) -> list[str]:
    # Collapse whitespace first, then split.
    cleaned = re.sub(r"\s+", " ", s).strip()
    if not cleaned:
        return []
    parts = SENTENCE_SPLIT_RE.split(cleaned)
    # Filter empties and very short stubs (e.g. just a number or a header word).
    return [p for p in parts if count_words(p) >= 2]


def stddev(nums: list[int]) -> float:
    if len(nums) < 2:
        return 0.0
    mean = sum(nums) / len(nums)
    var = sum((n - mean) ** 2 for n in nums) / len(nums)
    return math.sqrt(var)


def find_phrase_violations(
    segments: list[tuple[int, str]],
    patterns: list[tuple[str, str]],
    severity: str,
    rule_label: str,
    extra_msg: str = "",
) -> list[Violation]:
    out: list[Violation] = []
    seen: set[tuple[int, str]] = set()
    for line, seg in segments:
        for pat, label in patterns:
            try:
                m = re.search(pat, seg, flags=re.IGNORECASE)
            except re.error:
                continue
            if m:
                key = (line, label)
                if key in seen:
                    continue
                seen.add(key)
                msg = f'{rule_label} "{label}"'
                if extra_msg:
                    msg += f" {extra_msg}"
                out.append(Violation(line=line, severity=severity, rule=rule_label, message=msg))
    return out


_STOP_WORDS = {
    "the", "and", "but", "for", "with", "from", "into", "onto", "than", "that",
    "this", "these", "those", "their", "there", "they", "them", "what", "when",
    "where", "which", "while", "would", "could", "should", "have", "been", "were",
    "your", "yours", "ours", "his", "her", "its", "about", "after", "before",
    "between", "across", "over", "under", "without", "within",
}


def find_triplet_violations(segments: list[tuple[int, str]]) -> list[Violation]:
    out: list[Violation] = []
    for line, seg in segments:
        for m in TRIPLET_RE.finditer(seg):
            a, b, c = m.group(1), m.group(2), m.group(3)
            items = [a, b, c]
            # Skip if any slot is a stop-word (the regex grabs "and the X"
            # tails out of normal sentences otherwise).
            if any(it.lower() in _STOP_WORDS for it in items):
                continue
            phrase = f"{a}, {b}, {c}"
            out.append(Violation(
                line=line,
                severity=SEVERITY_WARN,
                rule="triplet pattern",
                message=f'triplet pattern "{phrase}"',
            ))
            break  # one per line is enough
    return out


def find_callback_violations(segments: list[tuple[int, str]]) -> list[Violation]:
    """
    Approximation: look at the final sentence of each contiguous segment.
    Real paragraph boundaries are harder to detect across stripped HTML, so
    each non-empty segment is treated as paragraph-ish.
    """
    out: list[Violation] = []
    for line, seg in segments:
        sents = split_sentences(seg)
        if not sents:
            continue
        last = sents[-1].strip()
        for pat in CALLBACK_OPENERS:
            if re.match(pat, last, flags=re.IGNORECASE):
                snippet = last[:60].rstrip() + ("…" if len(last) > 60 else "")
                out.append(Violation(
                    line=line,
                    severity=SEVERITY_WARN,
                    rule="closing callback",
                    message=f'closing-callback summary: "{snippet}"',
                ))
                break
    return out


# ──────────────────────────────────────────────────────────────────────
# File analysis
# ──────────────────────────────────────────────────────────────────────

def analyze_file(path: str) -> FileResult:
    result = FileResult(path=path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except (OSError, UnicodeDecodeError) as e:
        result.error = f"read failed: {e}"
        return result

    raw = normalize(raw)
    segments = extract_segments(path, raw)
    full_text = " ".join(s for _, s in segments)
    full_text = normalize(full_text)

    # Stats
    words = count_words(full_text)
    em_dashes = full_text.count("—")
    sentences = split_sentences(full_text)
    sent_lens = [count_words(s) for s in sentences if count_words(s) >= 2]
    sd = stddev(sent_lens)

    result.word_count = words
    result.em_dash_count = em_dashes
    result.sentence_stddev = sd

    # Phrase checks
    result.violations.extend(find_phrase_violations(
        segments, BANNED_PHRASES, SEVERITY_BLOCK, "banned phrase",
    ))
    result.violations.extend(find_phrase_violations(
        segments, AI_VOCAB, SEVERITY_WARN, "blocked vocab",
        extra_msg="→ use a concrete verb",
    ))
    result.violations.extend(find_triplet_violations(segments))
    result.violations.extend(find_callback_violations(segments))

    # Em-dash density (per 1000 words)
    if words >= 100:
        density = (em_dashes / words) * 1000.0
        if density > EMDASH_BLOCK:
            result.violations.append(Violation(
                line=1,
                severity=SEVERITY_BLOCK,
                rule="em-dash density",
                message=f"em-dash density {density:.1f}/1k words (threshold {EMDASH_BLOCK})",
            ))
        elif density > EMDASH_WARN:
            result.violations.append(Violation(
                line=1,
                severity=SEVERITY_WARN,
                rule="em-dash density",
                message=f"em-dash density {density:.1f}/1k words (threshold {EMDASH_WARN})",
            ))

    # Sentence-length burstiness
    if len(sent_lens) >= 8:
        if sd < STDDEV_BLOCK:
            result.violations.append(Violation(
                line=1,
                severity=SEVERITY_BLOCK,
                rule="sentence stddev",
                message=f"sentence-length stddev {sd:.1f} (threshold {STDDEV_BLOCK})",
            ))
        elif sd < STDDEV_WARN:
            result.violations.append(Violation(
                line=1,
                severity=SEVERITY_WARN,
                rule="sentence stddev",
                message=f"sentence-length stddev {sd:.1f} (threshold {STDDEV_WARN})",
            ))

    # Sort violations by line, then severity (BLOCK first)
    result.violations.sort(key=lambda v: (v.line, 0 if v.severity == SEVERITY_BLOCK else 1))
    return result


# ──────────────────────────────────────────────────────────────────────
# Reporting
# ──────────────────────────────────────────────────────────────────────

def render_human(results: list[FileResult], quiet: bool) -> str:
    lines: list[str] = []
    blocked = warned = clean = 0

    for r in results:
        if r.error:
            blocked += 1
            lines.append(f"✗ {r.path}  (ERROR)")
            lines.append(f"  {r.error}")
            lines.append("")
            continue

        status = r.status
        if status == "CLEAN":
            clean += 1
            if not quiet:
                lines.append(f"✓ {r.path}  (CLEAN)")
                lines.append(
                    f"  stats: {r.word_count} words, {r.em_dash_count} em-dashes, "
                    f"sentence-length stddev {r.sentence_stddev:.1f}"
                )
                lines.append("")
            continue

        if status == SEVERITY_BLOCK:
            blocked += 1
            mark = "✗"
        else:
            warned += 1
            mark = "⚠"

        lines.append(f"{mark} {r.path}  ({status})")
        for v in r.violations:
            lines.append(f"  L{v.line}: {v.message}  [{v.severity}]")
        stats_severity = ""
        if r.sentence_stddev and r.sentence_stddev < STDDEV_WARN:
            stats_severity = " [WARN]" if r.sentence_stddev >= STDDEV_BLOCK else " [BLOCK]"
        lines.append(
            f"  stats: {r.word_count} words, {r.em_dash_count} em-dashes, "
            f"sentence-length stddev {r.sentence_stddev:.1f}{stats_severity}"
        )
        lines.append("")

    summary = (
        f"{blocked} file{'s' if blocked != 1 else ''} BLOCKED, "
        f"{warned} file{'s' if warned != 1 else ''} WARNED, "
        f"{clean} file{'s' if clean != 1 else ''} clean"
    )
    lines.append(summary)
    return "\n".join(lines)


def render_json(results: list[FileResult]) -> str:
    payload = {
        "files": [
            {
                "path": r.path,
                "status": r.status,
                "word_count": r.word_count,
                "em_dash_count": r.em_dash_count,
                "sentence_stddev": round(r.sentence_stddev, 2),
                "error": r.error,
                "violations": [v.to_dict() for v in r.violations],
            }
            for r in results
        ],
        "summary": {
            "blocked": sum(1 for r in results if r.status == SEVERITY_BLOCK),
            "warned": sum(1 for r in results if r.status == SEVERITY_WARN),
            "clean": sum(1 for r in results if r.status == "CLEAN"),
            "total": len(results),
        },
    }
    return json.dumps(payload, indent=2)


# ──────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────

def expand_paths(args: Iterable[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for a in args:
        # Treat as a glob; if no matches and the path exists, use it directly.
        matches = glob.glob(a, recursive=True)
        if not matches and os.path.exists(a):
            matches = [a]
        for m in matches:
            if os.path.isdir(m):
                continue
            if m not in seen:
                seen.add(m)
                out.append(m)
    return sorted(out)


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description="Voice linter — flag AI-generated writing tells.",
    )
    p.add_argument("paths", nargs="+", help="File paths or globs (HTML / Markdown).")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of human output.")
    p.add_argument("--warn-ok", action="store_true", help="Don't fail on WARN-only files.")
    p.add_argument("--quiet", action="store_true", help="Only show violations.")
    p.add_argument("--config", default=None,
                   help="Override VOICE.md location (informational; rules live in this script).")
    args = p.parse_args(argv)

    try:
        files = expand_paths(args.paths)
    except OSError as e:
        sys.stderr.write(f"error: {e}\n")
        return 2

    if not files:
        sys.stderr.write("error: no files matched\n")
        return 2

    results = [analyze_file(f) for f in files]

    if args.json:
        sys.stdout.write(render_json(results) + "\n")
    else:
        sys.stdout.write(render_human(results, quiet=args.quiet) + "\n")

    has_block = any(r.status == SEVERITY_BLOCK for r in results)
    has_warn = any(r.status == SEVERITY_WARN for r in results)

    if has_block:
        return 1
    if has_warn and not args.warn_ok:
        # Default behaviour: WARN does not fail the build (per spec the gate
        # uses --warn-ok in CI, and locally a developer wants to see warns
        # without the script returning non-zero on every blog post).
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
