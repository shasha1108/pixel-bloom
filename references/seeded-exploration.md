# Seeded Randomness + Parameter Exploration

让像素生命从"一次生成"升级为"可复现、可探索、可分享"的交互体验。

## 为什么需要 Seeded Randomness

p5.js 默认 `random()` 每次运行结果不同。用户说"刚才那个花园很好看，再来一次"——做不到。

**Seeded randomness 解决这个问题：相同 seed → 相同结果。** 用户：
- 可以用 seed 精确保存喜欢的布局（"记下来了，seed=42"）
- 可以 prev/next 浏览变体
- 可以把 seed 分享给别人，对方看到完全相同的花园

## 核心模式

```javascript
// 从 hash 或参数生成 seed
function getSeed() {
  const params = new URLSearchParams(window.location.search);
  const hash = params.get('seed');
  if (hash) return parseInt(hash, 10);
  return Math.floor(Math.random() * 100000);
}

let SEED = getSeed();

function setup() {
  createCanvas(CW, CH);  // CW/CH 由画幅比例决定，见 generation-workflow §STEP1
  randomSeed(SEED);
  noiseSeed(SEED);
  // 后续所有 random() / noise() 调用都由 SEED 决定
  generateGarden(SEED);
}

function generateGarden(seed) {
  randomSeed(seed);
  noiseSeed(seed);
  // 植物位置、颜色偏移、生长方向——全部 deterministic
}
```

**URL 参数持久化**：每次生成完把 seed 写进 URL，用户复制链接即保存。

```javascript
// 生成完成后更新 URL（不刷新页面）
const url = new URL(window.location);
url.searchParams.set('seed', SEED);
window.history.replaceState({}, '', url);
```

## Seed 导航面板

轻量版，适合 pixel-bloom 的玻璃态风格：

```html
<div class="seed-nav">
  <button id="btn-prev" onclick="changeSeed(-1)">◂ 上一个</button>
  <span class="seed-display">Seed: <strong id="seed-label">42</strong></span>
  <button id="btn-random" onclick="randomSeedJump()">🎲 随机</button>
  <button id="btn-next" onclick="changeSeed(1)">下一个 ▸</button>
</div>
```

```css
.seed-nav {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  padding: 10px 16px;
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  font-size: 13px; color: rgba(255,255,255,0.85);
}
.seed-nav button {
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.2);
  color: rgba(255,255,255,0.8);
  padding: 4px 12px; border-radius: 12px;
  font-size: 12px; cursor: pointer;
  transition: background 0.2s;
}
.seed-nav button:hover { background: rgba(255,255,255,0.22); }
.seed-display strong { font-family: monospace; }
```

```javascript
function changeSeed(delta) {
  SEED += delta;
  if (SEED < 0) SEED = 99999;
  if (SEED > 99999) SEED = 0;
  document.getElementById('seed-label').textContent = SEED;
  generateGarden(SEED);
  updateURL();
}

function randomSeedJump() {
  SEED = Math.floor(Math.random() * 100000);
  document.getElementById('seed-label').textContent = SEED;
  generateGarden(SEED);
  updateURL();
}
```

## 参数面板

当 pixel-bloom 场景允许用户调参（植物密度、颜色主题、粒子数量），提供 slider 控制：

```javascript
let params = {
  plantDensity: 0.5,   // 0–1
  colorTemp: 0.5,       // 0=cool, 1=warm
  growSpeed: 1.0,       // 0.5–2.0
  particleCount: 60,    // 20–120
};
```

```html
<div class="param-panel">
  <div class="control-group">
    <label>植物密度</label>
    <input type="range" id="plantDensity" min="0" max="1" step="0.05"
           value="0.5" oninput="updateParam('plantDensity', this.value)">
  </div>
  <div class="control-group">
    <label>色温</label>
    <input type="range" id="colorTemp" min="0" max="1" step="0.05"
           value="0.5" oninput="updateParam('colorTemp', this.value)">
  </div>
</div>
```

```css
.param-panel {
  display: flex; flex-direction: column; gap: 8px;
  padding: 12px 16px;
  background: rgba(255,255,255,0.1);
  backdrop-filter: blur(10px);
  border-radius: 16px;
}
.control-group { display: flex; align-items: center; gap: 8px; }
.control-group label {
  width: 64px; font-size: 11px; color: rgba(255,255,255,0.7);
}
.control-group input[type="range"] {
  flex: 1; accent-color: rgba(180,210,255,0.8);
}
```

```javascript
function updateParam(key, value) {
  params[key] = parseFloat(value);
  // 参数变更时实时重绘（或等待用户按"应用"按钮）
  generateGarden(SEED); // SEED 不变，参数变
}
```

**实时 vs 按需重绘**：slider 拖动时频繁重绘可能卡顿。两种策略——
- **轻量场景**（<50 生命体）：`oninput` 实时重绘
- **重量场景**（>50 生命体）：slider 只更新值，加一个"应用"按钮触发重绘

## 与现有参考文件的关系

