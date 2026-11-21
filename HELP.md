# pmu-beautify — help

**What it does.** Smooths the skin in a photo or video: fine lines, blotches, redness and under-eye texture go down, pores and natural texture stay, so the face does not look plastic. Brows, eyes, lips and any permanent makeup are never touched. Light and colour are not changed.

**What you need.** A photo (JPG, PNG, HEIC from iPhone, WEBP) or a video (MP4, MOV) where the face is visible. Close-ups shot sideways or with the face cut off may not be recognised.

**What you can ask** (in your own words, any language):

- *"Retouch this photo: ~/Desktop/anna.jpg"* — natural retouch, PMU protected
- *"Retouch this video, only from second 10 to 18"*
- *"Very subtle retouch"* / *"a bit stronger"*
- *"It's me in the video, I'm not wearing PMU"* — retouch closer to eyes and lips
- *"There are two of us: retouch only me"* — the other person is left exactly as is
- *"Also slim the jaw a little"* / *"whiten the teeth"* — only if you ask
- *"Make a before/after to show the client"* — side-by-side photo or video with labels
- *"Show me what gets retouched"* — the mask, white = retouched area
- *"Guide me"* / *"wizard"* — I ask you one question at a time

**What it will not do.** It will not smooth or change the treated area of a result (brows, lips, eyeliner, areola). Retouching the work itself is misleading advertising.

**Where the result goes.** Next to the original, named `<name>-beautify.jpg` or `.mp4`. The original is never overwritten.

**First time.** The first run installs the tools it needs (ffmpeg, Python, two small face models, ~42 MB, plus Python packages). This takes a few minutes once; after that it starts right away.
