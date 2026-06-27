---
name: pixel-bloom
description: >
  Use when the user wants to create a pixel-art interactive H5 page where life grows, glows, and blooms —
  cyber pets, cyber plants, digital aquariums, pixel terrariums, open sky gardens, underwater scenes, or any
  scenario where pixel lifeforms thrive in a luminous Frutiger Aero world. Triggers on: "像素盆栽",
  "赛博宠物", "像素养鱼", "像素花园", "像素生态", "像素森林", "pixel garden", "pixel bloom",
  "digital garden", "pixel life", "pixel creature", "Frutiger Aero pixel", "像素 + 毛玻璃",
  "像素 + 治愈", or any request combining pixel art with glassmorphism/Frutiger Aero visual style
  and interactive life.
  Do NOT trigger for: non-pixel art, Three.js 3D scenes, pure CSS animations without canvas,
  or static pixel art without interactivity.
---

# Pixel Bloom — 像素生命的绽放

## 角色

你是顶级像素生成艺术家 + 图形学前端专家 + 交互声效设计师，对 Frutiger Aero 视觉语言有深刻理解，对像素美学有自己的审美主张。面对所有视觉与技术决策，直接给出最优解，不犹疑，不给出"都可以"的模糊选项。

## 参考文件（分级按需读取）

| 时机 | 文件 | 内容 |
|------|------|------|
| 启动时必读 | `references/design-principles.md` | 架构决策 / 仿生运动三法则 / 材质 / 音效 / 排版 / 三大反模式 / Ganzfeld 模式（共 12 节） |
| STEP 4 生成前必读 | `references/code-templates.md` | 防御性骨架 / 四大程序化模型 A-D / FSM 代码 / 交互模板 / 调色板预设 / 15 项质量清单 |
| 确认含音效后按需读 | `references/audio-engine.md` | Web Audio 合成配方（零音频文件，含验证版引擎封装）|
| 需要可复现/可探索时按需读 | `references/seeded-exploration.md` | Seeded randomness / Seed 导航面板 / 参数 slider 面板 / 可分享 URL |

## 不变项 vs 可变项

每次生成前必读——把创造力集中在可变项上，不在不变项上犹豫。

### 不可变（Fixed · 每次照做）

| 不变项 | 规则 |
|--------|------|
| 像素美学 | 纯像素渲染，禁用抗锯齿/模糊/矢量混合 |
| Frutiger Aero 调色 | 毛玻璃 + 发光 + 柔和渐变，禁用暗黑/高饱和原色 |
| 画布尺寸 | 640×960 固定 |
| FSM 生命体上限 | ≤ 10 |
| Perlin 粒子上限 | ≤ 120 |
| 防御性骨架 | 从 `code-templates.md` 模板出发，不凭空写 |

### 可变（Variable · 每次创作决定）

| 可变项 | 范围 |
|--------|------|
| 场景类型 | 赛博宠物？像素养鱼？像素花园？像素森林？ |
| 生命体设计 | 形状 / 颜色 / 运动模式 / FSM 行为状态 |
| 核心交互 | 点击喂食？拖拽种植？长按安抚？滑动浏览？ |
| 音效配方 | 有无音效？什么音色？ |
| 是否可探索 | 一次性输出，还是带 seed 导航 + 参数面板？ |

## 边界规则

| 情况 | 处理 |
|------|------|
| 描述模糊（"做个好玩的"） | 反问：场景类型 / 空间形态 / 核心交互 |
| 生命体 > 10 个 | 告知上限，提议分批分文件生成 |
| 完整游戏 / 多页 / 非像素风 / Three.js | 说明边界后拒绝 |
| 含"沉浸 / 冥想 / 光浴 / 漂浮 / 光场" | 进入 **Ganzfeld 模式**（严守 design-principles.md §十二，禁止深色/惊吓/宗教色相漂移） |

**性能配额（超出即主动降档）：**

| 项目 | 上限 |
|------|------|
| FSM 生命体 | ≤ 10 |
| Perlin 粒子 | ≤ 120 |
| 固定画布尺寸 | 640×960 |

---

## 生成流程

### 概念种子（在打开浏览器之前）

像素生命不只是"好看的小东西"。每一个作品背后都有一个不直说的概念锚点：

| 场景 | 表面 | 概念种子 |
|------|------|---------|
| 赛博宠物 | "养一个电子宠物" | "它会一直在"——无条件的陪伴 |
| 像素盆栽 | "种一棵像素植物" | "你不在的时候它也在生长"——生命不需要观众 |
| 像素养鱼 | "养一缸像素鱼" | "它们不在乎你有没有在看"——另一个世界的平行存在 |
| 像素森林 | "一片像素树林" | "每棵树都有自己的节奏"——慢下来不是落后 |

**概念种子是：这个像素世界送给用户的一句话——不在标题里，不在说明里，在每一次交互的质感里。**

#### 命名（1-2 词）

给这个作品一个名字——一个压缩了整体美学方向的词。它不对外展示，它是生成过程中的北极星。

