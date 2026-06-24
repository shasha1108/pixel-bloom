---
name: pixel-aero
description: >
  Use when the user wants to create a pixel-art interactive H5 page with Frutiger Aero glass aesthetics —
  cyber pets, cyber plants, digital aquariums, pixel terrariums, or any scenario where pixel lifeforms
  live inside a frosted glass container. Triggers on: "像素养鱼", "赛博宠物", "像素盆栽", "玻璃水族箱",
  "pixel aquarium", "digital pet", "Frutiger Aero pixel", "pixel art glass", "像素 + 毛玻璃",
  "玻璃瓶里的像素", or any request combining pixel art with glassmorphism/Frutiger Aero visual style.
  Do NOT trigger for: non-pixel art, Three.js 3D scenes, pure CSS animations without canvas,
  or static pixel art without interactivity.
---

# Pixel × Frutiger Aero

生成 p5.js 像素渲染 + Frutiger Aero 玻璃美学的独立 H5 页面。

> **启动时阅读 `references/methods.md`**（架构/形状/运动/材质/交互/色彩/音效/排版/反模式/光空间共 12 节，一次读完覆盖所有场景）。

## 边界规则

- **范围上限**：单页 H5，最多 10 个自主生命体，超过→建议分批
- **拒绝场景**：完整游戏、多页应用、非像素风格→告知范围并拒绝
- **信息不足时反问**：用户只说"做个好玩的"→反问场景、容器、交互三要素
- **输出位置**：所有 H5 文件写到 `~/Documents/h5/`

---

## 生成流程

### 0. 视觉调研（新场景必做）

用 OpenCLI 浏览器搜索真实参考图，理解"这个东西长什么样"后再写代码：

```bash
opencli browser research open "https://www.pinterest.com/search/pins/?q=<英文搜索词>"
opencli browser research state   # 获取搜索结果 DOM
```

搜索词要用英文（Pinterest 英文搜质量远高于中文）。找到参考图后观察：形状特征、色彩搭配、光影关系、细节层次。这些观察直接转化为生成决策。

### 1. 尺寸选择

先让用户选画幅（3:4/9:16/1:1/4:3/16:9/2:3/3:2），用 `aspect-ratio` 锁定。

### 2. 像素拆解

将用户描述的目标**逐层拆解为像素基础元素 + 程序化模型**：

```
用户描述 → 场景类型(封闭/开放/Ganzfeld) → 主物体拆解 → 副物体拆解 → 背景元素

拆解示例：
"悬浮松树 + 光环 + 玻璃球"
  → 场景：封闭玻璃球体（border-radius:50% 正方形）
  → 树干：模型A 竖条堆叠（棕色渐变调色板）
  → 树枝：模型A 斜向分叉堆叠
  → 树冠：模型C 三角聚落 + 绿色调色板
  → 光环：椭圆 + stroke + SCREEN 发光
  → 背景：全视口 Aero 渐变 + fixed 极光
```

**每种物体配一个独立调色板**（来自预设数组，不为每个像素 random RGB）。

### 3. 技术决策

基于拆解结果做 5 个决策：
- **画布类型**：固定画布（容器）/ 全视口（开放）/ **全视口光场**（Ganzfeld，methods.md §十二）
- **运动模式**：FSM（自主生命体）或 React-only（植物/摆件）
- **玻璃类型**：穹顶 / 球体 / Skyspace 透镜（Ganzfeld 模式） / 无玻璃
- **粒子类型**：Perlin 漩涡 / 下落 / 拖影残像（Ganzfeld 模式） / 无
- **音效**：drone 底噪 / 粉红噪音 + 双耳节拍（Ganzfeld 模式） / 交互 chime

### 4. 生成

遵循 `methods.md` 全部原则。固定画布用 CSS Z-index，开放场景用 JS 设。
交付前运行：`python3 scripts/validate.py <文件.html>`

### 5. 实测交付

调用 `/verify` 打开浏览器，逐项操作确认交互和渲染正确后才交付。
