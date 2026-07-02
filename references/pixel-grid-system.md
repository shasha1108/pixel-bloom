# Pixel Grid System — 五维像素完整性规范

> **核心哲学**：像素不是限制，是真值的单位。Frutiger Aero 是通透光感，像素艺术是诚实约束。融合意味着：每个像素都有意图，每个颜色都来自约束调色板，每个光晕都由离散层构建（非连续模糊）。
>
> 本文件定义 pixel-bloom 的像素完整性五维体系。与 `design-principles.md §一~§二` 六大铁律互补——铁律 1-5 管架构/管线/履约/美学/确定性，铁律 6 管**像素网格纯度**。

---

## I. 网格纯洁度指标（Grid Metrics & Integer Constraint）

### PX 基准像素单位

```
const PX = 2;  // 默认值。小画布(<400px宽)用3，大画布(>1200px宽)用4
```

所有坐标、尺寸、线宽必须是 `PX` 的整数倍。没有例外。

### 整数吸附公式

```javascript
function snap(v) { return Math.round(v / PX) * PX; }
function snapVec(x, y) { return { x: snap(x), y: snap(y) }; }
```

**使用位置**：仅在 `draw()` 渲染时调用 `snap()`。物理计算保持浮点数精度（见 §IV）。

### 双重像素锐利保险

```javascript
// setup() 中
noSmooth();                                          // p5.js 禁用平滑
const ctx = drawingContext;
ctx.imageSmoothingEnabled = false;                   // Canvas2D 原生层禁用

// CSS 中
canvas { image-rendering: pixelated; }                // 浏览器层禁用
```

**铁律**：三者缺一不可。`noSmooth()` 处理 p5.js 内部纹理，`imageSmoothingEnabled` 处理 Canvas2D 原生调用，`image-rendering: pixelated` 处理 CSS 缩放。

### Canvas 尺寸约束

```javascript
// 固定画布：CW 和 CH 必须是 PX 的整数倍
const CW = 640, CH = 960;  // 640 % 2 === 0, 960 % 2 === 0 ✓
createCanvas(CW, CH);
```

### 禁止清单

- ❌ 亚像素描边（`lineWidth: 0.5` / `strokeWeight(0.5)`）
- ❌ 非整数 `scale()`（`scale(1.5)` 产生 1.5× 像素 = mixel）
- ❌ `translate()` 传入非整数坐标（未包裹 `round()` / `snap()`）
- ❌ `rotate()` 使用非 90° 倍数的角度（见 §V ANTI-4）

---

## II. 拟物像素化法则（Pixel Skeuomorphism Rules）

> 以下 6 条规则从 Saint11 (Pedro Medeiros) "Basic Shading" (Article 4) 直接提取，结合 Frutiger Aero 材质需求转化为像素断言。

### 规则 1：平面着色 — 一个平面 = 一个颜色

Saint11: "Flat faces must use uniform color across their entire surface."

```
【平面着色法则】平/硬表面禁止颜色渐变。一个平面 → 一种纯色 fill()。
仅曲面（球/柱/锥/贝塞尔瓶身）可使用色阶过渡。
```

### 规则 2：曲面着色 — 3-5 级离散色阶

Saint11: "Rounded shapes can employ color ramps... keep variation to a minimum."

```
【曲面着色法则】曲面用 3-5 级离散色阶（每级宽度 = PX 的整数倍），非连续渐变。
禁止使用 createLinearGradient() 在像素精灵上产生连续色调。
```

### 规则 3：明暗过渡 — ≤ 2 PX 锐利切变

Saint11: "In pixel art we favor sharp transitions to avoid banding."

```
【明暗过渡法则】亮面→暗面过渡区域 ≤ 2 PX 宽。
过渡区只使用 1 个中间色，不产生超过 3 色的渐宽带（= banding）。
```

### 规则 4：高光峰值 — ≤ 2 PX 宽，纯白

