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
  createCanvas(640, 960);
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
| 程序化模型 A-D、FSM 代码、调色板预设 | `code-templates.md` — STEP 4 前必读 |
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

## 参数设计思考框架

不是"想到什么加什么"——在决定哪些维度可调之前，系统性地问：

| 维度 | 问题 | 像素场景示例 |
|------|------|------------|
| **数量** (Quantities) | 多少个？ | 植物数量、花瓣层数、鱼群规模 |
| **尺度** (Scales) | 多大？多快？ | 生长速度、粒子大小、游动幅度 |
| **概率** (Probabilities) | 多可能？ | 开花概率、突变概率、颜色变异率 |
| **比例** (Ratios) | 什么配比？ | 花 vs 叶比例、暖色 vs 冷色占比 |
| **角度** (Angles) | 什么方向？ | 枝干分叉角、游动偏转角、光源方向 |
| **阈值** (Thresholds) | 何时行为改变？ | FSM 状态切换时间、粒子衰减触发点 |

**设计原则：**
- **3-5 个参数是甜蜜点**——少于 3 个不够探索，多于 5 个眼花缭乱
- **每个参数必须对应一个视觉变化**——用户调 slider 后能立刻看到"变了什么"
- **默认值 = 最佳体验值**——用户不调参数也应该看到好作品，参数是"锦上添花"而非"修bug"
- **给每个参数起中文名 + 一句话解释**——用户在面板上看到"植物密度：控制花园里出现多少株植物"而非 `plantDensity: 0.5`
