# Voice profile — joemattiello.dev

This file is the human-readable companion to `scripts/voice-lint.py`. The
linter's rules are hard-coded in the script; this document explains the
voice the linter is trying to protect, with samples and counter-examples.

If something here disagrees with the script, the script wins for the gate
and this file should be updated to match.

## Voice profile

How Joe writes, in 7 bullets:

- **Concrete first.** Lead with the artifact, the version, the bug
  number, the chip. Abstractions come after the specifics, if at all.
- **Short paragraphs, varied sentences.** Mix one-line statements
  ("Single-author push to master.") with longer technical passages.
  Sentence-length stddev sits in the 11–18 range.
- **Plain verbs.** "fixes", "ships", "boots", "wires up", "rewrote".
  Not "leverages", "streamlines", "enables", "facilitates".
- **No throat-clearing.** Skip "Importantly,", "Crucially,",
  "It's worth noting,". If it's worth noting, just note it.
- **Receipts over claims.** Numbers, file paths, PR links, commit hashes,
  benchmarks measured against a baseline. "~2x on the hot paths,
  profile-driven and measured against v2.1 on the same hardware."
- **Em-dashes are fine, in moderation.** Joe uses them, but not as a
  substitute for a period or a colon every paragraph. The linter caps
  density at ~4 per 1000 words.
- **Endings are flat, not summative.** Posts end on the next concrete
  thing, not on a "Ultimately, this shows..." recap.

## Hard rules (BLOCK — fails CI)

1. **Banned phrases.** Word-boundary, case-insensitive matches on the
   list in `scripts/voice-lint.py` (`BANNED_PHRASES`). Examples:
   `Crucially`, `Importantly`, `Notably`, `It's worth noting`,
   `Here's the thing`, `In conclusion`, `Ultimately`, `At its core`,
   `Whether you're`, `Let me explain`, `delve into`, `In essence`,
   `Essentially`, plus the rhetorical templates
   `It's not just X, it's Y` / `Not just X but Y` /
   `more than you'd think` / `The interesting thing is` /
   `Think of it as` / `Dive into`.
2. **Em-dash density > 4.0 per 1000 visible words.** Real human
   technical writing rarely exceeds this. AI prose routinely does.
3. **Sentence-length stddev < 4.0** (over a sample of at least 8
   sentences). AI tends to write metronomically; humans don't.

## Soft rules (WARN — surfaced, doesn't fail CI by default)

1. **AI vocabulary.** `leverage`, `streamline`, `robust`, `seamless`,
   `holistic`, `nuanced`, `unpack`, `foster`, `empower`, `elevate`,
   `align with`, `enhance`, `tapestry`, `intricate`, `testament`,
   `pivotal`, `meticulous`, `vibrant`, `serves as`, `stands as`,
   `boasts`. Replace with a concrete verb.
2. **Em-dash density > 2.0 per 1000 words.**
3. **Sentence-length stddev < 6.0.**
4. **Triplet pattern.** Three short, parallel words joined with commas
   and "and"/"or" — `fast, reliable, and scalable`. The classic AI
   cadence. Real lists of three distinct concrete things (chips,
   features, file paths) don't trip this rule.
5. **Closing-callback summary.** Final sentence of a paragraph that
   starts with `So,`, `In sum`, `Ultimately`, or `That's the` — flagged
   because AI loves to recap a paragraph it just wrote.

## Voice samples

Pulled from the v2.2.0 release post and recent PR descriptions. These
are what passing content reads like.

> The Atari Jaguar shipped in 1993, sold ~250k units, and ended Atari's
> run as a hardware maker. Most modern users have never legally booted
> one. The real BIOS image isn't on Archive.org, isn't in any of the big
> ROM sets, and Atari's successor companies have never released it.

> v2.2.0 takes a third path. It re-implements the BIOS at the function
> level. Any cart ROM boots, the emulator runs the same init steps the
> real BIOS would have run, hardware lands in the same state, control
> passes to the game. No copyrighted file ever touches the user's
> machine.

> Single-author push to master. That's how a small project moves when
> there's nobody to wait on.

> The frame-edge dropout bug has been in the core since at least 2014.
> Symptom: every few seconds, a brief click or half-sample of silence
> right at the audio-frame boundary. Not catastrophic but enough to make
> extended sessions unpleasant. The diagnostic took longer than the fix.

> I wasn't chasing performance in this release. I was chasing
> correctness. Several of the correctness fixes turned out to also be
> much faster than what they replaced.

Notice what these have in common: dates, numbers, file paths, specific
chip names, plain verbs, sentences of wildly different lengths, no
throat-clearing, no recap.

## Don't do this

Phrases that show up in AI-flavored prose. The linter catches all of
these; the explanations below are for humans deciding what to write
instead.

- **"Crucially, the new BIOS implementation..."** → just say it.
  "The new BIOS implementation..." carries the same weight without
  signaling that you're about to say something Important.
- **"At its core, virtualjaguar is..."** → "virtualjaguar is..." Drop
  the philosophical framing.
- **"It's not just an emulator, it's a..."** → describe what it is.
  The contrast frame is filler.
- **"Whether you're a homebrew dev or a speedrunner..."** → talk about
  the actual feature. Audience-flattery openers don't earn their space.
- **"This release leverages a robust, holistic approach to..."** →
  "This release does X by Y." Verbs not adjectives.
- **"Dive into the v2.2.0 changelog to unpack..."** → "v2.2.0
  highlights:" + bullets.
- **"In conclusion, v2.2.0 represents a pivotal moment..."** → end on
  the next concrete thing, not on a recap.
- **"Fast, reliable, and scalable."** → pick the one that's actually
  load-bearing for the reader and explain it.

## Running the linter locally

```bash
# Single file
python3 scripts/voice-lint.py static-site/blog/your-post/index.html

# Glob
python3 scripts/voice-lint.py 'static-site/blog/**/*.html'

# JSON for tooling
python3 scripts/voice-lint.py --json static-site/blog/your-post/index.html

# CI mode (warnings don't fail; only BLOCK fails)
python3 scripts/voice-lint.py --warn-ok 'static-site/**/*.html'
```

Exit codes: `0` clean (or warnings only with `--warn-ok`), `1` BLOCK,
`2` invocation/IO error.