Saint11: "Specular highlight: the brightest spot... small and focused on glossy surfaces."

```
【高光峰值法则】光滑表面高光 ≤ 2 PX 宽，颜色 #FFFFFF。
粗糙表面（木头/软木塞/土地）无高光。
高光位置 = 光源方向最近的曲面法线指向处。
```

### 规则 5：边缘光 — 1 PX 背光亮边

Saint11: "Rim light: looks like a bright outline, usually cast by a secondary, dimmer light."

```
【边缘光法则】背光物体外轮廓：1 PX 宽亮边。
颜色：rgba(255, 255, 255, 0.4-0.6)。
位置：物体远离主光源的一侧轮廓。
```

### 规则 6：枕形着色禁止

Saint11: "Pillow shading happens from shading with no clear light source... generic shadow around the outlines."

```
【枕形着色反模式】禁止：无明确光源方向 → 围绕物体轮廓均匀加暗边。
正解：先定义光源方向（如左上 45°），再按光源做定向明暗。
```

**延伸阅读**：
- Saint11 (Pedro Medeiros): *Pixel Art Tutorials — Basic Shading, Glass, Water & Translucent* (`saint11.art/pixel_art_articles/`)
- Brandon James Greer (YouTube): 1px 菲涅尔边缘与 2px 阶梯弧线高光画法
- Lospec Palette List (`lospec.com`): 16 色/32 色 Aero 调色板参考 — 青蓝 `#a0f0ff`、草绿 `#80e040`

### 玻璃容器特定规则

与 `design-principles.md §四` 三榻饼管线配合：

| 规则 | 像素约束 |
|------|---------|
| 玻璃壁厚 | ≥ 2 PX（< 2 PX = 线框而非玻璃容器） |
| 菲涅尔描边 | 1 PX 深绿描边 + 不等宽（边缘最粗 → 中心消失） |
| 曲面高光带 | 2 PX 高条纹，阶梯状排列（像素格对齐，禁斜线锯齿） |
| 内发光 | Bayer 抖动网点填充（见 §III），禁止 `createRadialGradient()` |

---

## III. 色彩与抖动标准（Color & Dithering Standard）

### Bayer 有序抖动矩阵

**Bayer 2×2（最小矩阵）**：

```javascript
const BAYER_2X2 = [[0, 2], [3, 1]]; // 归一化: 除以4
```

适合极低分辨率像素画（< 64×64）或需要粗粒度抖动的场景。

**Bayer 4×4（推荐默认）**：

```javascript
const BAYER_4X4 = [
  [ 0,  8,  2, 10],
  [12,  4, 14,  6],
  [ 3, 11,  1,  9],
  [15,  7, 13,  5]
];  // 归一化: 除以 16 → [0, 1] 阈值范围
```

**Bayer 8×8（高精度场景）**：

```javascript
const BAYER_8X8 = [
  [ 0, 32,  8, 40,  2, 34, 10, 42],
  [48, 16, 56, 24, 50, 18, 58, 26],
  [12, 44,  4, 36, 14, 46,  6, 38],
  [60, 28, 52, 20, 62, 30, 54, 22],
  [ 3, 35, 11, 43,  1, 33,  9, 41],
  [51, 19, 59, 27, 49, 17, 57, 25],
  [15, 47,  7, 39, 13, 45,  5, 37],
  [63, 31, 55, 23, 61, 29, 53, 21]
];  // 归一化: 除以 64 → [0, 1] 阈值范围
```

### 有序抖动函数（O(1)，draw() 中实时可用）