| 能力 | 来源 |
|------|------|
| 程序化模型 A-D、FSM 代码 | `code-templates.md` — STEP 4 前必读 |
| 调色板 | `assets/palettes.json` — STEP 2 选色时查阅 |
| 架构决策、仿生运动、材质、反模式 | `design-principles.md` — 启动时必读 |
| **Seeded randomness、Seed 导航、参数面板** | 本文件 — 需要可复现/可探索时读取 |

## 使用时机

技能启动时判断：用户是否表达了"探索式"或"可分享"的意图？
- "帮我生成一个像素花园" → 不需要，一次性输出
- "我想要能换不同样式的" / "能不能保存我喜欢的那个" → 按需加载本文件
- "做一个赛博宠物，我想自己调颜色" → 按需加载本文件

## 质量检查

- [ ] `randomSeed(SEED)` + `noiseSeed(SEED)` 在 `setup()` 和 `generateX()` 中都有调用
- [ ] 每次生成后种子写入 URL（`history.replaceState`）
- [ ] prev/next 循环不越界（seed 范围 0–99999）
- [ ] 参数 slider 有明确 min/max/step
- [ ] 移动端触摸 slider 不触发画布交互

> 参数设计方法论见 `design-principles.md §十二`。

---

## 确定性逐元素变化模式

> 设计哲学源自 stylized-scene 的逐叶片 hash 变化。Pixel Bloom 场景中大量相似元素（50 棵树、100 个花瓣、80 个花粉粒子）——不能每个都用 `random()`（破坏种子可复现性），也不能全部相同（看起来像克隆）。

### 核心公式（p5.js 适配）

```javascript
// 轻量确定性 hash —— 用于逐元素变化（非加密）
function hf(n) {
  const x = Math.sin(n * 12.9898 + 7.373) * 43758.5453123;
  return x - Math.floor(x);
}

// 模式 1：振幅变化 （每棵树的摇摆幅度不同）
// 范围 65%-135% —— 有些树"硬"，有些"软"
const ampVar = 0.65 + hf(treeIdx + 7) * 0.7;
tree.swayAmplitude = BASE_SWAY * ampVar;

// 模式 2：亮度变化 （每棵树的颜色微调）
// 范围 ±15% —— 微妙但打破"克隆感"
const brightVar = 0.85 + hf(treeIdx + 13.37) * 0.3;
plantBaseColor = lerpColor(rootColor, tipColor, heightT);
plantBaseColor.setRed(constrain(plantBaseColor._getRed() * brightVar, 0, 255));

// 模式 3：确定性抖动 （位置/边缘不规则化）
// 范围 ±amount
function jitter(idx, amount) {
  return (hf(idx * 12.9898) - 0.5) * 2 * amount;
}
// 用法：植物初始位置微调——不是完美网格排列
plant.x = gridX + jitter(plantIdx, 3);  // ±3px 抖动

// 模式 4：多值解耦
// 不同用途的 hash 用不同偏移，确保值之间不相关
const PHASE_OFFSET = 0;
const AMP_OFFSET = 7;
const BRIGHT_OFFSET = 13.37;
const JITTER_OFFSET = 73;
```

### 在 `generateGarden(seed)` 中的集成

```javascript
function generateGarden(seed) {
  randomSeed(seed);   // p5.js 内置 —— 用于 rng() 序列
  noiseSeed(seed);    // p5.js 内置 —— 用于 noise() 场

  for (let i = 0; i < plantCount; i++) {
    // 场景结构决策（位置、物种选择）→ 用 rng()
    const sp = SPECIES[Math.floor(rng() * speciesKeys.length)];
    const baseX = rng() * gardenWidth;

    // 逐元素变化（振幅、亮度、颜色微调）→ 用 hash(i + OFFSET)
    const swayAmp = 0.65 + hf(i + 7) * 0.7;      // 每棵树不同
    const bright = 0.85 + hf(i + 13.37) * 0.3;   // 每棵树不同
    const posJitter = jitter(i, 2);               // ±2px

    plants.push({
      x: baseX + posJitter,
      species: sp,
      swayAmp: swayAmp,
      brightness: bright,
    });
  }
}
```

**⚠️ p5.js 注意事项**：`randomSeed(seed)` 影响 `random()` 调用，`noiseSeed(seed)` 影响 `noise()` 调用——但 `hf()` 是独立的，不受这两个 seed 影响。三者共存时：`rng()` 用于场景结构、`noise()` 用于空间场、`hf(idx)` 用于逐元素微变——各司其职，互不干扰。

### 自检（追加到上方质量检查）

- [ ] 大量同类元素（>10）是否使用 `hf(idx + OFFSET)` 做逐元素变化（而非 `random()`）？
- [ ] 不同用途的 hash 是否使用了不同的偏移值（7/13.37/73）？
- [ ] 振幅变化是否限制在 65%-135%（不会出现"几乎不动"或"疯狂摇摆"的极端）？
- [ ] 亮度变化是否限制在 ±15%（不会出现"太暗看不清"或"太亮刺眼"）？
