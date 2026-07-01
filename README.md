<a id="top"></a>

<div align="center">

<h1>Pixel Bloom · 像素生命的绽放</h1>

<p><em>一个 Claude Code Skill，用于生成像素艺术 × Frutiger Aero 毛玻璃风格的交互式 H5 页面。</em></p>

<p>
  <a href="https://github.com/shasha1108/pixel-bloom/stargazers"><img src="https://img.shields.io/github/stars/shasha1108/pixel-bloom?style=for-the-badge&color=f5a97f" alt="Stars"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge" alt="License"></a>
  <a href="https://github.com/shasha1108/pixel-bloom"><img src="https://img.shields.io/badge/Claude%20Code-Skill-6C4AB6?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code Skill"></a>
  <a href="#"><img src="https://img.shields.io/badge/output-p5.js-ED225D?style=for-the-badge&logo=p5.js&logoColor=white" alt="p5.js"></a>
</p>

<p>
  <a href="#-快速开始">快速开始</a> ·
  <a href="#-生成什么">生成什么</a> ·
  <a href="#-能力矩阵">能力矩阵</a> ·
  <a href="#-工作原理">工作原理</a> ·
  <a href="#-项目结构">项目结构</a>
</p>

</div>

---

<details open>
<summary><strong>📑 目录</strong></summary>