```javascript
/**
 * 两色之间用 Bayer 矩阵做像素抖动选择。
 * @param {number} x, y — 像素坐标（整数值，非 PX 单位）
 * @param {number} t — 混合因子 [0,1]，0 = 全 colorA，1 = 全 colorB
 * @param {string} colorA, colorB — hex 颜色字符串
 * @param {number[][]} matrix — Bayer 矩阵，默认 4×4
 * @returns {string} 选中的 hex 颜色
 */
function orderedDither(x, y, t, colorA, colorB, matrix = BAYER_4X4) {
  const N = matrix.length;
  const threshold = matrix[y % N][x % N] / (N * N);
  return threshold < t ? colorA : colorB;
}

// 用法示例 — 像素地形深度渐变：
// fill(orderedDither(bx, by, depthT, '#70d0f0', '#1070a0'));
```

### Floyd-Steinberg 误差扩散（参考算法）

**核权重**（已验证）：向右 7/16，左下 3/16，向下 5/16，右下 1/16。

**⚠️ 性能警告**：Floyd-Steinberg 需要遍历像素缓冲区 + 读写误差数组，复杂度 O(W×H)。**只能用于 `setup()` 中一次性预计算**（如预生成背景地形像素图），禁止在 `draw()` 循环中每帧执行。

**何时用**：需要高质量静态抖动（地形、天空、大型背景）→ Floyd-Steinberg 在 `setup()` 中一次计算。需要实时渐变（水面深度、动态光影）→ Bayer 有序抖动。

### 抖动决策树

```
需要渐变效果？
├── 背景/地形（静态）→ Floyd-Steinberg，setup() 一次性计算
├── 水面/光影（实时）→ Bayer 有序抖动，draw() 每帧 O(1)
├── 玻璃高光 → 永不抖动！使用纯白 #FFFFFF + SCREEN 混合
├── 像素轮廓/文字 → 永不抖动！纯色 fill + snap 坐标
└── 大气光斑/Bokeh → CSS 层处理（filter: blur），非 Canvas 抖动
```

### 控制台调色板参考

| 来源 | 色系描述 | 典型 HEX（近似值） |
|------|---------|-------------------|
| NDS/DSi 系统菜单 | 白-灰-青绿 | `#FFFFFF`, `#D0D0D0`, `#A0A0A0`, `#50B8B0`, `#2878D0` |
| PSP XMB 波浪（默认） | 暗底 + 青绿+橙 | `#1A1A2E`, `#00BFFF`, `#7FFF00`, `#FF8C00` |
| Wii 频道菜单 | 白底圆角 + 蓝绿红 | `#F8F8F8`, `#4AA0F0`, `#50D050`, `#F04040` |
| Web 2.0 Glossy Badge | 亮底 + 光泽弧线 | `#F8F8F8`, `#0099FF`, `#66CC00`, `#FF9900` |

> 完整控制台调色板数组见 `assets/palettes.json`。上述值为色系参考，精确值需从 Spriters Resource 采样。

---

## IV. 像素物理与运动（Pixel Physics & Motion）

### 浮点计算 + 整数渲染 — 唯一正确模式

与 `code-templates.md §防坑铁律 1` 一致：

```javascript
// ✅ 正确
entity.x += entity.vx;              // 浮点物理累积
entity.y += entity.vy;
translate(round(entity.x), round(entity.y)); // 仅渲染时网格对齐

// ❌ 错误
entity.x = floor(entity.x / PX) * PX; // 直接 snap 状态 → 一格一格跳跃
```

### 像素化波浪方程

```javascript
// 通用公式 — 适用于水面、旗帜、水草摆动等
// y = snap(baseY + sin(x * freq + phase) * amplitude * PX)
//
// 完整海浪系统见 references/ocean-pixels.md
```

### 像素字体渲染

**首选**：Ark Pixel（方舟像素字体）。GitHub: `TakWolf/ark-pixel-font`。`.woff2` 格式可用。12px 为主要开发目标。

