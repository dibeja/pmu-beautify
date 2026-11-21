---
name: pmu-beautify
description: Face-aware skin retouch ("beauty" / "beautify" pass) for photos and videos of permanent-makeup (PMU) artists and their clients — smooths lines, blotches and under-eye texture while keeping pores, and never touches brows, eyes, lips or the PMU work itself. Optional before/after comparison, jaw slim, teeth whitening, and retouching only one chosen person in a group shot. Has a help page and a step-by-step wizard. Use whenever the user wants to beautify, retouch, smooth skin, soften wrinkles on a face in a photo or a video (reel, story, testimonial, talking head), in any language, even if they only drop a file and say "make her skin nicer", or asks "pmu-beautify help" / "how does pmu-beautify work". macOS and Windows.
---

# pmu-beautify

Skin retouch for photos and video, built for PMU (permanent makeup) studios: the skin gets cleaner, the tattooed work stays exactly as it is.

Always talk to the user in their language. Keep option names (`--guard` etc.) out of what you say unless they ask: describe the effect instead.

## Help and wizard

- **Help** — the user writes `pmu-beautify help` (or just `help` while using the skill), asks how it works or what they can ask: show [HELP.md](HELP.md) translated into their language, then offer the wizard.
- **Wizard** — the user writes `pmu-beautify wizard` or asks to be guided step by step, or invokes the skill without a file or without saying who is in it: ask the questions below **one at a time**, waiting for each answer, skipping any the user already answered. Then say in one line what you will do and run it.
  1. **File** — which photo or video? (path, or drag it into the chat)
  2. **Who is in it** — the artist (the user) / a client wearing PMU / more than one person? If more than one: retouch one of them, or each of them? Then confirm who is who (e.g. "the artist is the one in the apron, 0–11 s?") and whether each wears PMU. The reference moments are found by you (see "More than one person"); ask for a separate photo of a person only when they are never alone in the shot. Questions 3 and 4 may then be answered per person.
  3. **Strength** — subtle / natural (recommended) / strong → `--amount 0.4 / 0.6 / 0.8`
  4. **Extras** — none (recommended) / slimmer jaw / whiter teeth / both
  5. **Video only: which part** — whole video, or from second X for Y seconds?
  6. **Comparison** — also make a before/after side-by-side? If yes, the two labels in their language.

## First run: install what is missing

Before the first retouch, check for the `.ready` file in the pmu-beautify home: `~/.pmu-beautify/.ready` on macOS, `%USERPROFILE%\.pmu-beautify\.ready` on Windows (or `$PMU_BEAUTIFY_HOME/.ready` if that variable is set). If it is missing, run the setup for the user's system:

```bash
bash <this skill's folder>/scripts/setup.sh                                          # macOS
powershell -ExecutionPolicy Bypass -File "<this skill's folder>\scripts\setup.ps1"   # Windows
```

It installs ffmpeg and Python 3.12 (Homebrew on macOS, winget on Windows), a private venv (mediapipe, opencv, numpy) and two face models (~42 MB, SHA-256 checked). It is safe to re-run. Exit codes:
- **2** — the package manager is missing (Homebrew on macOS, winget on Windows): show the user what the script printed (Homebrew needs their Mac password, so they run it themselves), then run setup again.
- **4** (Windows) — something was installed but is not on PATH yet: ask the user to open a new terminal / restart the agent, then run setup again.

The Windows setup has not been tested on a real Windows machine yet: if a step fails, show the user the exact error and fix the step rather than guessing.

Every command below uses:
- macOS: `PY=~/.pmu-beautify/venv/bin/python`, `S=<this skill's folder>/scripts`
- Windows: `PY=%USERPROFILE%\.pmu-beautify\venv\Scripts\python.exe`, `S=<this skill's folder>\scripts` (quote paths with spaces)

## The rule that is never broken

**Never retouch the treated area of a client's result** (brows, lip blush, eyeliner, areola, scar camouflage). Retouching the work is misleading advertising. The mask already leaves brows, eyes and lips out; on anyone wearing PMU always add `--guard 0.06`, which widens those protected zones so eyeliner and lip-liner stay untouched. If the user asks to smooth the treated area itself, say no and explain why.

## Retouch

