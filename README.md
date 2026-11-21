# pmu-beautify

An [Agent Skill](https://agentskills.io) for **Claude Code, OpenAI Codex, Gemini CLI, Cursor** and other agents that read `SKILL.md` skills. It retouches skin in **photos and videos** for permanent-makeup (PMU) studios: lines, blotches and under-eye texture go down, pores stay, and **brows, eyes, lips and the PMU work are never touched**.

🇮🇹 [Italiano più sotto](#italiano)

## Install

**Any agent — one command** (asks which agents and whether to install for all your projects):

```bash
npx skills add dibeja/pmu-beautify
```

**Or by hand** — clone into your agent's skills folder:

| Agent | Command |
|---|---|
| Claude Code | `git clone https://github.com/dibeja/pmu-beautify ~/.claude/skills/pmu-beautify` |
| Codex, Gemini CLI, Cursor | `git clone https://github.com/dibeja/pmu-beautify ~/.agents/skills/pmu-beautify` |

**Or ask your agent:** *"Install the skill from https://github.com/dibeja/pmu-beautify"* (in Codex you can also use `$skill-installer`).

**Zip:** download `pmu-beautify.zip` from [Releases](https://github.com/dibeja/pmu-beautify/releases/latest) and unzip it into the skills folder above.

Then restart your agent.

## First use

Just ask: *"beautify this photo: ~/Desktop/client.jpg"*. On the first run the skill installs what it needs (macOS only):

- [Homebrew](https://brew.sh) — must be there already; if not, the skill gives you the one command to paste (it asks for your Mac password)
- ffmpeg and Python 3.12 (via Homebrew)
- a private Python environment in `~/.pmu-beautify/` with mediapipe, opencv, numpy
- two face models (~42 MB): [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) and [OpenCV SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface)

To remove everything: delete the `pmu-beautify` folder from your agent's skills folder and `~/.pmu-beautify`.

## What you can ask

- retouch a photo or a video (or just a segment of it)
- protect the PMU (`guard`): eyeliner and lip line stay exactly as they are — the default on clients
- retouch only one person in a group photo/video
- slim jaw/chin a little, whiten teeth (only if you ask)
- a side-by-side **before/after** image or video for approval (optional)

**Rule:** the skill refuses to retouch the treated area of a result (brows, lips, eyeliner, areola). Retouching the work is misleading advertising.

---

## Italiano

[Agent Skill](https://agentskills.io) per **Claude Code, OpenAI Codex, Gemini CLI, Cursor** e gli altri agenti che leggono le skill `SKILL.md`. Ritocca la pelle in **foto e video** per studi di trucco permanente (PMU): rughe, macchie e occhiaie si attenuano, i pori restano, e **sopracciglia, occhi, labbra e il lavoro PMU non vengono mai toccati**.

### Installazione

**Qualsiasi agente — un comando** (chiede per quali agenti e se installarla per tutti i progetti):

```bash
npx skills add dibeja/pmu-beautify
```

**Oppure a mano** — clona nella cartella skill del tuo agente:

| Agente | Comando |
|---|---|
| Claude Code | `git clone https://github.com/dibeja/pmu-beautify ~/.claude/skills/pmu-beautify` |
| Codex, Gemini CLI, Cursor | `git clone https://github.com/dibeja/pmu-beautify ~/.agents/skills/pmu-beautify` |

**Oppure chiedilo al tuo agente:** *"Installa la skill da https://github.com/dibeja/pmu-beautify"* (in Codex puoi usare anche `$skill-installer`).

**Zip:** scarica `pmu-beautify.zip` dalle [Releases](https://github.com/dibeja/pmu-beautify/releases/latest) e scompattalo nella cartella skill indicata sopra.

Poi riavvia l'agente.

### Primo utilizzo

Chiedi e basta: *"ritocca la pelle in questa foto: ~/Desktop/cliente.jpg"*. Alla prima esecuzione la skill installa ciò che serve (solo macOS):

- [Homebrew](https://brew.sh) — deve esserci già; se manca, la skill ti dà il comando da incollare (chiede la password del Mac)
- ffmpeg e Python 3.12 (con Homebrew)
- un ambiente Python dedicato in `~/.pmu-beautify/` con mediapipe, opencv, numpy
- due modelli per il volto (~42 MB): [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) e [OpenCV SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface)

Per rimuovere tutto: cancella la cartella `pmu-beautify` dalla cartella skill del tuo agente e `~/.pmu-beautify`.

### Cosa puoi chiedere

- ritoccare una foto o un video (anche solo un pezzo)
- proteggere il PMU (`guard`): eyeliner e contorno labbra restano identici — di default sulle clienti
- ritoccare una sola persona in una foto/video di gruppo
- snellire leggermente mascella/mento, sbiancare i denti (solo se lo chiedi)
- un confronto **prima/dopo** affiancato, foto o video, per l'approvazione (opzionale)

**Regola:** la skill si rifiuta di ritoccare la zona trattata di un risultato (sopracciglia, labbra, eyeliner, areola). Ritoccare il lavoro è pubblicità ingannevole.

## License

MIT — see [LICENSE](LICENSE). The face models are downloaded from their original sources under their own licenses.
