---
name: pmu-beautify
description: Face-aware skin retouch ("beauty" / "beautify" pass) for photos and videos of permanent-makeup (PMU) artists and their clients — smooths lines, blotches and under-eye texture while keeping pores, and never touches brows, eyes, lips or the PMU work itself. Optional before/after comparison, jaw slim, teeth whitening, and retouching only one chosen person in a group shot. Use whenever the user wants to beautify, retouch, smooth skin, "ritocca la pelle", "fai il beauty", "bőrretus", soften wrinkles on a face in a photo or a video (reel, story, testimonial, talking head), even if they only drop a file and say "make her skin nicer". macOS only.
---

# pmu-beautify

Skin retouch for photos and video, built for PMU (permanent makeup) studios: the skin gets cleaner, the tattooed work stays exactly as it is.

## First run: install what is missing

Before the first retouch, check for `~/.pmu-beautify/.ready` (or `$PMU_BEAUTIFY_HOME/.ready`). If it is missing, run:

```bash
bash <this skill's folder>/scripts/setup.sh
```

It installs ffmpeg and Python 3.12 with Homebrew, a private venv in `~/.pmu-beautify/venv` (mediapipe, opencv, numpy) and two face models (~42 MB, SHA-256 checked). It is safe to re-run. If it exits with code 2, Homebrew is missing: show the user the command the script printed (it needs their Mac password, so they run it themselves), then run setup again.

Every command below uses `PY=~/.pmu-beautify/venv/bin/python` and `S=<this skill's folder>/scripts`.

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

Slim and teeth are only applied when the user asks for them.

MediaPipe prints `W0000`/`I0000`/`INFO` lines on stderr at start: harmless, ignore them. The last stdout line (`N frames, face missed in M`) is the one that matters.

Light and colour are not changed by this skill.

## Before/after comparison (optional)

Only when the user asks for it (offer it once after the retouch, e.g. "want a side-by-side to approve?"):

```bash
$PY $S/compare.py BEFORE AFTER OUT --labels "ORIGINAL,RETOUCHED"
```

Photo pair → `.jpg`, video pair → `.mp4` (audio from BEFORE). Labels in the user's language, ASCII only (no accents): e.g. `"PRIMA,DOPO"`, `"ELOTTE,UTANA"`. If `--ss/--t` was used for the retouch, compare against the same segment of the original (cut it first with ffmpeg), not the full clip.

## Check before handing over

Open (Read) the result or a frame of it and look at the eyes and lips: eyeliner, lip line and brows must be identical to the original. Then tell the user the output path and the settings used.