**备选**：
| 字体 | 语言 | 特性 | 适用场景 |
|------|------|------|---------|
| **ZPix**（站酷像素体） | 中文/英文 | 清新唯美，最契合 Frutiger Aero 气质 | 中文像素场景首选，必须在 12px 整数倍渲染 |
| **Ark Pixel**（方舟像素体） | 中文/日文/英文 | 多字重开源像素体 | 标题 + 微型文字 |
| **Fusion Pixel**（融合像素体） | 中文/日文/英文 | 8/10/12px 三尺寸 | 过渡方案，覆盖全尺寸 |
| **Pixel Operator** | 英文/数字 | 复古 Vista/Win98 系统风格 | 英文界面/数字显示/终端拟物 |
| **Unifont** | 全球多语言 | 全覆盖点阵字 | 代码/终端拟物界面，全语言 fallback |

```css
/* CSS @font-face 加载（CDN 或 self-host） */
@font-face {
  font-family: 'Ark Pixel';
  src: url('ark-pixel-12px-proportional.woff2') format('woff2');
}

/* 像素文字防虚化 */
.pixel-text {
  font-family: 'Ark Pixel', 'ZPix', monospace;
  -webkit-font-smoothing: none;
  font-smooth: never;
}
```

**⚠️ 局限性**：Canvas `fillText()` 的抗锯齿由 OS + 浏览器控制，`imageSmoothingEnabled = false` **不影响文本渲染**。真正消除文本抗锯齿的唯一方法是使用像素字体的字形本身就是像素化的（Ark Pixel 满足此条件）。

**字体尺寸约束**：字体大小必须是字体基础尺寸的整数倍（如 Ark Pixel 12px → 只能用 12/24/36px，不允许 13/25/37px）。

---

## V. 质量门禁 — 7 条像素反模式

> 以下 7 条是 pixel-bloom 像素完整性的一票否决项。与 `design-principles.md §十` 三大架构反模式互补——§十 管架构，本 §V 管像素纯度。

| # | 反模式 | 检测方式 | 级别 |
|---|--------|---------|------|
| **ANTI-1** | `createLinearGradient()` / `createRadialGradient()` 用于像素精灵 | 搜索渐变 API + 判断使用上下文 | WARN |
| **ANTI-2** | Mixels：`scale()` 参数为非整数（如 `scale(1.5)`、`scale(someVar)`） | 正则 `scale(` + 参数分析 | WARN |
| **ANTI-3** | CSS `filter: blur()` 或 `backdrop-filter` 出现在像素 Canvas 上层（z-index ≥ 3） | 正则搜索 CSS 规则块 | FATAL |
| **ANTI-4** | `rotate()` 角度 ≠ 0, PI/2, PI, 3×PI/2 的倍数 | 正则 `rotate(` + 参数分析 | WARN |
| **ANTI-5** | `translate()` 未包裹 `Math.round()` / `snap()` | 正则 `translate(` | WARN |
| **ANTI-6** | 抗锯齿文字覆盖像素艺术 — Canvas fillText 未使用像素字体 | 搜索 `fillText`/`text(` + 检查字体声明 | WARN |
| **ANTI-7** | 连续 alpha 混合在硬像素边缘 — 像素边缘透明度 ≠ 0 或 1 | 检查 `rgba(` 中 alpha 值非 0/1 且无抖动上下文 | WARN |

**执行纪律**：
- ANTI-3 致命 → 必须修复才能交付（CSS blur 抹杀所有像素网格，画质不可逆）
- ANTI-1/2/4/5/6/7 警告 → 逐项目测确认。正则无法区分合法/非法使用场景

---

## VI. 架构模板（Architecture Template）

### 美学哲学（Aesthetic Philosophy）

```
Fusion of Mid-2000s Web 2.0 Skeuomorphism (Gloss, Glass, Water, Sunshine)
with Strict Retro Pixel Art.

"Precision Grid, Volumetric Gloss"
——用严苛的像素网格，伪造无限通透的光影。
```

**风格参考**：Frutiger Aero 核心意象 — Glass, Water, Lens Flare, Bubbles, Gloss, Aqua, Sky, Meadow。见 Aesthetics Fandom: Frutiger Aero 词条 (`aesthetics.fandom.com`)。

