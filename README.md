<a id="top"></a>

<div align="center">

```
  ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
  ⬜⬜⬜🟦🟦🟦⬜⬜⬜🟩🟩⬜⬜🟪🟪🟪⬜⬜⬜🟦🟦🟦⬜
  ⬜⬜🟦✨🟦⬜⬜🟩🌱🟩⬜🟪✨🟪⬜⬜🟦✨🟦⬜⬜
  ⬜🟦🟦🟦🟦🟦⬜🟩🟩🟩🟩🟩🟪🟪🟪🟪🟪🟦🟦🟦🟦🟦⬜
  ⬜⬜🟦🟦🟦⬜⬜🟩🟩🟩⬜⬜🟪🟪🟪⬜⬜⬜🟦🟦🟦⬜⬜
  ⬜⬜⬜🟦⬜⬜⬜⬜🟩⬜⬜⬜⬜🟪⬜⬜⬜⬜⬜🟦⬜⬜⬜⬜
  ⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜⬜
```

<h1>Pixel Bloom · 像素生命的绽放</h1>

<p><em>A Claude Code skill for building pixel-art interactive H5 pages with Frutiger Aero glassmorphism.</em></p>

<p>
  <a href="https://github.com/shasha1108/pixel-bloom/stargazers"><img src="https://img.shields.io/github/stars/shasha1108/pixel-bloom?style=for-the-badge&color=f5a97f" alt="Stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/shasha1108/pixel-bloom"><img src="https://img.shields.io/badge/Claude%20Code-Skill-6C4AB6?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill"></a>
  <a href="#"><img src="https://img.shields.io/badge/output-p5.js-ED225D?style=for-the-badge&logo=p5.js&logoColor=white" alt="p5.js"></a>
</p>

<p>
  <a href="#-quick-start">Quick Start</a> ·
  <a href="#-what-it-makes">What It Makes</a> ·
  <a href="#-features">Features</a> ·
  <a href="#-how-it-works">How It Works</a> ·
  <a href="#-project-structure">Structure</a>
</p>

</div>

---

<details open>
<summary><strong>📑 Table of Contents</strong></summary>