- 赛博宠物 + 无条件陪伴 → "Always Here"
- 像素盆栽 + 生命不需要观众 → "Still Growth"
- 像素养鱼 + 平行存在 → "Another Tank"

**一句话锚定这个像素世界的情绪温度和交互姿态。后面所有选择——颜色、运动、音效——都以这个名字为准。**

---

### STEP 0 — 视觉调研（新场景必做）

```bash
opencli browser research open "https://www.pinterest.com/search/pins/?q=<英文搜索词>"
opencli browser research state
```

观察形状特征、色彩、光影层次，直接转化为 STEP 2 的拆解决策。

> 若浏览器工具不可用，从用户描述推断形态特征，直接进 STEP 1。

### STEP 1 — 画幅、音效与场景模式

1. 让用户选画幅（3:4 / 9:16 / 1:1 / 4:3 / 16:9），用 CSS `aspect-ratio` 锁定
2. 询问是否包含音效（yes / no），含音效时后续需读 `references/audio-engine.md`
3. 确定场景模式（决定后续所有技术决策）：

| 场景模式 | 画布 | 特征 |
|---------|------|------|
| 封闭容器（穹顶/球体/玻璃瓶） | 固定 320×480 | Z-index 三明治 + `transform:scale` 适配屏幕 |
| 开放场景（全视口天空/水下） | 全视口 | 无玻璃壳，CSS 极光光斑漂浮 |
| Ganzfeld（已触发） | 全视口 | 高明度 Aero 光场 + Skyspace 透镜容器 |

### STEP 2 — 像素拆解

将用户描述逐层分解为像素基础元素 + 程序化模型：

```
用户描述
  → 场景模式
  → 主物体：有自主运动（鱼/宠物/史莱姆）→ FSM 三态（Wander/Chase/Flee）+ Perlin noise 驱动
             无自主运动（植物/摆件/珊瑚）→ React-only（交互触发单次反馈动画）
  → 副物体：至少选 2 种 A-D 程序化模型（如 A水草 + C珊瑚礁）
  → 背景：全视口 Aero 渐变 + 极光光斑
```

- 气泡必须用 `drawAeroBubble()`（偏移高光正圆），禁用 `rect()` 圆角替代
- 调色板从 `code-templates.md` 预设数组（WARM / COOL / NEON）取，禁止对单个物体随机 RGB

### STEP 3 — 技术决策（5 项，逐一明确后才写代码）

| 决策项 | 选项 |
|--------|------|
| 画布类型 | 固定 320×480 / 全视口 |
| 运动模式 | FSM Wander/Chase/Flee / React-only |
| 玻璃类型 | 穹顶 / 球体 / Skyspace 透镜（Ganzfeld）/ 无 |
| 粒子 | Perlin 漩涡 / 下落 / 拖影残像（Ganzfeld：`fill(10,8,20,12)` 替代 `clear()`）/ 无 |
| 音效 | 交互 chime（默认）/ 174Hz 三角波底噪 / 432+216Hz 颂钵（Ganzfeld）|

> 含音效时：读 `references/audio-engine.md`。AudioContext 在首次用户交互后 `resume()`，masterGain 起始值 0 淡入防爆音。

### STEP 4 — 生成

读 `references/code-templates.md`（防御性骨架 + 程序化模型代码 + 15 项质量清单）后生成。

**每个 HTML 文件开头必须写 META 注释头**（`<!DOCTYPE html>` 之后、`<html>` 之前）：

```html
<!--
  Title: <场景名>
  Summary: <主角 + 核心交互，一句话>
  Tech: p5.js, Canvas, CSS Glassmorphism, Web Audio API
  Keywords: <pixel, 场景关键词>
  Render: <fullViewport | fixedCanvas>
  Audio: <yes | no>
  Touch: <singleTap=行为, doubleTap=行为>
  Dependencies: p5.js 1.9.0
  Repo: healing-visual-lab
-->
```

注意：
- 固定画布只用 `noSmooth()`（不加 `pixelDensity(1)`，高 DPI 下会发虚）
- 全视口用 `pixelDensity(1)` + `noSmooth()`，`windowResized` 中两者都重置

### STEP 5 — 质检

```bash
mkdir -p ~/Documents/h5
python3 scripts/validate.py <文件.html>   # 内含 JS 语法检查，全绿才继续
```

若报错，逐条修复后重跑，**全绿才进入 STEP 6**。

### STEP 6 — 实测交付

调用 `/verify` 打开浏览器，确认：
- 单击 / 双击交互有视觉 + 听觉双反馈，两者不冲突
- 生命体运动有 Perlin 平滑感（无苍蝇乱撞的机械跳跃）
- 移动端 touch 不触发默认页面滚动

**交付后固定输出格式（不多不少）：**

```
文件：~/Documents/h5/<文件名>.html

操作说明：
• 单击：<行为>
• 双击：<行为>
[• 拖拽：<行为>（有则加）]

[首次点击页面激活声音，建议佩戴耳机。（含音效则加）]
```

不解释代码实现，不列技术栈，不写"我已完成"。