### 技术铁律（Technical Imperatives）

| 铁律 | 实现 |
|------|------|
| 强制性 `PX` 网格单位 | `const PX = 2`，所有尺寸/坐标必须是 PX 整数倍 |
| 强制性 `noSmooth()` + `imageSmoothingEnabled = false` + `image-rendering: pixelated` | 三个层面全部禁用抗锯齿 |
| 零 CSS blur 覆盖像素元素 | `backdrop-filter` 仅允许 z=2 `.glass-bg`；`filter: blur()` 绝不允许在 z≥3 |
| 零 Mixel | 所有元素共享同一个 PX scale。`scale()` 只能传入整数 |

### 像素拟物管线（Pixel Skeuomorphism Pipeline）

```
1. 1px 外轮廓描边（深色，比填充暗 40-60%）
2. 扁平纯色填充（平面）或 3-5 级离散色阶（曲面）
3. 1px 内高光（光源侧，白/浅色）
4. 1px 边缘光（背光侧，半透明白）
5. 2px 阶梯状高光弧（光源侧，纯白，步进对齐）
6. Bayer 抖动网点（内发光/深度渐变，非径向渐变）
7. SCREEN 混合高光叠加（仅在完成上述后叠加，不替代上述步骤）
```

### 物理与运动规则（Physics & Motion Rules）

```
1. 亚像素浮点计算（vx, vy 为浮点数）
2. 整数网格渲染吸附（translate(round(x), round(y))）
3. Perlin noise 驱动连续运动（非 random() 抖动）
4. FSM 状态机驱动行为切换（≥ 3 态）
5. 速度/加速度以 PX/frame 为单位
```

---

## VII. Bloom & Glow 光效姿势库（工业级图形学标准）

以下 3 套姿势直接对标工业级图形学管线，覆盖 pixel-bloom 的全部发光需求。

### 光效分类体系

```
┌──────────────────────────────────────────────────────────┐
│              工业级 Glow / Bloom 姿势库                   │
└──────────────────────────────────────────────────────────┘
                            │
  ┌─────────────────────────┼──────────────────────────────┐
  ▼                         ▼                              ▼
【姿势 A】                 【姿势 B】                      【姿势 C】
2D 对象级光晕               Canvas 2D 全屏 Bloom            像素风格光晕
指数衰减径向渐变加色法      离屏下采样 + Blur 叠加           Bayer 抖动光晕
                           Offscreen Downsampled Bloom      Bayer Dithered Pixel Glow
```

### 姿势 A：指数衰减径向渐变加色法（2D 对象级标准）

**适用场景**：萤火虫、发光蝴蝶、魔法粒子、太阳耀斑、单个气泡发光。

**原理**：真实光强衰减遵循反比平方律（$I \propto 1/r^2$）或指数衰减（$I = I_0 \cdot e^{-k \cdot r}$）。使用 `createRadialGradient` 配合 `globalCompositeOperation = 'lighter'`（加色混合——光能叠加，非透明度混合）。

**权威来源**：W3C HTML Canvas 2D Context Specification — `globalCompositeOperation: 'lighter'` 定义加色混合语义（像素值直接相加而非 alpha 混合）。这是 PixiJS、Phaser 等 2D 引擎处理单体发光粒子的标准公式。

**关键区别**：
- `'lighter'`（加色）→ 光能叠加，两个光源交叠处更亮（物理正确）
- `'screen'`（滤色）→ 反转-乘-反转，比 `'lighter'` 暗，用于高光叠加

**代码见** `code-templates.md §Bloom/Glow 光效姿势库 → 姿势 A`。

### 姿势 B：离屏下采样 Blur 叠加 Bloom 管线（全屏级）

**适用场景**：画面中有多个发光体（如售货机+信号灯+萤火虫），希望光线融为一体并漫延到暗部。