- [About](#-about)
- [What It Makes](#-what-it-makes)
- [Quick Start](#-quick-start)
- [Scene Modes](#-scene-modes)
- [Features](#-features)
- [The Concept Seeds](#-the-concept-seeds)
- [How It Works](#-how-it-works)
- [Quality Standards](#-quality-standards)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Color Palettes](#-color-palettes)
- [Related Projects](#-related-projects)
- [Contributing](#-contributing)
- [License](#-license)

</details>

---

## 📖 About

**pixel-bloom** is a Claude Code skill that generates complete, standalone HTML pages — each one a living pixel-art world wrapped in luminous Frutiger Aero glass. It combines five disciplines into a single output:

| Pillar | Role |
|--------|------|
| 🎨 **p5.js pixel rendering** | Sharp, grid-aligned sprites — zero anti-aliasing, pure pixel aesthetic |
| 🪟 **Frutiger Aero glassmorphism** | Frosted glass shells, ambient light orbs, Ganzfeld light fields |
| 🌿 **Procedural flora** | 4 algorithmic plant models that grow, sway, and breathe |
| 🐟 **AI FSM creatures** | Wander / Chase / Flee state machines driven by Perlin noise |
| 🔊 **Web Audio synthesis** | Healing bowls, ambient drones, binaural beats — code only, zero audio files |

> **The output is a single `.html` file.** No build step, no framework, no dependencies beyond p5.js CDN. Open it in any browser and it runs.

<br>

<div align="center">

| 🐱 Cyber Pet | 🌱 Pixel Bonsai | 🐠 Digital Aquarium | 🌲 Pixel Forest |
|:---:|:---:|:---:|:---:|
| *A companion that waits* | *Growth needs no audience* | *A world that exists without you* | *Every tree has its rhythm* |

</div>

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🎬 What It Makes

Every pixel-bloom generation is a **self-contained living pixel ecosystem** — here's what a typical output looks like:

```
┌──────────────────────────────────────┐
│  🌟  Ambient Light Orbs (z=1)        │  ← CSS radial-gradient, slow floating
│  ┌────────────────────────────────┐  │
│  │ 🪟  Frosted Glass Base (z=2)    │  │  ← backdrop-filter: blur()
│  │  ┌──────────────────────────┐  │  │
│  │  │  🎨  Pixel Canvas (z=3)  │  │  │  ← p5.js: creatures, flora, particles
│  │  │  🐟→  🌿~  🫧↑          │  │  │
│  │  └──────────────────────────┘  │  │
│  │  ✨  Glass Shell (z=4)          │  │  │  ← ::after Fresnel highlight, no blur
│  └────────────────────────────────┘  │
│  🖐️  Interaction Layer (z=5)         │  ← pointerdown events
└──────────────────────────────────────┘
```

**Each page includes:**
- Pixel-art lifeforms with smooth Perlin-noise motion
- Touch/click interactions (feed, knock, drag, soothe)
- Ambient audio synthesized in real-time (no audio files)
- Responsive canvas that works on mobile and desktop

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🚀 Quick Start

### Prerequisites

- [Claude Code](https://claude.ai/code) installed
- The pixel-bloom skill in your skills directory

### Generate your first pixel world

In Claude Code, type:

```
/pixel-bloom 帮我做一个像素多肉盆栽，阳光透过玻璃洒下来
```

Or in English:

```
/pixel-bloom Create a pixel succulent garden in a glass terrarium with sunlight streaming through
```

### More ideas

```
/pixel-bloom 做一个像素水族箱，里面有3条热带鱼和珊瑚
/pixel-bloom A cyber pet cat that naps and occasionally wakes up to play
/pixel-bloom 一个像素森林，每棵树有不同的摆动节奏，点击种花
/pixel-bloom A meditative Ganzfeld light field with floating pixel particles
```

> 💡 **The more specific your scene description, the better the result.** Mention the container (glass dome? open sky?), the lifeforms (how many? what kind?), and the interaction (feed? knock? drag?).

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🏞️ Scene Modes

| Mode | Description | Best For | Visual Style |
|------|-------------|----------|--------------|
| 🫙 **Closed Container** | Glass terrarium, aquarium, dome | Cyber pets, bonsai, fish tanks | Frosted glass frame, `backdrop-filter: blur()` |
| 🌌 **Open Viewport** | Sky, underwater, open field | Pixel forests, sky gardens, seabed | Edge-to-edge canvas, no glass frame |
| 🌅 **Ganzfeld** | Immersive light field — no objects, pure light | Meditation, light baths, floating experiences | Slow color-temperature drift, no hard edges, no darkness |

> **Keywords that trigger Ganzfeld mode:** 沉浸 / 冥想 / 光浴 / 漂浮 / 光场 — the skill automatically switches to a specialized light-field rendering pipeline.

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## ✨ Features

| | Feature | Description |
|---|---------|-------------|
| 🧬 | **Procedural Flora (4 models)** | Stack-sway (grasses), grid-cull (leaves), radial-domain (rosettes/succulents), fan-spread (ferns) — plants that grow algorithmically |
| 🧠 | **AI Creature FSM** | Wander → Chase → Flee state machine with Perlin-noise motion — creatures that *react*, not just animate |
| 🪟 | **Frutiger Aero Glass** | Multi-layer glass shells with Fresnel highlights, ambient light orbs, Ganzfeld light fields — luminous, not dark |
| 🔊 | **Zero-File Audio** | Singing bowls, anxiety/healing drones, chord pads, binaural beats — all synthesized from Web Audio oscillators |
| 🖐️ | **Touch Rituals** | Click-to-feed, double-click-to-knock, drag-to-soothe — custom pointerdown debounce with mobile support |
| 🌱 | **Seed System** | Reproducible random seeds + parameter sliders + shareable URLs — revisit the exact same world |
| 📐 | **5 Canvas Ratios** | 3:4, 9:16, 1:1, 4:3, 16:9, or full viewport — scene-recommended, user-chosen |
| 🎨 | **6 Color Palettes** | Aqua Glass, Botanical Dew, Sunlit Meadow, Coral Reef, Lavender Mist, Cyber Mint |
| ✅ | **Built-in Validator** | `validate.py` — 8 categories of checks: meta headers, pixel rules, z-index sandwich, audio, color, performance, JS syntax |

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🌱 The Concept Seeds

> Every pixel-bloom scene is built around an unspoken emotional anchor — a "concept seed" that guides every design decision from color temperature to motion speed to interaction feedback.

| Scene | Surface | Concept Seed | Guiding Name |
|-------|---------|-------------|--------------|
| 🐱 **Cyber Pet** | "Raise a digital pet" | *"It will always be there"* — unconditional companionship | **Always Here** |
| 🌿 **Pixel Bonsai** | "Grow a pixel plant" | *"It grows even when you're not watching"* — life needs no audience | **Still Growth** |
| 🐠 **Digital Aquarium** | "Keep a tank of pixel fish" | *"They don't care whether you're watching"* — a parallel world's parallel existence | **Another Tank** |
| 🌲 **Pixel Forest** | "A grove of pixel trees" | *"Every tree has its own rhythm"* — slowness is not falling behind | — |

These aren't marketing slogans. They're **polaris names** — every subsequent decision (color warmth, motion speed, interaction latency) is checked against them. If a cyber pet's motion feels "impressive" instead of "companionable," the name says: fix it.

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## ⚙️ How It Works

### The Generation Pipeline (6 Steps)

```
STEP 0           STEP 1–3          STEP 4            STEP 4.5       STEP 5–5.5        STEP 6
Visual           Design            Code              Polish         Quality           Deliver
Research  ──→    Decisions  ──→    Generation  ──→   (Refine)  ──→  Assurance  ──→   & Verify
(new scenes)     Canvas ratio      From defensive    Delete only    validate.py       Browser test
                 Scene mode        skeleton          Micro-tune     Reader test       Touch check
                 Audio profile     Templates         Strengthen     Emotional check   Format output
                 Decompose scene   Flora models      resonance
                 Tech decisions    FSM code
```

<details>
<summary><strong>🔍 Step-by-step details</strong></summary>

| Step | What Happens |
|------|-------------|
| **STEP 0** | Visual research — for new scene types, gather reference on real-world glass, plants, creature behaviors |
| **STEP 1** | Decide canvas ratio, audio profile, and scene mode (closed/open/Ganzfeld) |
| **STEP 2** | Decompose the user's description into pixel elements + assign procedural models |
| **STEP 3** | 5 technical decisions: canvas type, motion mode, glass type, particle count, audio profile |
| **STEP 4** | Code generation from defensive skeleton + matching flora/FSM templates |
| **STEP 4.5** | Polish — *only* delete, micro-tune parameters, strengthen resonance. No new entities |
| **STEP 5** | Run `validate.py` — 8 categories, must pass all green |
| **STEP 5.5** | **Reader test** — shift perspective to a first-time user: does the first second feel right? |
| **STEP 6** | Browser verification via `/verify`, touch check, final delivery |

</details>

### Immutable Architecture: The Z-Index Sandwich

Every generated page uses this exact layer stack — never changed:

```
z=1  🌟  Ambient Light Orbs       CSS radial-gradient, fixed, slow float
z=2  🪟  Frosted Glass Base       ONLY layer with backdrop-filter: blur()
z=3  🎨  Pixel Canvas             p5.js render surface, drop-shadow
z=4  ✨  Glass Shell              ::after Fresnel highlight, NO blur, pointer-events: none
z=5  🖐️  Interaction Intercept    Native pointerdown events, no synthetic clicks
```

### Three Biomimetic Motion Laws

| Law | Principle | Implementation |
|-----|-----------|---------------|
| 🔄 **Life Breathing** | No object is ever perfectly still | `sin`/`cos` micro-motion on every entity |
| 🌊 **Soul Wandering** | Smooth exploration, not mechanical patrol | Perlin noise (`noise()`) — never `random()` for movement |
| 🍮 **Delayed Gratification** | Weight and "jelly-like" feel | `lerp()` damping on all transitions |

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🔬 Quality Standards

pixel-bloom enforces a multi-layered quality gate before any output is delivered:

| Gate | Tool | Checks |
|------|------|--------|
| 🔧 **Structural** | `scripts/validate.py` | Meta headers, p5.js pixel rules (`pixelDensity(1)`, `noSmooth()`), z-index sandwich integrity, JS syntax (`node --check`) |
| 🎨 **Aesthetic** | Manual review | Color discipline (no dark mode, no high-saturation primaries), Frutiger Aero palette adherence |
| 🧠 **Interaction** | Manual review | Click/double-click separation (300ms debounce), mobile touch (no default scroll), drag support |
| 🔊 **Audio** | Manual review | AudioContext resume on first interaction, volume envelopes, no audio file dependencies |
| ❤️ **Emotional** | **Reader Test** | 4 questions: first-second feeling, instinctive interaction targets, 10-second retention, "AI-made" tells |

> The **Reader Test** (STEP 5.5) is unique to pixel-bloom: the AI must shift perspective and evaluate the output as a first-time user, checking emotional resonance against the concept seed — not just technical correctness.

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|:---:|:---:|---|
| 🎨 | **p5.js 1.9.0** | Pixel-perfect Canvas2D rendering |
| 🪟 | **CSS Glassmorphism** | Multi-layer frosted glass with `backdrop-filter` |
| 🔊 | **Web Audio API** | Oscillator-based synthesis (no audio files) |
| 🌊 | **Perlin Noise** | Smooth organic motion for all lifeforms |
| 🧮 | **Procedural Math** | 4 flora models + FSM creature behaviors |
| 🌐 | **Vanilla HTML/CSS/JS** | Zero framework, single-file output |

</div>

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 📁 Project Structure

```
pixel-bloom/
├── SKILL.md                          # Core skill definition & 6-step generation pipeline
├── README.md                         # ← You are here
├── LICENSE                           # MIT
├── CLAUDE.md                         # Git workflow discipline (multi-device safety)
│
├── assets/
│   └── palettes.json                 # 6 Frutiger Aero color palettes
│
├── references/
│   ├── design-principles.md          # Architecture decisions, motion laws, materials, anti-patterns
│   ├── generation-workflow.md        # STEP 0–3 execution details, scene mode tables
│   ├── code-templates.md             # Defensive HTML skeleton, 4 flora models, FSM, quality checklist
│   ├── audio-engine.md               # Web Audio synthesis recipes (zero audio files)
│   ├── audio-advanced.md             # Chord pads, pentatonic scales, AudioWorklet, spatial reverb
│   └── seeded-exploration.md         # Seed navigation, parameter sliders, shareable URLs
│
└── scripts/
    └── validate.py                   # 8-category static validator (meta, pixel, z-index, JS syntax, …)
```

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🎨 Color Palettes

Six hand-crafted Frutiger Aero palettes — each scene picks one:

<table>
<tr>
<td align="center"><strong>Aqua Glass</strong><br><code>#C8E6F5</code> <code>#7EC8E3</code> <code>#4A9EC8</code></td>
<td align="center"><strong>Botanical Dew</strong><br><code>#C5E8C9</code> <code>#7DB87D</code> <code>#4A8C4A</code></td>
<td align="center"><strong>Sunlit Meadow</strong><br><code>#F5E6C8</code> <code>#E8C87D</code> <code>#C8A84A</code></td>
</tr>
<tr>
<td align="center"><strong>Coral Reef</strong><br><code>#F5C8D0</code> <code>#E87D8E</code> <code>#C84A5E</code></td>
<td align="center"><strong>Lavender Mist</strong><br><code>#E0D0F0</code> <code>#B89AE0</code> <code>#8B6CC0</code></td>
<td align="center"><strong>Cyber Mint</strong><br><code>#C8F5E6</code> <code>#7DE8C8</code> <code>#4AC8A8</code></td>
</tr>
</table>

> All palettes follow Frutiger Aero rules: soft pastels, luminous gradients, **no dark backgrounds, no high-saturation primaries**.

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🔗 Related Projects

| Repo | What It Does |
|------|-------------|
| [**healing-visual-lab**](https://github.com/shasha1108/healing-visual-lab) | 15 interactive digital healing experiments — Three.js / WebGL |
| [**healing-space**](https://github.com/shasha1108/healing-space) | Touch-driven healing H5 generator — GPU fluids, WebGL shaders |
| [**inner-voice**](https://github.com/shasha1108/inner-voice) | Xiaohongshu emotional content creation — metaphor mining, visual storytelling |
| [**h5-publish-skill**](https://github.com/shasha1108/h5-publish-skill) | One-click H5 publishing to GitHub Pages — drag, drop, deploy |

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>

---

## 🤝 Contributing

This is a personal creative tool, but contributions and ideas are welcome:

1. 🍴 **Fork** the repository
2. 🌿 **Branch** (`feature/your-idea`)
3. ✍️ **Commit** with clear messages
4. 📤 **Push** and open a **Pull Request**

**Areas where contributions are especially welcome:**
- New procedural flora models (beyond A–D)
- Additional Frutiger Aero color palettes
- Audio synthesis recipes for new emotional textures
- Translation improvements (English / 中文)

> See [CLAUDE.md](CLAUDE.md) for git workflow conventions used in this repo.

---

## 📄 License

MIT © 2026 [@shasha1108](https://github.com/shasha1108) — see [LICENSE](LICENSE) for full text.

<br>

<div align="center">

```
  ⬜⬜⬜🟦🟦🟦⬜⬜⬜🟩🟩⬜⬜🟪🟪🟪⬜⬜⬜🟦🟦🟦⬜⬜⬜
  ⬜⬜🟦✨🟦⬜⬜🟩🌱🟩⬜🟪✨🟪⬜⬜🟦✨🟦⬜⬜⬜
  ⬜🟦🟦🟦🟦🟦⬜🟩🟩🟩🟩🟩🟪🟪🟪🟪🟪🟦🟦🟦🟦🟦⬜⬜
  ⬜⬜🟦🟦🟦⬜⬜🟩🟩🟩⬜⬜🟪🟪🟪⬜⬜⬜🟦🟦🟦⬜⬜⬜
```

<sub>Made with pixels, glass, and light. 用像素、玻璃与光，创造出生命绽放的世界。</sub>

</div>

<p align="right"><sub><a href="#top">↑ back to top</a></sub></p>