- [概述](#-概述)
- [生成什么](#-生成什么)
- [快速开始](#-快速开始)
- [场景模式](#-场景模式)
- [能力矩阵](#-能力矩阵)
- [概念种子](#-概念种子)
- [工作原理](#-工作原理)
- [质量门禁](#-质量门禁)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [调色板](#-调色板)
- [相关项目](#-相关项目)
- [参与贡献](#-参与贡献)
- [许可](#-许可)

</details>

---

## 📖 概述

**pixel-bloom** 是一个 Claude Code Skill，能生成完整的、独立运行的 HTML 页面——每个页面都是一个活在 Frutiger Aero 发光玻璃中的像素世界。一次生成，融合五种能力：

| 能力 | 说明 |
|------|------|
| 🎨 **p5.js 像素渲染** | `pixelDensity(1)` + `noSmooth()`，栅格对齐的锐利像素精灵，零抗锯齿 |
| 🪟 **Frutiger Aero 玻璃美学** | 磨砂玻璃层叠、环境光球、Ganzfeld 光场——发光的，不是暗黑的 |
| 🌿 **程序化植物** | 4 种算法植物模型（stack-sway / grid-cull / radial-domain / fan-spread），会生长、摇摆、呼吸 |
| 🐟 **AI 状态机生物** | Wander / Chase / Flee 有限状态机 + Perlin noise 驱动——会感知、会反应的生命体 |
| 🔊 **Web Audio 代码合成** | 颂钵、环境 drone、和弦垫、双耳节拍——全部代码合成，零音频文件 |

> **输出就是一个 `.html` 文件。** 不需要构建、不需要框架、除了 p5.js CDN 没有任何依赖。用浏览器打开就能运行。

<br>

<div align="center">

| 🐱 赛博宠物 | 🌱 像素盆栽 | 🐠 电子水族箱 | 🌲 像素森林 |
|:---:|:---:|:---:|:---:|
| *一个会一直等你的伙伴* | *不需要观众的生长* | *一个与你平行存在的世界* | *每棵树有自己的节奏* |

</div>

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🎬 生成什么

每次生成都是一个**自包含的像素生态系统**——这是产出的结构：

```
┌──────────────────────────────────────┐
│  🌟  环境光球 (z=1)                  │  ← CSS radial-gradient，缓慢漂浮
│  ┌────────────────────────────────┐  │
│  │ 🪟  磨砂玻璃基层 (z=2)          │  │  ← 唯一使用 backdrop-filter: blur() 的层
│  │  ┌──────────────────────────┐  │  │
│  │  │  🎨  像素画布 (z=3)       │  │  │  ← p5.js：生物、植物、粒子
│  │  │  🐟→  🌿~  🫧↑          │  │  │
│  │  └──────────────────────────┘  │  │
│  │  ✨  玻璃外壳 (z=4)             │  │  │  ← ::after 菲涅尔高光，无模糊，pointer-events: none
│  └────────────────────────────────┘  │
│  🖐️  交互拦截层 (z=5)               │  ← 原生 pointerdown 事件
└──────────────────────────────────────┘
```

**每个页面包含：**
- 像素艺术生命体，Perlin noise 驱动的平滑运动
- 触控 / 点击交互（喂食、敲击、拖拽、安抚）
- 实时合成的环境音效（零音频文件）
- 响应式画布，移动端和桌面端都能跑

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🚀 快速开始

### 前提

- 已安装 [Claude Code](https://claude.ai/code)
- pixel-bloom skill 已在你的 skills 目录中

### 生成你的第一个像素世界

在 Claude Code 中输入：

```
/pixel-bloom 帮我做一个像素多肉盆栽，阳光透过玻璃洒下来
```

或者用英文描述：

```
/pixel-bloom Create a pixel succulent garden in a glass terrarium with sunlight streaming through
```

### 更多灵感

```
/pixel-bloom 做一个像素水族箱，里面有3条热带鱼和珊瑚
/pixel-bloom A cyber pet cat that naps and occasionally wakes up to play
/pixel-bloom 一个像素森林，每棵树有不同的摆动节奏，点击种花
/pixel-bloom A meditative Ganzfeld light field with floating pixel particles
```

> 💡 **场景描述越具体，生成效果越好。** 建议描述清楚：容器形态（玻璃罩？开放天空？）、生命体（什么种类？几个？）、交互方式（喂食？敲击？拖拽？）。

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🏞️ 场景模式

| 模式 | 说明 | 适合 | 视觉特征 |
|------|------|------|----------|
| 🫙 **封闭容器** | 玻璃 terrarium、水族箱、玻璃罩 | 赛博宠物、像素盆栽、像素养鱼 | 磨砂玻璃边框，`backdrop-filter: blur()` |
| 🌌 **开放视口** | 天空、水下、开放原野 | 像素森林、天空花园、海底 | 无边画布，无玻璃边框 |
| 🌅 **Ganzfeld 光场** | 沉浸式光场——无物体，纯光 | 冥想、光浴、漂浮体验 | 缓慢色温漂移，无硬边缘，无暗色 |

> **触发 Ganzfeld 模式的关键词：** 沉浸 / 冥想 / 光浴 / 漂浮 / 光场——skill 会自动切换到专用的光场渲染管线。

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## ✨ 能力矩阵

| | 能力 | 说明 |
|---|------|------|
| 🧬 | **程序化植物（4 种模型）** | stack-sway（草叶层叠摇摆）、grid-cull（网格删减法叶簇）、radial-domain（径向域莲座/多肉）、fan-spread（扇状蕨类）——算法生成的植物 |
| 🧠 | **AI 生物状态机** | Wander → Chase → Flee 有限状态机 + Perlin noise 运动——生物会*反应*，不只是播放动画 |
| 🪟 | **Frutiger Aero 玻璃** | 多层玻璃壳 + 菲涅尔高光 + 环境光球 + Ganzfeld 光场——发光的，不是暗黑的 |
| 🔊 | **零文件音频** | 颂钵、焦虑/疗愈 drone、和弦垫、双耳节拍——全部由 Web Audio 振荡器合成 |
| 🖐️ | **触控仪式** | 单击喂食、双击敲击、拖拽安抚——自定义 pointerdown 去抖，移动端适配 |
| 🌱 | **种子系统** | 可复现随机种子 + 参数滑块 + 可分享 URL——随时回到那个世界 |
| 📐 | **5 种画幅比例** | 3:4 / 9:16 / 1:1 / 4:3 / 16:9 / 全视口——场景推荐，用户决定 |
| 🎨 | **6 套调色板** | Aqua Glass / Botanical Dew / Sunlit Meadow / Coral Reef / Lavender Mist / Cyber Mint |
| ✅ | **内置校验器** | `validate.py`——8 大类检查：meta 头、像素规则、z-index 夹层、音频、色彩、性能、JS 语法 |

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🌱 概念种子

> 每一个 pixel-bloom 场景都建立在一个不直说的情感锚点上——"概念种子"。它决定后续所有设计的走向：颜色温度、运动速度、交互反馈的延迟和质感。

| 场景 | 表面需求 | 概念种子 | 北极星命名 |
|------|----------|----------|------------|
| 🐱 **赛博宠物** | "养一个电子宠物" | **"它会一直在"**——无条件的陪伴 | **Always Here** |
| 🌿 **像素盆栽** | "种一棵像素植物" | **"你不在的时候它也在生长"**——生命不需要观众 | **Still Growth** |
| 🐠 **电子水族箱** | "养一缸像素鱼" | **"它们不在乎你有没有在看"**——另一个世界的平行存在 | **Another Tank** |
| 🌲 **像素森林** | "一片像素树林" | **"每棵树都有自己的节奏"**——慢下来不是落后 | — |

这些不是营销文案，而是**北极星命名**——后续每一项决策（颜色冷暖、运动快慢、交互延迟）都要对照它检查。如果赛博宠物的运动让人觉得"好厉害"而不是"好安心"，北极星会说：不对，改。

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## ⚙️ 工作原理

### 六步生成管线

```
STEP 0           STEP 1–3          STEP 4            STEP 4.5       STEP 5–5.5        STEP 6
视觉调研          设计决策          代码生成          精修           质量保障           交付验证
──────→          ──────→          ──────→          ──────→        ──────→          ──────→
新场景调研       画幅比例          从防御性骨架出发    只删不增        validate.py      浏览器实测
                场景模式          匹配植物模型        微调参数        读者测试          触控检查
                音频方案          组装 FSM 代码       强化呼应        情感检查          格式化输出
                像素拆解
                5 项技术决策
```

<details>
<summary><strong>🔍 各步骤详情</strong></summary>

| 步骤 | 做什么 |
|------|--------|
| **STEP 0** | 视觉调研——新场景类型需要先搜集真实玻璃、植物、生物行为参考 |
| **STEP 1** | 确定画幅比例、音频方案、场景模式（封闭/开放/Ganzfeld） |
| **STEP 2** | 把用户描述拆解为像素元素，匹配程序化模型 |
| **STEP 3** | 5 项技术决策：画布类型、运动模式、玻璃类型、粒子数量、音频方案 |
| **STEP 4** | 从防御性骨架出发生成代码，加载匹配的植物模型和 FSM 模板 |
| **STEP 4.5** | 精修——*只做*删减、微调参数、加强已有元素呼应。不加新实体 |
| **STEP 5** | 运行 `validate.py`——8 大类检查，全绿才继续 |
| **STEP 5.5** | **读者测试**——切换视角为第一次打开页面的用户：第一秒的感觉对吗？ |
| **STEP 6** | `/verify` 浏览器验证，触控实测，最终交付 |

</details>

### 不可变架构：Z-Index 夹层

每个生成页面使用完全一致的图层堆叠——永不改变：

```
z=1  🌟  环境光球               CSS radial-gradient，固定定位，缓慢漂浮
z=2  🪟  磨砂玻璃基层           唯一使用 backdrop-filter: blur() 的层
z=3  🎨  像素画布               p5.js 渲染面，drop-shadow
z=4  ✨  玻璃外壳               ::after 菲涅尔高光，禁止模糊，pointer-events: none
z=5  🖐️  交互拦截层             原生 pointerdown 事件，无合成点击
```

### 仿生运动三法则

| 法则 | 原则 | 实现 |
|------|------|------|
| 🔄 **生命呼吸** | 没有任何物体是完全静止的 | 每个实体都有 `sin`/`cos` 微动 |
| 🌊 **灵魂漫游** | 平滑探索，不是机械巡逻 | Perlin noise（`noise()`）——绝对不用 `random()` 做运动 |
| 🍮 **延迟满足** | 有重量感、"果冻般"的质感 | 所有过渡使用 `lerp()` 阻尼 |

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🔬 质量门禁

pixel-bloom 在交付前执行多层质量把关：

| 门禁 | 工具 | 检查内容 |
|------|------|----------|
| 🔧 **结构** | `scripts/validate.py` | Meta 注释头、p5.js 像素规则（`pixelDensity(1)`、`noSmooth()`）、z-index 夹层完整性、JS 语法（`node --check`） |
| 🎨 **美学** | 人工审查 | 色彩纪律（禁止暗黑模式、禁止高饱和原色）、Frutiger Aero 色板一致性 |
| 🧠 **交互** | 人工审查 | 单击/双击分离（300ms 去抖）、移动端 touch 不触发默认滚动、拖拽支持 |
| 🔊 **音频** | 人工审查 | AudioContext 首次交互后恢复、音量包络、零音频文件依赖 |
| ❤️ **情感** | **读者测试** | 4 个问题：第一秒感受、本能想碰哪里、10 秒后还在看吗、有没有"AI 做的"痕迹 |

> **读者测试**（STEP 5.5）是 pixel-bloom 独有的质量环节：AI 必须切换视角，以首次打开页面的用户身份评估情感共鸣是否与概念种子一致——不只是检查技术正确性。

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🛠️ 技术栈

<div align="center">

| 层级 | 技术 | 用途 |
|:---:|:---:|---|
| 🎨 | **p5.js 1.9.0** | 像素级 Canvas2D 渲染 |
| 🪟 | **CSS Glassmorphism** | `backdrop-filter` 多层磨砂玻璃 |
| 🔊 | **Web Audio API** | 振荡器合成音频（零音频文件） |
| 🌊 | **Perlin Noise** | 所有生命体的平滑有机运动 |
| 🧮 | **程序化数学** | 4 种植物模型 + FSM 生物行为 |
| 🌐 | **纯 HTML/CSS/JS** | 零框架，单文件输出 |

</div>

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 📁 项目结构

```
pixel-bloom/
├── SKILL.md                          # 核心 skill 定义 & 六步生成管线
├── README.md                         # ← 你在看这里
├── LICENSE                           # MIT
├── CLAUDE.md                         # Git 工作流规范（多设备防冲突）
│
├── assets/
│   └── palettes.json                 # 6 套 Frutiger Aero 调色板
│
├── references/
│   ├── design-principles.md          # 22 节通用设计原则与反模式
│   ├── generation-workflow.md        # STEP 0–3 执行细节 / 场景模式表 / 技术决策表
│   ├── code-templates.md             # 防御性骨架 / 4 种植物模型 / FSM 代码 / 质量清单
│   ├── landscape-composition.md      # 风景画纵深构图 7 层公式（开放场景触发）
│   ├── vegetation-system.md          # 像素植被系统 — 物种表 / 分支生长 / 三级风
│   ├── ocean-pixels.md               # 像素海洋 — Gerstner 波浪 / 焦散 / 河流模式
│   ├── audio-engine.md               # Web Audio 合成配方（零音频文件）
│   ├── audio-advanced.md             # 和弦垫 / 节拍器 / 五声音阶 / AudioWorklet / 空间混响
│   └── seeded-exploration.md         # 种子导航 / 参数滑块面板 / 可分享 URL
│
└── scripts/
    └── validate.py                   # 8 类静态校验器（meta / 像素 / z-index / JS 语法 / …）
```

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🎨 调色板

6 套手工调校的 Frutiger Aero 色板——每个场景选用一套：

<table>
<tr>
<td align="center"><strong>Aqua Glass</strong>（水族玻璃）<br><code>#C8E6F5</code> <code>#7EC8E3</code> <code>#4A9EC8</code></td>
<td align="center"><strong>Botanical Dew</strong>（植物晨露）<br><code>#C5E8C9</code> <code>#7DB87D</code> <code>#4A8C4A</code></td>
<td align="center"><strong>Sunlit Meadow</strong>（阳光草甸）<br><code>#F5E6C8</code> <code>#E8C87D</code> <code>#C8A84A</code></td>
</tr>
<tr>
<td align="center"><strong>Coral Reef</strong>（珊瑚礁）<br><code>#F5C8D0</code> <code>#E87D8E</code> <code>#C84A5E</code></td>
<td align="center"><strong>Lavender Mist</strong>（薰衣草雾）<br><code>#E0D0F0</code> <code>#B89AE0</code> <code>#8B6CC0</code></td>
<td align="center"><strong>Cyber Mint</strong>（赛博薄荷）<br><code>#C8F5E6</code> <code>#7DE8C8</code> <code>#4AC8A8</code></td>
</tr>
</table>

> 全部遵循 Frutiger Aero 色彩纪律：柔和粉彩、发光渐变、**禁止深色背景、禁止高饱和原色**。

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🔗 相关项目

| 仓库 | 做什么 |
|------|--------|
| [**healing-visual-lab**](https://github.com/shasha1108/healing-visual-lab) | 交互式数字疗愈作品集——15 件 Three.js / WebGL 交互实验 |
| [**healing-space**](https://github.com/shasha1108/healing-space) | 触觉驱动的交互式疗愈 H5 生成器——GPU 流体、WebGL 着色器 |
| [**inner-voice**](https://github.com/shasha1108/inner-voice) | 小红书情绪内容创作——隐喻挖掘、场景写作、视觉叙事 |
| [**h5-publish-skill**](https://github.com/shasha1108/h5-publish-skill) | 一键发布 H5 到 GitHub Pages——拖入文件夹即上线 |

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>

---

## 🤝 参与贡献

这是个人创作工具，但欢迎任何想法和贡献：

1. 🍴 **Fork** 本仓库
2. 🌿 **创建分支**（`feature/你的想法`）
3. ✍️ **提交**清晰的 commit message
4. 📤 **Push** 并打开 **Pull Request**

**特别欢迎以下方向的贡献：**
- 新的程序化植物模型（超越现有 A–D 四种）
- 更多 Frutiger Aero 调色板
- 新情感质感的音频合成配方
- 文档翻译改进（中文 / English）

> 本仓库使用的 Git 工作流规范见 [CLAUDE.md](CLAUDE.md)。

---

## 📄 许可

MIT © 2026 [@shasha1108](https://github.com/shasha1108) —— 详见 [LICENSE](LICENSE)。

<br>

<div align="center">

<sub>用像素、玻璃与光，创造出生命绽放的世界。</sub>

</div>

<p align="right"><sub><a href="#top">↑ 回到顶部</a></sub></p>