**原理（3 步管线）**：
1. **下采样**（Downsample）：建立 1/4 或 1/8 尺寸的离屏画布（Offscreen Canvas），将主画布绘制到离屏画布
2. **模糊**（Blur）：利用 `ctx.filter = 'blur(Npx)'` 模糊低分辨率离屏画布（性能极高——模糊 1/4 画布 = 模糊原画 ~4% 的像素数）
3. **叠加**（Composite）：将模糊后的离屏画布用 `'lighter'` 加色模式放大叠加回原画布

**权威来源**：这是现代 Web 2D 引擎（PixiJS v5+ blur filter pipeline、Phaser 3 post-FX）在不使用 WebGL Shader 时实现**真实全屏 Bloom** 的标准管线。

**代码见** `code-templates.md §Bloom/Glow 光效姿势库 → 姿势 B`。

### 姿势 C：Bayer 抖动光晕（Frutiger Aero × 像素风专属）

**适用场景**：pixel-bloom 像素艺术场景的专属光效——像素玻璃高光扩散、像素萤火虫外发光、像素魔法阵光芒。

**原理**：光强不使用平滑的 Alpha 衰减，而是映射到 **Bayer 4×4 / 8×8 有序抖动矩阵**。中心是纯色像素（光强最高），边缘越远，Bayer 矩阵阈值筛选后的点阵密度越稀疏——产生"像素点逐渐稀疏"的光晕衰减效果，而非连续模糊。

**为什么是像素风权威方案**：NDS、GBA、Wii 等 2000s 掌机的像素界面中，表现高光和光晕的标准方法——硬件不支持浮点 Alpha 混合或 Shader Bloom，只能通过抖动网点（Dither Pattern）模拟光衰减。这与 pixel-bloom 的 Frutiger Aero × 像素风定位完全一致。

**代码见** `code-templates.md §Bloom/Glow 光效姿势库 → 姿势 C`。

### 姿势选择决策树

```
光效需求：
├── 单个发光对象（粒子/气泡/萤火虫）→ 姿势 A（指数衰减加色法）
├── 全屏多光源融合（整个场景的辉光弥漫）→ 姿势 B（离屏 Bloom 管线）
├── 像素艺术发光（像素玻璃/像素魔法阵/像素萤火虫）→ 姿势 C（Bayer 抖动光晕）
└── CSS 背景光斑（不涉及 Canvas）→ CSS filter:blur()（见 §III 抖动决策树）
```

### 权威文献背书

| 算法 / 姿势 | 出处 | 核心人物 / 机构 |
|------------|------|---------------|
| `globalCompositeOperation: 'lighter'` 加色混合 | W3C HTML Canvas 2D Context Specification | W3C / MDN |
| 指数衰减光晕（Inverse-Square / Exponential Attenuation） | 基础物理学 — 点光源辐照度 | — |
| 离屏下采样 Blur（Offscreen Downsampled Blur） | PixiJS v5+ / Phaser 3 后处理管线 | Goodboy Digital / Photon Storm |
| Dual Filter Kawase Bloom | *Bandwidth-Efficient Rendering*, SIGGRAPH 2015 | Marius Bjørge (ARM) |
| Kawase Blur（Kawase Bloom 前身） | *Frame Buffer Postprocessing Effects in DOUBLE-S.T.EAL*, GDC 2003 | Masaki Kawase |
| Next-Gen Bloom Pipeline（现代 Bloom 参考） | *Next-Generation Post-Processing in Call of Duty*, SIGGRAPH 2014 | Jorge Jimenez |
| Bayer 有序抖动矩阵 | Bryce Bayer, *Color Imaging Array*, US Patent 1976 | Eastman Kodak |

---

## VIII. 像素折射姿势库（Pixel Refraction — 图形学 × 像素画规范）

折射在物理图形学中使用斯涅尔定律（Snell's Law: $n_1\sin\theta_1 = n_2\sin\theta_2$）+ 法线贴图 + 位移映射。在 2D Canvas / 像素风中，以下是经过图形学验证的平替方案。