Photo in → photo out, video in → `.mp4` out. Pick the output extension from the input: a photo (`.jpg .jpeg .png .heic .webp .tif`) gets `.jpg` (or `.png` if the input was PNG); a video gets `.mp4`. Never overwrite the original: write next to it as `<name>-beautify.<ext>`.

```bash
$PY $S/retouch.py IN OUT --guard 0.06            # client with PMU: the default
$PY $S/retouch.py IN OUT                         # the artist's own face, no PMU near the eyes/lips
$PY $S/retouch.py IN.mp4 OUT.mp4 --ss 12 --t 8   # only a segment of a video
```

| Option | What it does | Default / good value |
|---|---|---|
| `--amount` | how much line/blotch detail is removed (0..1) | 0.6 natural; 0.4 subtle; >0.8 looks plastic |
| `--even` | evens out redness/shine patches | 0.1; above 0.2 the cheeks lose colour |
| `--guard` | widens protected brow/eye/lip zones (fraction of face width) | 0 own face; **0.06 with PMU** |
| `--slim` | narrows jaw, lifts chin (nose never touched) | off; 0.02–0.03 max, it also warps hair/collar near the jaw |
| `--teeth` | takes yellow out of teeth only | off; 0.5 natural |
| `--ref SEC` | video: only the person alone in frame at SEC (seconds into the span) is retouched | — |
| `--ref-image PHOTO` | photo or video: only the person shown alone in PHOTO is retouched | — |
| `--debug-mask` | writes the mask (white = retouched) instead of the result | use to check |

Use `--ref` / `--ref-image` whenever more than one face is in the shot (artist + client, two friends): without it, only the most prominent face is found and the others may get the mask. Check with `--debug-mask` when unsure. The script prints how many frames lost the face; if that is high, tell the user.

### More than one person

One run retouches one face. To retouch several people, run **one pass per person, chained**: pass 1 reads the original and writes a temporary file; pass 2 reads that and writes the final output; and so on. Each pass has its own reference and its own settings: `--guard 0.06` only for a person wearing PMU, no guard for the artist's own face.

```bash
$PY $S/retouch.py IN.mp4 TMP.mp4 --ref 0.5               # pass 1: the artist, alone at 0.5 s
$PY $S/retouch.py TMP.mp4 OUT.mp4 --ref 40 --guard 0.06  # pass 2: the client with PMU, alone at 40 s
```

1. **Find the reference moments yourself.** Sample a frame every few seconds (ffmpeg), count the faces in each and look at a contact sheet to see who is where. Pick, for each person, a moment where they are alone, facing the camera, with no hand over the face. If a person is never alone, ask the user for a separate photo of them alone and use `--ref-image`.
2. **Confirm who is who** with the user before running ("the client is the one in the blue shirt, from 12 s?").
3. **Check each pass's last line.** The frames it retouched (total minus "face missed") should match roughly the time that person is on screen, and "other faces left alone" should match the time the others are. A big mismatch means a wrong reference: pick another moment.
4. Write temporary files in a scratch/temp folder and delete them at the end. Make the before/after comparison against the **original**, not against an intermediate file.

Each pass re-encodes the video at high quality (CRF 15): two or three passes show no visible loss.

Slim and teeth are only applied when the user asks for them.

MediaPipe prints `W0000`/`I0000`/`INFO` lines on stderr at start: harmless, ignore them. The last stdout line (`N frames, face missed in M`) is the one that matters.

Light and colour are not changed by this skill.

## Before/after comparison (optional)

Only when the user asks for it (offer it once after the retouch, e.g. "want a side-by-side to approve?"):

```bash
$PY $S/compare.py BEFORE AFTER OUT --labels "ORIGINAL,RETOUCHED"
```

Photo pair → `.jpg`, video pair → `.mp4` (audio from BEFORE). Labels in the user's language, ASCII only (no accents): e.g. `"BEFORE,AFTER"` translated. If `--ss/--t` was used for the retouch, compare against the same segment of the original (cut it first with ffmpeg), not the full clip.

## Check before handing over

Look at the result (for a video, extract a frame with ffmpeg) and check the eyes and lips: eyeliner, lip line and brows must be identical to the original. Then tell the user the output path and the settings used, in plain words.
