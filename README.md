# pmu-beautify

An [Agent Skill](https://agentskills.io) for **Claude Code, OpenAI Codex, Gemini CLI, Cursor** and other agents that read `SKILL.md` skills, on **macOS and Windows**. It retouches skin in **photos and videos** for permanent-makeup (PMU) studios: lines, blotches and under-eye texture go down, pores stay, and **brows, eyes, lips and the PMU work are never touched**.

🇮🇹 [Italiano più sotto](#italiano)

## Install

**Any agent — one command** (needs [Node.js](https://nodejs.org); asks which agents and whether to install for all your projects):

```bash
npx skills add dibeja/pmu-beautify
```

**Or by hand** — clone into your agent's skills folder (needs [git](https://git-scm.com)):

| Agent | macOS (Terminal) | Windows (PowerShell) |
|---|---|---|
| Claude Code | `git clone https://github.com/dibeja/pmu-beautify ~/.claude/skills/pmu-beautify` | `git clone https://github.com/dibeja/pmu-beautify $HOME\.claude\skills\pmu-beautify` |
| Codex, Gemini CLI, Cursor | `git clone https://github.com/dibeja/pmu-beautify ~/.agents/skills/pmu-beautify` | `git clone https://github.com/dibeja/pmu-beautify $HOME\.agents\skills\pmu-beautify` |

**Or ask your agent:** *"Install the skill from https://github.com/dibeja/pmu-beautify"* (in Codex you can also use `$skill-installer`).

**Zip (no tools needed):** download `pmu-beautify.zip` from [Releases](https://github.com/dibeja/pmu-beautify/releases/latest) and unzip it into the skills folder above.

Then restart your agent.

## First use

Just ask: *"beautify this photo: ~/Desktop/client.jpg"*, or *"pmu-beautify help"*, or *"guide me through pmu-beautify"* for a step-by-step wizard. On the first run the skill installs what it needs:

| | macOS | Windows 10/11 |
|---|---|---|
| Package manager | [Homebrew](https://brew.sh) — if missing, the skill gives you the command to paste (it asks for your Mac password) | winget (built into Windows; if missing, install "App Installer" from the Microsoft Store) |
| Installed | ffmpeg, Python 3.12 | ffmpeg, Python 3.12 |
| Private environment | `~/.pmu-beautify/` | `%USERPROFILE%\.pmu-beautify\` |

Plus Python packages (mediapipe, opencv, numpy) and two face models (~42 MB): [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) and [OpenCV SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface).

> **Windows is new and not yet tested on a real PC.** If setup stops, the agent shows you the error; please [open an issue](https://github.com/dibeja/pmu-beautify/issues) with it.

To remove everything: delete the `pmu-beautify` folder from your agent's skills folder and the `.pmu-beautify` folder in your home.

## What you can ask

See [HELP.md](HELP.md) — or just ask the agent for *help*. In short:

- retouch a photo or a video (or just a segment of it), subtle / natural / strong
- PMU protected: eyeliner and lip line stay exactly as they are — the default on clients
- retouch only one person in a group photo/video
- slim jaw/chin a little, whiten teeth (only if you ask)
- a side-by-side **before/after** image or video for approval (optional)
- a **wizard** that asks you one question at a time

**Rule:** the skill refuses to retouch the treated area of a result (brows, lips, eyeliner, areola). Retouching the work is misleading advertising.

---

## Italiano

[Agent Skill](https://agentskills.io) per **Claude Code, OpenAI Codex, Gemini CLI, Cursor** e gli altri agenti che leggono le skill `SKILL.md`, su **macOS e Windows**. Ritocca la pelle in **foto e video** per studi di trucco permanente (PMU): rughe, macchie e occhiaie si attenuano, i pori restano, e **sopracciglia, occhi, labbra e il lavoro PMU non vengono mai toccati**.

### Installazione

**Qualsiasi agente — un comando** (serve [Node.js](https://nodejs.org); chiede per quali agenti e se installarla per tutti i progetti):

```bash
npx skills add dibeja/pmu-beautify
```

**Oppure a mano** — clona nella cartella skill del tuo agente (serve [git](https://git-scm.com)):

| Agente | macOS (Terminale) | Windows (PowerShell) |
|---|---|---|
| Claude Code | `git clone https://github.com/dibeja/pmu-beautify ~/.claude/skills/pmu-beautify` | `git clone https://github.com/dibeja/pmu-beautify $HOME\.claude\skills\pmu-beautify` |
| Codex, Gemini CLI, Cursor | `git clone https://github.com/dibeja/pmu-beautify ~/.agents/skills/pmu-beautify` | `git clone https://github.com/dibeja/pmu-beautify $HOME\.agents\skills\pmu-beautify` |

**Oppure chiedilo al tuo agente:** *"Installa la skill da https://github.com/dibeja/pmu-beautify"* (in Codex puoi usare anche `$skill-installer`).

**Zip (senza strumenti):** scarica `pmu-beautify.zip` dalle [Releases](https://github.com/dibeja/pmu-beautify/releases/latest) e scompattalo nella cartella skill indicata sopra.

Poi riavvia l'agente.

### Primo utilizzo

Chiedi e basta: *"ritocca la pelle in questa foto: ~/Desktop/cliente.jpg"*, oppure *"pmu-beautify aiuto"*, oppure *"guidami con pmu-beautify"* per un wizard passo passo. Alla prima esecuzione la skill installa ciò che serve:

| | macOS | Windows 10/11 |
|---|---|---|
| Gestore pacchetti | [Homebrew](https://brew.sh) — se manca, la skill ti dà il comando da incollare (chiede la password del Mac) | winget (già in Windows; se manca, installa "App Installer" dal Microsoft Store) |
| Installati | ffmpeg, Python 3.12 | ffmpeg, Python 3.12 |
| Ambiente dedicato | `~/.pmu-beautify/` | `%USERPROFILE%\.pmu-beautify\` |

Più i pacchetti Python (mediapipe, opencv, numpy) e due modelli per il volto (~42 MB): [MediaPipe Face Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker) e [OpenCV SFace](https://github.com/opencv/opencv_zoo/tree/main/models/face_recognition_sface).

> **Il supporto Windows è nuovo e non ancora provato su un PC reale.** Se l'installazione si ferma, l'agente ti mostra l'errore: [aprici una issue](https://github.com/dibeja/pmu-beautify/issues) con quel testo.

Per rimuovere tutto: cancella la cartella `pmu-beautify` dalla cartella skill del tuo agente e la cartella `.pmu-beautify` nella tua home.

### Cosa puoi chiedere

Vedi [HELP.md](HELP.md), oppure chiedi *aiuto* all'agente. In breve:

- ritoccare una foto o un video (anche solo un pezzo), leggero / naturale / deciso
- PMU protetto: eyeliner e contorno labbra restano identici — di default sulle clienti
- ritoccare una sola persona in una foto/video di gruppo
- snellire leggermente mascella/mento, sbiancare i denti (solo se lo chiedi)
- un confronto **prima/dopo** affiancato, foto o video, per l'approvazione (opzionale)
- un **wizard** che ti fa una domanda alla volta

**Regola:** la skill si rifiuta di ritoccare la zona trattata di un risultato (sopracciglia, labbra, eyeliner, areola). Ritoccare il lavoro è pubblicità ingannevole.

## License

MIT — see [LICENSE](LICENSE). The face models are downloaded from their original sources under their own licenses.