### 折射姿势分类体系

```
┌──────────────────────────────────────────────────────────┐
│              权威像素与 2D 折射姿势库                    │
└──────────────────────────────────────────────────────────┘
                            │
  ┌─────────────────────────┼─────────────────────────┐
  ▼                         ▼                         ▼
【姿势 1】                 【姿势 2】                  【姿势 3】
双重遮罩位移与透镜缩放     像素网格色散折射             Saint11 像素折射三大定律
2D Canvas 黄金标准          Chromatic Aberration         点阵艺术规范
(Clip + Translate + Scale)  Dither Displacement           (1px 断线/边缘压缩/全反射)
```

### 姿势 1：双重遮罩位移与透镜缩放（2D Canvas 黄金标准）

**适用场景**：玻璃瓶/水族箱/水滴透镜/水晶球——任何透明容器内部的内容物。

**原理**：折射的本质不是"在玻璃里画新东西"，而是**将玻璃背后的背景内容裁切出来，进行偏移（Offset）与放大（Scale），再叠加玻璃 tint**。

**管线（3 步）**：
1. `ctx.save()` → `glassPathFunc()` → `ctx.clip()` — 裁切玻璃形状
2. `ctx.translate(dx, dy)` + `ctx.scale(1.04, 1.04)` — 对裁切区域进行位移+透镜放大
3. 重新绘制背景 + 叠加 `rgba(180,240,255,0.15)` tint

**为什么权威**：这是 Flash/Animate 时代至 PixiJS 2D Displacement Filter 的标准管线——在不遍历逐个像素的情况下，唯一能模拟物理折射的通用方案。

**代码见** `code-templates.md §Bloom/Glow 光效姿势库 → 折射姿势 1`。

### 姿势 2：像素网格法线位移与色散（Chromatic Aberration）

**适用场景**：像素风高精场景——玻璃边缘的彩虹色散、钻石/水晶的 RGB 分光。

**原理**：
- **位移公式**：$\text{SamplePos} = \text{PixelPos} + \vec{N}(x, y) \cdot \text{RefractionAmount}$（根据曲面法线方向推开采样像素）
- **色散**：RGB 三个通道位移距离不同（红 +1PX，绿 0PX，蓝 -1PX），在像素网格上产生玻璃边缘经典的**彩虹色散边缘**

**为什么权威**：这就是 3D 渲染中 **Screen-Space Refraction (SSR)** 的标准数学模型。GPU Gems 1 Chapter 8 描述色散模拟，GPU Gems 2 Chapter 19 描述 2D 位移折射。

**代码见** `code-templates.md §Bloom/Glow 光效姿势库 → 折射姿势 2`。

### 姿势 3：Saint11 像素画折射三大定律（点阵艺术规范）

**适用场景**：16×16 / 32×32 纯手工像素画、像素风 Sprite 贴图、低分辨率像素场景。

**三大定律**（从 Saint11 像素画玻璃/水体教程提取）：

| # | 定律 | 规范 |
|---|------|------|
| **定律 1** | **1px 平行错位法则** | 透过水/玻璃看到的线条，在交界处必须断开并平行平移 1 个 PX 单元。禁止线条顺畅无缝穿过玻璃边界 |
| **定律 2** | **边缘压缩与中心膨胀** | 圆球/圆柱玻璃：中心像素被拉宽（≥ 2 PX），边缘像素被挤压变窄（≤ 1 PX）。模拟 Fisheye 畸变 |
| **定律 3** | **全反射边界** | 临界角处的像素不显示背景——显示为 1 PX 的反色光线或深色暗边（菲涅尔全反射的像素化表达） |

**应用断言（注入生成 Prompt）**：
```markdown
当线段或物体穿过玻璃/水面边界时：
1. 禁止：线段无缝穿过交界处（无视折射物理）
2. 强制：交界处像素线发生 1-2 PX 阶梯断裂
3. 公式：玻璃内线段 X = 玻璃外线段 X + sign(曲面法线X) × PX
4. 交界点填充为 1 PX 的亮白高光点
```

### 折射姿势选择决策树

```
折射需求：
├── Canvas 2D 玻璃容器（漂流瓶/水族箱/水晶球）
│   └── 姿势 1（双重遮罩位移缩放）— 管线级，60fps 可用
├── 像素风高精折射（钻石/水晶边缘彩虹边）
│   └── 姿势 2（色散位移映射）— ImageData 逐像素处理
├── 低分辨率像素 Sprite（16×16～32×32 手工像素画）
│   └── 姿势 3（Saint11 三大定律）— 纯逻辑断言
└── 仅需"物体在水下看起来略有偏移"
    └── 姿势 1 简化版（仅 translate(1, -1)，不 scale）
```

### 权威文献背书

| 算法 / 姿势 | 出处 | 核心人物 / 机构 |
|------------|------|---------------|
| 斯涅尔定律（Snell's Law） | 基础物理学 — 折射角计算 | Willebrord Snellius (1621) |
| 2D Displacement Refraction | *GPU Gems 2 — Chapter 19: Generic Refraction Simulation* | NVIDIA |
| Chromatic Aberration 色散 | *GPU Gems 1 — Chapter 8: Simulating Diffraction* | NVIDIA |
| Screen-Space Refraction (SSR) | 现代 3D 渲染管线标准后处理 | — |
| Canvas 2D Clip + Transform 折射 | W3C HTML Canvas 2D Context Specification | W3C / MDN |
| Saint11 像素折射三大定律 | *Pixel Art Tutorials — Glass, Water & Translucent Objects* | Pedro Medeiros (Saint11) |
| Pokemon Emerald 水体像素 | The Spriters Resource: `GBA → Pokemon Emerald` — 经典 2D 水面折射、波浪泡沫与浅滩点阵 | Game Freak / Nintendo |
| DeviantArt / Archive.org 像素徽章 | `Pixel Web 2.0 Badge`, `Pixel Glass Icon` — 水晶胶囊按钮、微型发光徽章网格结构 | Web 2.0 社区 |

---

## 引用索引

| 主题 | 详细内容位置 |
|------|------------|
| 防御性骨架 + wrapper 架构 | `code-templates.md §防御性前端骨架` |
| 玻璃容器三榻饼管线 | `code-templates.md §玻璃容器渲染` |
| 六大铁律完整规范 | `design-principles.md §一~§二` |
| 架构反模式（Y轴/坐标分离/假绿） | `design-principles.md §十` |
| 屏幕像素锚定（最小可见尺寸） | `design-principles.md §十四` |
| 对抗式检查 SOP | `design-principles.md §十五` |
| 海洋波浪完整系统 | `ocean-pixels.md` |
| 程序化植被系统 | `vegetation-system.md` |
| 像素字体（Ark Pixel） | `https://github.com/TakWolf/ark-pixel-font` |
| Bayer 抖动（Surma Ditherpunk） | `https://surma.dev/things/ditherpunk/` |
| Saint11 像素画教程 | `https://saint11.art/pixel_art_articles/article4/` |
| Brandon James Greer 像素高光 | YouTube: `Brandon James Greer Pixel Art Glass/Water` |
| Lospec 调色板数据库 | `https://lospec.com/palette-list` |
| Aesthetics Fandom (Frutiger Aero) | `https://aesthetics.fandom.com/wiki/Frutiger_Aero` |
| The Spriters Resource | `https://spriters-resource.com` (DS/PSP/GBA UI + Pokemon Emerald) |
| PSP XMB 月份主题色 | `https://www.psdevwiki.com/psp/XrossMediaBar` |
| Bloom/Glow/折射/字体代码模板 | `code-templates.md §Bloom/Glow 光效姿势库 + §像素折射姿势库 + §像素实体系统` |
