# Pixel Bloom 通用方法论

> 不穷举场景。掌握这些原则，任意新场景都能自主做对决策。

## 一、五大硬性铁律 1-5（架构 / 管线 / 履约 / 美学 / 确定性）

> 以下 5 条规则是 pixel-bloom 的"宪法"。任何场景、任何主题、任何画幅比例都必须遵守。违反任一条 = 生成失败。

---

### 铁律 1：渲染领域绝对隔离（Domain Isolation Rule）

**原则**：DOM/CSS 和 Canvas 的职责边界不可逾越。

| 领域 | 允许 | 禁止 |
|------|------|------|
| **DOM / CSS** | `#pixel-stage` wrapper 的居中与响应式缩放；`body` 整体大渐变背景；交互层 `#interact-layer` 的事件监听 | 用 `backdrop-filter` / `border` / `box-shadow` / `::after` 绘制拟物化主体（玻璃瓶、气泡、晶体、光晕、水面） |
| **Canvas** | 所有拟物化主体、高光、阴影、液体、折射、内容物、粒子、FSM 生命体 | 用 CSS 类名选择器控制 Canvas 内部元素；用 DOM 元素叠加模拟 Canvas 内效果 |

**校验方法**：在最终 HTML 中搜索 `backdrop-filter` —— 如果出现在 `.glass-shell` 或任何 z-index ≥ 3 的元素上 → 致命错误。`backdrop-filter` 仅允许出现在 `.glass-bg`（z=2，仅用于非玻璃容器场景的整体底板模糊，且不在 Canvas 玻璃模式下使用）。

---

### 铁律 2：容器类材质的三榻饼管线（Sandwich Render Pipeline）

**原则**：凡涉及"内部装有内容物的容器"（玻璃瓶、水族箱、水晶球、水滴透镜），必须严格按照以下顺序在 Canvas 中绘制。

```
Pass 1 — 瓶后体块 (Back Mass)
  ctx.save() → defineContainerPath() → 径向/线性渐变填充（半透明冰蓝→边缘深绿）→ ctx.restore()

Pass 2 — 遮罩裁剪 (Clip Mask)
  ctx.save() → defineContainerPath() → ctx.clip()
    → 液体（带波浪水面 + 深度渐变）
    → 内容物（信纸/小船/生物/气泡）
    → 用户自定义内容（cfg.drawContents 回调）
  → ctx.restore()

Pass 3 — 前曲面高光 (Front Specular)
  ctx.save()
    → 厚玻璃底沉淀（径向椭圆渐变，暗绿褐）
    → 菲涅尔边缘描边（不等宽深绿→白亮线→透明→白亮线→深绿）
    → 曲面条带高光（globalCompositeOperation = 'screen' + bezierCurveTo 沿曲面路径）
    → 瓶口全反射环（椭圆 stroke + 径向渐变）
  → ctx.restore()
```

**校验方法**：若场景含玻璃容器，搜索 `ctx.clip()` 或 `drawingContext.clip()` —— 必须存在。搜索 `globalCompositeOperation` —— 必须在高光 Pass 中出现（`'screen'` 或 `'lighter'`）。

---

### 铁律 3：概念动词 → 代码履约断言（Concept Fulfillment Contract）

**原则**：用户 Prompt 中的每一个动词和意象，必须在代码中有对应的、可验证的技术实现。概念不能停留在"描述"层。

| Prompt 动词 / 意象 | 强制技术实现 | 禁止的"伪履约" |
|-------------------|-------------|--------------|
| **"展开"、"揭开"、"慢慢打开"** | `lerp()` 驱动的尺寸/进度变量（0→1），由交互（点击/时间）分段推进。每段有独立的 `lerp` 目标和速度 | 静态图片一次显示；`if(clicked) show=true` 瞬间切换 |
| **"漂浮"、"漂荡"、"悬浮"** | FSM（Wander 状态）+ Perlin noise 驱动速度与角度（`noise(x*0.01, t*0.3)`），至少 2 个正交方向的缓动 | `random()` 抖动；固定速度直线运动；绝对静止 |
| **"玻璃"、"水晶"、"透明容器"** | `createLinearGradient` 条带高光（alpha 0.8-1.0）+ `clip()` 遮罩 + 菲涅尔深色边缘描边 | CSS `backdrop-filter: blur()`；纯色 `fill(rgba)` 无渐变；无边缘描边 |
| **"水"、"液体"、"水面"** | 多正弦叠加波浪线（≥2 个频率分量）+ 深度渐变（浅蓝→深海蓝）+ 水面高光椭圆环 | 纯色 `rect()` 无波浪；单频率正弦（太机械） |
| **"气泡"、"水珠"** | 正圆 `circle()` + 偏移高光小白圆（Crescent Highlight）+ Perlin 上升轨迹 | `rect()` 圆角气泡；直线上升；无高光 |
| **"生命"、"生物"、"宠物"** | 状态机 ≥ 3 态（Wander/Chase/Flee 或自定义）+ 呼吸微动（`sin(t*0.05)*0.03`）+ 交互反馈动画 | 静态图片；只有 1 个状态；交互无反馈 |
| **"光"、"发光"、"光场"** | 单体粒子→指数衰减径向渐变 + `globalCompositeOperation = 'lighter'`（姿势 A）；全屏辉光→离屏下采样 Bloom 管线（姿势 B）；像素风发光→Bayer 抖动光晕（姿势 C）。详见 `pixel-grid-system.md §VII` | CSS `box-shadow` 发光；纯色无渐变 |

**校验方法**：逐条提取 Prompt 中的动词和意象词，对照上表检查代码中是否存在对应的技术实现。若 Prompt 含"展开"但代码无 `lerp()` → 概念未履约。

---

### 铁律 4：Frutiger Aero 材质物理规格（Aesthetic Translation Dictionary）

**原则**：当场景要求 Frutiger Aero 风格时，代码必须满足以下物理特征。这不是"建议"——是 Frutiger Aero 的定义性特征。

**禁用清单（Anti-Aero — 出现任一即风格偏离）**：
- ❌ 暗沉的毛玻璃（frosted blur — 灰白模糊，非通透）
- ❌ 纯黑阴影（`rgba(0,0,0,x)` — Aero 阴影是深蓝/深绿色调）
- ❌ 扁平无渐变色块（Flat Design — Aero 的核心是渐变模拟 3D 曲面）
- ❌ 高饱和原色（`#FF0000` / `#00FF00` / `#0000FF` — Aero 是粉彩柔和色）

**强制清单（Aero Required — 缺一不可）**：

| 特征 | 技术参数 | 视觉结果 |
|------|---------|---------|
| 纯白条带/弧形强高光 | `createLinearGradient` 多 stop（0→0.88α 白→0），`globalCompositeOperation = 'screen'`，沿曲面 `bezierCurveTo` 路径 | 晶莹刺眼的曲面镜像反射 |
| 鲜艳通透液体渐变 | 浅层 `#70d0f0`（Aqua Blue）→ 深层 `#1070a0`（Deep Cyan），`createLinearGradient` 垂直方向 | 水体的深度感和透光感 |
| 菲涅尔边缘描边 | 深绿/深青 `rgba(15,70,60,0.55)`，不等宽（边缘厚→中心消失），基于光程计算 | 厚玻璃边缘的铁离子吸收 |
| 上升气泡粒子 | 正圆 + 左上 Crescent 高光 + Perlin 上升轨迹 + 大小变化 | 水下生态的生命感 |
| 大气光斑（Bokeh） | CSS 径向渐变巨大模糊光斑（`filter: blur(30px)`，`opacity: 0.25`）缓慢漂浮在背景 | 镜头光晕 / 空气感 |

**调色板强制值**：

| 用途 | 色值 | 说明 |
|------|------|------|
| Aero 天空顶 | `#a8e6f8` | 清透天蓝 |
| Aero 水体浅层 | `#70d0f0` | Aqua Blue |
| Aero 水体深层 | `#1070a0` | Deep Cyan |
| Aero 玻璃高光峰 | `rgba(255,255,255,0.88)` | 纯白 screen |
| Aero 叶绿 | `#7DB87D` | Botanical Dew 中绿 |
| Aero 暖阳 | `#F5E6C8` | Sunlit Meadow 奶油黄 |

---

### 铁律 5：确定性渲染 — 禁止 `random()` 在 `draw()` 中用于静态/半静态元素

**原则**：`draw()` 每秒执行 60 次。在其中调用 `random()` 绘制静态或半静态元素（草丛、树叶、花朵、树木位置、纹理）会导致每秒 60 次帧间闪烁和抖动。

**禁止**：
```javascript
// ❌ 每秒 60 次重新随机——闪烁、抖动
function draw() {
  for (let i = 0; i < 100; i++) {
    fill(random(palette));  // 每帧颜色不同 → 闪烁
    rect(random(width), random(height), px, px); // 每帧位置不同 → 抖动
  }
}
```

**必须**：
```javascript
// ✅ setup() 中预生成，draw() 中只用 sin(t) 平滑位移
let grassBlades = []; // { x, y, color, phase }
function setup() {
  for (let i = 0; i < 100; i++) {
    grassBlades.push({
      x: hf(i * 12.9898) * width,       // 确定性 hash
      y: hf(i * 37.373) * height,
      color: palette[floor(hf(i + 7) * palette.length)], // 确定性选色
      phase: hf(i * 73.37) * TWO_PI      // 预生成相位
    });
  }
}
function draw() {
  for (let g of grassBlades) {
    let sway = sin(frameCount * 0.03 + g.phase) * 2; // 平滑位移
    fill(g.color);
    rect(g.x + sway, g.y, px, px * 3);
  }
}
```

**例外**：以下场景允许在 `draw()` 中使用 `random()`：
- 一次性粒子爆发（交互触发，非每帧）
- 云/雾的位置初始化偏移（配合 `noise()` 使用，非独立决定位置）
- 音效随机触发（不影响视觉）

**校验方法**：在 `<script>` 块中搜索 `draw()` 函数体内的 `random(` 调用。若存在且不在上述例外中 → 致命错误。

---

### 铁律自检清单（STEP 4 生成后强制执行）

- [ ] **规则 1**：搜索 `backdrop-filter` — 是否仅出现在 `.glass-bg`（z=2）？z≥3 的元素禁止
- [ ] **规则 2**：若场景含玻璃容器 → `ctx.clip()` 存在？`globalCompositeOperation = 'screen'` 在高光 Pass 中出现？
- [ ] **规则 3**：逐条对照 Prompt 动词与上表——每个动词是否有对应的技术实现？
- [ ] **规则 4**：搜索 `rgba(0,0,0` / `#000000` / 高饱和原色 → 是否存在 Aero 反模式？
- [ ] **规则 5**：搜索 `draw()` 内的 `random(` → 是否在例外清单之外？

---

## 二、铁律 6：像素完整性（Pixel Integrity Rule）

> 此规则与 §一 五大铁律并列，合称"六大铁律"。§一 管架构/管线/履约/美学/确定性，§二 管**像素网格纯度**。

### 原则

任何包含像素艺术元素的场景，必须满足以下像素完整性约束。违反任一条 → 像素美学崩溃。

### 约束清单

| # | 约束 | 检测方式 | 级别 |
|---|------|---------|------|
| 1 | `noSmooth()` + `imageSmoothingEnabled = false` + `image-rendering: pixelated` 三者缺一不可 | 搜索代码 | 致命 |
| 2 | 所有渲染坐标使用 `Math.round()` / `snap()` 吸附到整数像素 | 搜索 `translate(` | 警告 |
| 3 | 禁止 Mixel — 所有 `scale()` 参数必须为整数（1/2/3...） | 搜索 `scale(` | 警告 |
| 4 | 禁止非 90° 旋转 — `rotate()` 角度必须为 `n × PI/2` | 搜索 `rotate(` | 警告 |
| 5 | 禁止 CSS `filter: blur()` 或 `backdrop-filter` 覆盖在像素 Canvas 上层（z ≥ 3） | 搜索 CSS | 致命 |
| 6 | 像素精灵禁止使用 `createLinearGradient()` / `createRadialGradient()` — 应使用 Bayer 抖动或离散色阶 | 搜索 + 上下文判断 | 警告 |
| 7 | 渐变效果（地形/水体深度/光晕）必须使用有序抖动（Bayer）或预计算 Floyd-Steinberg，不得使用 Canvas 原生渐变 API | 搜索抖动函数 | 警告 |

### 与五大铁律的关系

| 铁律 | 管辖领域 | §二补充 |
|------|---------|------------|
| 铁律 1（领域隔离） | DOM/CSS vs Canvas 职责边界 | 补充：CSS `filter: blur()` 在像素场景中即使 z=2 也应避免（会模糊 Canvas 内容） |
| 铁律 5（确定性渲染） | `random()` 禁用于 `draw()` | 补充：非整数 `scale()` 和 `rotate()` 同样导致帧间不确定性（边缘跳跃） |

完整像素完整性规范 + Bayer 矩阵 + 抖动决策树 + 反模式详解 → `references/pixel-grid-system.md`。

### 自检清单（追加到 STEP 4 生成后）

- [ ] **规则 6a**：搜索 `noSmooth()` — 在 `setup()` 中存在？
- [ ] **规则 6b**：搜索 `imageSmoothingEnabled` — 设置为 `false`？
- [ ] **规则 6c**：搜索 `scale(` — 所有参数是否为整数？
- [ ] **规则 6d**：搜索 `rotate(` — 所有参数是否为 `0` / `PI` / `HALF_PI` 等 90° 倍数？
- [ ] **规则 6e**：搜索 `filter: blur(` — 是否不存在于 z ≥ 3 的任何元素？

---

## 三、架构

### 固定画布
像素艺术用固定像素尺寸 + `#pixel-stage` wrapper 的 `sizeStage()` 适配屏幕。尺寸由用户选择的画幅比例决定（如 3:4 → 640×960，16:9 → 960×540），不传 `windowWidth/windowHeight`。Canvas 通过 `c.parent('pixel-stage')` + CSS `width:100%; height:100%` 填满 wrapper，`image-rendering: pixelated` 保持像素锐利。Wrapper 尺寸由 `sizeStage()` 计算 `Math.min(windowWidth/CW, windowHeight/CH)` 并保持 aspect-ratio。

```javascript
const CW=640,CH=960;  // 示例：3:4 竖幅，根据所选比例调整
createCanvas(CW,CH);noSmooth();
```

`noSmooth()` 在固定画布上单独生效（不需要 `pixelDensity(1)`，高 DPI 下后者反而可能发虚）。

### 玻璃容器统一坐标系统（全场景统一 Z-index + Wrapper，不得更改）

所有视觉层必须位于同一个 `#pixel-stage` wrapper 内，使用 `position: absolute` + 百分比单位。wrapper 的 CSS 尺寸 = 画布显示尺寸，由 JS 的 `sizeStage()` 统一计算。**任何 layer 禁止单独使用 `position: fixed`。**

```
#pixel-stage (position:fixed, 居中于视口, overflow:hidden)
├── z=1  环境极光光斑（position:absolute, CSS 径向渐变, % 单位, 缓慢漂浮）
├── z=2  毛玻璃底板（position:absolute, 唯一有 backdrop-filter:blur 的层, % 单位）
├── z=3  Canvas 像素渲染层（position:absolute, 填满 wrapper, c.parent('pixel-stage')）
├── z=4  玻璃外壳（position:absolute, ::after 菲涅尔高光, 绝对不加 blur, pointer-events:none, % 单位）
└── z=5  交互拦截层（position:absolute, #interact-layer, inset:0, 原生 pointerdown 事件）
```

**铁律：**
1. **blur 只在 z=2 底板层**，永远不在 canvas 上层或玻璃壳层
2. **所有层使用 `position: absolute`**（相对于 `#pixel-stage`），禁止 `position: fixed`
3. **`#pixel-stage` 必须有 `overflow: hidden`**，裁剪 `::after` 菲涅尔高光溢出
4. **固定画布模式**：`windowResized()` 只调 `sizeStage()` 重算 wrapper 尺寸，不改 canvas 分辨率。像素永远锐利
5. **全视口模式**：`#pixel-stage { width:100vw; height:100vh; top:0; left:0; transform:none }` + `resizeCanvas(windowWidth, windowHeight)`

无玻璃的开放场景中 z=2 和 z=4 不存在，其余层级 + wrapper 保持不变。

容器尺寸固定时，穹顶/球体的 border-radius 用精确数学值：
- 穹顶 `border-radius: <玻璃宽度的一半>px <玻璃宽度的一半>px 0 0`
- 球体 `border-radius: 50%`（正方形元素）
- 玻璃高光用 `::after` 斜切 `linear-gradient`（模拟菲涅尔反射），`#pixel-stage` 的 `overflow:hidden` 自动裁剪溢出

### 无玻璃的开放场景
全视口天空渐变 + `#pixel-stage` 填满视口 + canvas 填满 wrapper。无玻璃壳层。wrapper 仍用于统一坐标系统。

### Canvas 玻璃容器场景（漂流瓶/水族箱/玻璃罩）

当场景含玻璃容器时，**玻璃的全部渲染（形状、折射、高光、厚度）在 Canvas 内部通过 `drawAeroGlassBottle()` 完成**（见 `code-templates.md §玻璃容器渲染`）。此时 CSS 的 `.glass-bg` 和 `.glass-shell` 可选择性保留作为**环境底板**（仅 body 渐变模糊，不再承载容器形状），或完全移除——玻璃容器本身就是 Canvas 内的一幅画。

Canvas 玻璃模式下的 CSS 层简化：
```
#pixel-stage
├── z=1  环境光斑（可选，Canvas 之外的气氛光斑）
├── z=2  （无玻璃底板 — 玻璃容器在 Canvas 内绘制）
├── z=3  Canvas（包含：背景 + 玻璃容器 + 瓶内内容 + 前景）
├── z=4  （无玻璃外壳 — 高光已在 Canvas 内部叠加）
└── z=5  交互拦截层
```

---

## 四、形状

### 地形用数学公式
椭圆、正弦、抛物线——精确可控。

```javascript
// 半椭圆岛屿
for(let dy=0;dy>-h;dy-=PX){
  let lim=round(sqrt(1-pow(dy/h,2))*r);
  for(let dx=-lim;dx<=lim;dx+=PX){/*...*/}
}
```

### 程序化模型（按需选用，至少一种）
| 模型 | 适用于 |
|------|--------|
| A·堆叠摇摆 | 树干、茎、水草、柳条 |
| B·网格剔除 | 灌木、云朵、海绵、草丛 |
| C·圆域筛选 | 花蕊、珊瑚、蘑菇伞、多肉 |
| D·扇形展开 | 棕榈叶、海扇、花瓣 |

**像素拆解法：** 任意目标物体 → 分解为基础几何（方块/圆/线/三角）+ 选配 A-D 模型 + 调色板数组。

---

## 五、运动（仿生数学三法则）

禁止线性赋值和 `random()` 抖动。所有运动必须有"生命感"。

### 法则一：生命呼吸（`sin` / `cos`）
任何物体都不允许绝对静止。哪怕停在原地，也必须有正弦波微动。
```javascript
scale(1+sin(frameCount*0.05)*0.03); // 心跳级呼吸
```
**像素呼吸：方向符号推，禁止 scale()。** 边缘块沿自身方向外推 1PX；蘑菇/荧光体用颜色明暗交替。非像素物体（光斑/气泡）可用 scale() 做呼吸。

### 法则二：灵魂漫游（Perlin Noise）
禁止 `random()` 做运动——产生苍蝇乱撞的机械感。`noise()` 产生连续伪随机，模拟流体涡流、风的轨迹、生物探索步态。
```javascript
c.vx+=(noise(c.x*.01,frameCount*.005)-.5)*.1; // 平滑不可预测
```

### 法则三：延迟满足（Lerp / 缓动）
物体绝不瞬间到达目标。`lerp()` 的阻尼跟随产生"重量感"和"果冻感"。
```javascript
x=lerp(x,target,.1); // 0.08=悬浮, 0.15=跟手
```

### FSM 状态机
- 有自主运动（宠物/鱼）→ Wander/Chase/Flee 三态 + Perlin noise 驱动
- 无自主运动（植物/摆件）→ React-only（交互触发单次反馈）

### Perlin 粒子 + 指数衰减加色光晕

```javascript
// 姿势 A：基于物理衰减模型的单体光晕
let g = drawingContext.createRadialGradient(x, y, innerR, x, y, outerR);
g.addColorStop(0,   'rgba(255,255,255,1.0)');  // 中心最强
g.addColorStop(0.2, 'rgba(255,255,255,0.6)');  // 近场衰减
g.addColorStop(0.5, 'rgba(255,255,255,0.2)');  // 中场
g.addColorStop(0.8, 'rgba(255,255,255,0.05)'); // 远场极弱
g.addColorStop(1,   'rgba(255,255,255,0.0)');  // 边界消失
drawingContext.globalCompositeOperation = 'lighter'; // ★ 加色混合 — 光能叠加
drawingContext.fillStyle = g;
drawingContext.beginPath();
drawingContext.arc(x, y, outerR, 0, Math.PI*2);
drawingContext.fill();
drawingContext.globalCompositeOperation = 'source-over'; // 恢复默认
```

---

## 六、材质（Canvas-Only 玻璃渲染）

> **铁律：玻璃的形状、折射与高光必须 100% 在 Canvas 内部绘制。禁止使用 CSS `backdrop-filter` / `border-radius` / `::after` 模拟玻璃容器。**

### 玻璃光泽（Canvas 三榻饼管线）

所有玻璃效果通过 `drawingContext`（p5.js 暴露的原生 Canvas2D 上下文）绑制，分层叠加：

```
1. ctx.save() → defineBottlePath() → 瓶后体块（径向渐变底色，模拟玻璃背壁透光）→ ctx.restore()
2. ctx.save() → defineBottlePath() → ctx.clip() → [瓶内水体/信纸/小船/气泡] → ctx.restore()
3. ctx.save() → [瓶底沉淀厚度] → [菲涅尔边缘描边] → [曲面条带高光screen] → [瓶口反射环] → ctx.restore()
4. ctx.save() → [软木塞3D圆柱体] → ctx.restore()
```

完整代码模板见 `code-templates.md §玻璃容器渲染`。

### 三个物理光学效应（Canvas 实现 vs CSS 的局限）

| 效应 | CSS 能做什么 | Canvas 正确做法 |
|------|------------|----------------|
| **菲涅尔反射** | `linear-gradient` 固定角度 | `schlick(cosθ)` 沿曲面法线计算 → 边缘自动亮起 |
| **比尔吸收** | `box-shadow: inset` 均匀内发光 | `beerAttenuation(thickness, sigma)` 每像素光程计算 → 边缘深绿 |
| **曲面高光** | `::after` 对角线渐变 | `globalCompositeOperation = 'screen'` + `bezierCurveTo()` 沿曲面绘制条带状高光 |

关键公式：
```javascript
// Schlick Fresnel: F = F0 + (1-F0)*(1-cosθ)^5,  F0=0.04（玻璃 IOR≈1.5）
// Beer-Lambert:  T = exp(-σ * thickness),  thickness = 2√(r² - d²)（球体光程）
```

> 完整玻璃调色板（含软木塞色）见 `code-templates.md §玻璃容器渲染 → 调色板参考`。

### 水珠透镜（Canvas 版）
```javascript
// 替代旧 CSS .water-drop
ctx.save();
ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI*2); ctx.clip();
// 透镜效果：放大 + 亮度提升
ctx.drawImage(canvas, 0, 0);  // 复制当前画布
// 叠加高光
ctx.globalCompositeOperation = 'screen';
ctx.fillStyle = 'rgba(255,255,255,0.4)'; ctx.fill();
ctx.restore();
```

### 底座质感
3 段渐变（亮面→固有色→暗面）+ 强外投影 + 顶部高光线 = 物体重量感。在 Canvas 中用 `createLinearGradient` 实现。

---

## 七、交互（防冲突法则）

### 移动端防线
```css
html,body{touch-action:none;user-select:none;-webkit-user-select:none}
```

### 单击/双击绝对隔离
**禁用 p5.js 内置 `mouseClicked`/`doubleClicked`。** 框架的双击必定先触发单击。

> 单击/双击隔离模板见 `code-templates.md §防坑铁律2`，直接复制使用。

### 反馈要求
交互至少产生一种视觉反馈（涟漪/粒子/颜色变化/缩放）。若音效开关为 yes，同时产生听觉反馈（Web Audio 合成音效）。

---

## 八、色彩

- 预设调色板数组，不为每个物体独立 random RGB
- Frutiger Aero 底色：柔和粉彩渐变，权威值见 `assets/palettes.json` 的 `base_gradient`
- 场景内 2-3 套调色板统一色调

### 6.1 空间相干颜色变化（去 random，用 noise field）

**当前反模式**：每个物体/每棵树用 `random(palette)` 独立选色 → 相邻物体颜色随机跳变 → 这是"噪声"，不是"自然变化"。

**自然界的颜色变化是空间相干的**：同一片草地的草颜色相近（共享土壤、光照），相邻的树有相似的色调（微气候），颜色变化发生在**区域尺度**上。

**升级方案**：用 Perlin 噪声场驱动颜色选择，不再逐物体 `random()`。

```javascript
// === 颜色补丁：噪声场 → colormap 查找 ===
// 在 setup() 中预计算或每帧实时计算

/**
 * 空间相干颜色选择 —— 替代 random(palette)
 * @param {number} x — 物体世界 X 坐标
 * @param {number} y — 物体世界 Y 坐标
 * @param {number} patchScale — 颜色补丁的尺度（越小=补丁越大）
 * @param {Array} palette — 调色板数组
 * @returns {string} 颜色（hex）
 */
function patchColor(x, y, patchScale, palette) {
  // 噪声值 [0, 1] —— 相邻的 (x,y) 产生相近的噪声值
  const n = noise(x * patchScale, y * patchScale);
  // 映射到调色板索引
  const idx = Math.floor(n * palette.length);
  return palette[constrain(idx, 0, palette.length - 1)];
}
```

**patchScale 的选择**（2D 像素画布，以 640px 宽为例）：

| patchScale | 补丁宽度 | 适用场景 |
|-----------|---------|---------|
| 0.01 | ~200px | 大区域颜色主题——整个草地东侧暖、西侧冷 |
| 0.03 | ~70px | 中等补丁——3-5 棵树共享一个颜色倾向 |
| 0.08 | ~25px | 小补丁——每棵树有自己的颜色，但相邻的仍相近 |

**⚠️ 避坑**：patchScale 过小（< 0.005）→ 整个场景同一颜色 → 失去变化。过大（> 0.2）→ 相邻像素噪声值不连续 → 退化为 random。**推荐起始值 0.03（约 70px 宽补丁），然后根据场景尺寸调整。**

### 6.2 双梯度混合（植物特定）

对于植被场景，颜色变化有两个正交维度：
1. **梯度方向**（A→B 或暖→冷）：决定补丁内所有植物的基调
2. **高度方向**（根→尖）：决定单个植物从基部到顶端的颜色推移

```javascript
// === 双梯度混合系统 ===
// 每套物种有两个颜色梯度（如：A=暖绿→黄绿，B=冷绿→蓝绿）

const SPECIES_COLORS = {
  broadleaf: {
    // 梯度 A — 默认（暖调）
    rootColorA: '#4a6b27', tipColorA: '#8fbc3b',
    // 梯度 B — 变体（冷调）
    rootColorB: '#3d5c1f', tipColorB: '#7aac2f',
  },
  conifer: {
    rootColorA: '#3d2b1f', tipColorA: '#2d5a1e',
    rootColorB: '#4a3528', tipColorB: '#3a6b28',
  },
};

/**
 * 双梯度颜色选择 + 逐物体亮度变异
 */
function plantColor(x, y, heightT, species, patchScale, palette) {
  const sp = SPECIES_COLORS[species];
  
  // 1. 补丁混合：噪声值决定梯度 A 和 B 的混合比例
  const patchNoise = noise(x * patchScale, y * patchScale);
  const blend = constrain(patchNoise, 0, 1);
  
  // 2. 根色和尖色分别在 A/B 之间混合
  const root = lerpColor(hexToColor(sp.rootColorA), hexToColor(sp.rootColorB), blend);
  const tip = lerpColor(hexToColor(sp.tipColorA), hexToColor(sp.tipColorB), blend);
  
  // 3. 沿高度方向在根色和尖色之间混合
  const baseColor = lerpColor(root, tip, heightT);
  
  // 4. 逐物体亮度微调（确定性 hash，范围 ±12%）
  const brightnessVar = 0.88 + hash(x * 100 + y * 37) * 0.24;
  
  return {
    r: constrain(Math.round(baseColor.r * brightnessVar), 0, 255),
    g: constrain(Math.round(baseColor.g * brightnessVar), 0, 255),
    b: constrain(Math.round(baseColor.b * brightnessVar), 0, 255),
  };
}
```

**效果**：
- 补丁噪声 → 相邻植物共享颜色倾向（同一片"微气候"）
- 双梯度 → 变化不单调（不只是"亮一点/暗一点"，是色调偏移）
- 逐物体亮度 hash → 同补丁内仍有细微个体差异（但不超过 ±12%，不会产生突兀的跳跃）

### 6.3 宏观亮度场（可选叠加层）

在补丁混合之上，可叠加一个更低频的亮度场来模拟"大片光照差异"——如云影、地形起伏。

```javascript
// 宏观亮度：极低频率噪声 → 大片区域偏亮或偏暗
const macroNoise = noise(x * 0.005 + 137, y * 0.005 + 91);
// 范围约 ±10%，非常微妙——这是"感觉"，不是"明显的明暗不同"
const macroFactor = 1.0 + (macroNoise - 0.5) * 0.2;
// 最终颜色 *= macroFactor
```

**⚠️ 微观颜色变化 vs 宏观亮度场**：微观（§6.1-6.2）= 逐物体的颜色选择，尺度 ~30-200px。宏观（§6.3）= 跨整个场景的亮度渐变，尺度 ~300-600px。两者叠加 = 自然界的多尺度变化。**不要只用其中一个——单尺度变化读作"单调"。**

### 6.4 色彩自检（追加到色彩相关检查）

- [ ] 颜色选择是否使用 `noise(x * patchScale, y * patchScale)` 而非 `random(palette)`？
- [ ] patchScale 是否匹配画布尺寸（推荐 0.02-0.05，约 40-100px 补丁）？
- [ ] 是否使用了双梯度混合（A→B 色调偏移 + 根→尖高度推移）？
- [ ] 逐物体亮度变异是否限制在 ±15% 以内（hash-based，非 random）？
- [ ] 宏观亮度场是否极低频率（patchScale 的 1/6 以下）？

---

## 九、音效

所有声音 Web Audio API 纯代码合成，零音频文件。
- AudioContext 在首次用户交互时初始化并 resume
- masterGain 起始值 0，linearRampToValueAtTime 淡入防爆音
- 174Hz 三角波 drone 作为治愈底噪（可选）
- 交互反馈音效：sine wave pop/chime

---

## 十、三大系统性反模式

### 反模式 1：p5.js Y 轴方向陷阱

p5.js 的 Y 轴指向**下方**（与数学坐标系相反）。所有角度计算必须用 `+sin(ang)` 而非 `-sin(ang)`。

```javascript
// ✅ p5.js 正确
ey = by + sin(angle) * length;

// ❌ 数学坐标系（p5 中会反向）
ey = by - sin(angle) * length;
```

**预防：** 写完任何涉及角度的绘制代码后，脑中默念 "p5 Y-down, +sin = down, -sin = up"。

### 反模式 2：CSS 玻璃层与固定画布坐标分离（🔴 最高频致命 bug）

**症状**：CSS 绘制的巨大模糊/白色遮罩压在固定画布上方，画面像被脏玻璃彻底挡死。

**根因**：各层使用 `position: fixed` + vw/vh 独立定位。当画布为固定像素（640×960）、玻璃壳为视口尺寸（~90vw×88vh）时：
- `.glass-shell`（z=4，canvas 之上）的 `::after` 伪元素 `width:120%; height:45%` + `rgba(255,255,255,0.4)` 白色渐变覆盖整个视口
- Canvas 只有 640×960，被远大于它的玻璃壳完全盖住 → 画面不可见
- 屏幕越大（1920×1080+），玻璃壳越大，覆盖越严重

**正解（唯一正确方式）**：使用 `#pixel-stage` wrapper 统一坐标系统。所有层用 `position: absolute` + `%` 单位相对于 wrapper。Canvas 通过 `c.parent('pixel-stage')` 挂入，CSS `width:100%; height:100%` 填满。Wrapper 尺寸由 JS `sizeStage()` 计算 = 画布显示尺寸。详见 `code-templates.md §防御性前端骨架`。

**禁止事项**：
- ❌ 任何层使用 `position: fixed`（wrapper 本身除外）
- ❌ 玻璃层使用 vw/vh 单位（应用 `%` 相对于 wrapper）
- ❌ Canvas 用 JS 设 `position: fixed; top:0; left:0`（应用 `c.parent()` + CSS `width:100%; height:100%`）
- ❌ `backdrop-filter: blur()` 出现在 z-index ≥ 3 的任何元素上
- ❌ 在 canvas 上层元素（z=4 玻璃壳、z=5 交互层）使用 `backdrop-filter`

### 反模式 3：校验通过 ≠ 页面正常

两步质检链必须**强制执行**——缺了浏览器实测的 validate.py 是假绿灯。

- **validate.py**（静态结构 + JS 语法检查）→ 查结构缺失和语法错误
- **浏览器实测** → 点一下看有没有反应，树是不是正的，猫是不是在树后面

**铁律：两步全完成才交付。跳任一步 = 白屏/倒树/无响应。**

---

## 十一、听觉心理学（Web Audio 疗愈频段）

音效不是"配个响声"——是触发副交感神经放松的疗愈手段。

### 数字疗愈频段
基频固定使用以下频率（声学疗愈验证）：
- **174Hz** — 缓解压力，身体放松
- **432Hz** — 宇宙疗愈频率，心轮共鸣
- **528Hz** — DNA 修复频率，转化

波形用**三角波**（`type='triangle'`）或**正弦波**（`type='sine'`），禁止锯齿波（焦虑感）。

### ADSR 声音包络
所有交互音效必须配置 Attack-Decay-Sustain-Release，禁止直上直下：
```javascript
// 颂钵/风铃音色：快起慢落
g.gain.setValueAtTime(0, t);                    // Attack: 静音起步
g.gain.linearRampToValueAtTime(0.15, t+.03);    // Decay: 极快触发峰值
g.gain.exponentialRampToValueAtTime(0.001, t+2.5); // Release: 2-3秒长尾泛音
```
**物理隐喻：** 短 Attack = 敲击瞬间。长 Release = 余音绕梁。模拟水晶颂钵或玻璃风铃的残响。

### 底噪与环境音
- 治愈底噪：174Hz 三角波 → 低通滤波到 300Hz 以下 → gain ≤ 0.05
- 雨声/海浪：白噪 buffer → 带通滤波 → 循环播放
- 风铃散音：Cmaj7 和弦（C4-E4-G4-B4），随机触发 2-3 音

---

## 十二、排版（Frutiger Aero 字体法则）

### 字体栈
```css
font-family:"Segoe UI","Frutiger","Trebuchet MS","PingFang SC",sans-serif
```

### 文字质感
- 发光白边：`text-shadow:0 1px 2px rgba(255,255,255,.8)`
- 禁用纯黑字体：统一深海蓝/墨绿 `#1a4a5e` 或半透明白 `rgba(255,255,255,.85)`
- 字间距：标题 6-8px，正文 3-4px，提示文字最大
- 标题字重 200-300（Light），不用粗体

### 操作提示
界面底部一行极简提示，字号 12px，letter-spacing 3px，半透明，不抢主视觉。
```html
<div class="hint">单击：浇水 | 双击：敲玻璃</div>
```

---

## 十三、参数设计思考框架

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

---

## 十四、屏幕像素锚定法则（全场景通用）

**参数设计必须以屏幕像素为锚点，不是以数学比例为锚点。**

### 最小可见尺寸（1280×800 参考）

| 元素类型 | 最小可见像素 | 占画布最小比例 |
|---------|------------|--------------|
| 主体元素（远层） | ≥ 20px | ≥ 2.5% 高度 |
| 主体元素（近层） | ≥ 80px | ≥ 10% 高度 |
| 尺度参照物（建筑/人物） | ≥ 12px | ≥ 1.5% 高度 |
| 生物细节（蝴蝶/鸟/鱼） | ≥ 6px 翼展 | — |
| 路径/引导线（近端） | ≥ 8px 宽 | — |
| 路径/引导线（远端） | ≥ 2px 宽 | — |
| 前景装饰（花/草/石） | ≥ 2px 直径 | — |

### 写完任何 scale/size 参数立刻验证

```
实际像素 = 基准尺寸 × scale
```

**< 15px = 用户看不见。 < 8px = 连点都不是。**

### 颜色可见性验证

```
颜色反差 = |R_元素 - R_背景| + |G_元素 - G_背景| + |B_元素 - B_背景|
```

- 反差 < 60：元素融入背景 → 需要提饱和 / 加描边 / 加光晕衬底
- 反差 > 120：清晰可见
- **白色/浅色元素在亮天/亮底背景上：必须有暗色光晕衬底，否则必然不可见**

---

## 十五、对抗式检查 SOP（全场景通用 · 强制执行）

**写完代码后，用脚本做结构性检查。人脑无法同时追踪所有参数的一致性。**

### 检查项

| # | 检查项 | 方法 | 级别 |
|---|--------|------|------|
| 1 | JS 语法 | `new Function(script)` | 致命 |
| 2 | API 兼容性 | 扫描 `fill(hex+'cc')` 等字符串拼接 α 值 → 替换为 `rgba()` | 致命 |
| 3 | 地形/背景参数一致性 | 元素放置函数与场景绘制函数的参数交叉比对 | 致命 |
| 4 | 元素坐标冲突 | 提取所有地面元素的 (x,y) 与水体/障碍边界交叉计算 | 致命 |
| 5 | **空间一致性（坐标系统）** | ① `position:fixed` 数量 ≤ 1（仅 wrapper）② 子层无 vw/vh 单位 ③ `c.parent()` 存在 ④ `sizeStage()` 存在（固定画布） | 致命 |
| 6 | **空间一致性（blur 层级）** | `backdrop-filter` 仅出现在 z-index=2 的 `.glass-bg` 中，z≥3 的任何元素禁止 | 致命 |
| 7 | **空间一致性（边界裁剪）** | `#pixel-stage` 有 `overflow:hidden`；`::after` 的 top+height ≤ 100%（不超出容器） | 警告 |
| 8 | 跨浏览器兼容性 | 扫描 `rect(x, y, w, -h)` 等负尺寸 → 替换为正尺寸 | 警告 |
| 9 | 缩放可见性 | 提取所有 `scale` 值，计算实际像素，标记 < 15px 的 | 警告 |
| 10 | 颜色可见性 | 提取元素颜色与背景颜色，计算反差，标记 < 60 的 | 警告 |

### 执行纪律

- **第一轮**：代码写完立刻跑，修完所有致命项才进 validate.py
- **第二轮**：validate.py 通过后跑，修完所有警告才进浏览器实测
- **检查脚本不替代浏览器实测**——它只查结构性错误，不查"运动是否流畅""交互反馈是否有疗愈感"

### 最小检查脚本骨架

```javascript
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const sm = (html.match(/<script>([\s\S]*?)<\/script>/) || [])[1] || '';
const issues = [];

// 1. JS 语法
try { new Function(sm); } catch (e) { issues.push('FATAL: JS - ' + e.message); }

// 2. hex + string 拼接 α
if (sm.includes("+ 'cc'") || sm.includes('+ "cc"')) {
  issues.push('FATAL: hex+string alpha concat — use rgba()');
}

// 3. 负尺寸 rect
const negRects = sm.match(/rect\([^)]*-\d+[^)]*\)/g) || [];
if (negRects.length) issues.push('WARN: rect with negative values');

// 4. 缩放可见性
const scales = [...sm.matchAll(/scale\s*=\s*([\d.]+)/g)];
for (const s of scales) {
  const px = 50 * parseFloat(s[1]); // 基准 50px
  if (px < 15) issues.push(`WARN: scale=${s[1]} → ${px.toFixed(0)}px < 15px minimum`);
}

// 5. 空间一致性 — 坐标系统（致命）
if (!html.includes('pixel-stage')) issues.push('FATAL: 缺少 #pixel-stage wrapper');

// 5a. 固定画布必须有 sizeStage
const isFixed = html.includes('Render: fixedCanvas');
if (isFixed && !html.includes('sizeStage')) {
  issues.push('FATAL: 固定画布缺少 sizeStage() 函数（wrapper 尺寸计算）');
}

// 5b. position:fixed 计数 — 只允许 #pixel-stage 使用
const fixedMatches = html.match(/position\s*:\s*fixed/g) || [];
// html, body 和 #pixel-stage 各算 1 次 fixed，合计 ≤ 3（html + body + wrapper）
const hasWrapperFixed = html.includes('#pixel-stage') && /#pixel-stage\s*\{[^}]*position\s*:\s*fixed/.test(html);
const allowedFixed = (html.includes('html') ? 1 : 0) + (html.includes('body') ? 1 : 0) + (hasWrapperFixed ? 1 : 0);
if (fixedMatches.length > allowedFixed) {
  issues.push('FATAL: 子层使用了 position:fixed（应全部改为 position:absolute）');
}

// 5c. 子层禁 vw/vh — 玻璃层必须用 %（开放场景 ambient-light 可用 vw/vh，但 glass-bg/shell 不行）
const glassVW = (html.match(/\.glass-bg\s*\{[^}]*[vh]w/g) || []).length +
                (html.match(/\.glass-shell\s*\{[^}]*[vh]w/g) || []).length;
if (glassVW > 0) issues.push('FATAL: .glass-bg 或 .glass-shell 使用了 vw/vh（应用 % 相对于 wrapper）');

// 5d. Canvas 挂入
if (!html.includes('c.parent') && !html.includes('.parent(')) {
  issues.push('FATAL: Canvas 未挂入 wrapper（缺少 c.parent()）');
}

// 6. 空间一致性 — blur 层级
const blurAboveZ2 = /z-index\s*:\s*[3-9][^}]*backdrop-filter/.test(html) ||
                     /backdrop-filter[^}]*z-index\s*:\s*[3-9]/.test(html);
if (blurAboveZ2) issues.push('FATAL: backdrop-filter 出现在 z-index≥3 的层上（仅允许 z=2 的 glass-bg）');

// 7. 空间一致性 — 边界裁剪（警告）
if (!html.includes('overflow:hidden') && !html.includes('overflow: hidden')) {
  issues.push('WARN: #pixel-stage 缺少 overflow:hidden（::after 高光可能溢出）');
}
// ::after 边界检查：提取 top 和 height 百分比值
const afterMatch = html.match(/\.glass-shell::after\s*\{[^}]*\}/);
if (afterMatch) {
  const topM = afterMatch[0].match(/top\s*:\s*(-?\d+)%/);
  const hM = afterMatch[0].match(/height\s*:\s*(\d+)%/);
  if (topM && hM) {
    const topVal = parseInt(topM[1]);
    const heightVal = parseInt(hM[1]);
    if (topVal < 0 && Math.abs(topVal) + heightVal > 100) {
      issues.push(`WARN: ::after top(${topVal}%)+height(${heightVal}%) 超出 100%，溢出部分可能覆盖相邻层`);
    }
  }
}

console.log(issues.length ? issues.join('\n') : 'All checks passed');
```

### 像素视觉验证（对抗式检查之后 · 质检之前 · 强制执行）

对抗式检查验证了"代码结构安全"——但它不能验证**运行时视觉正确**。以下 5 项中，检查 0 是代码级可验证的（AI 可以做到），检查 1-4 需要目测确认。**WARN 不是"可以忽略"——WARN 的项目必须在本步骤逐项目测确认。**

#### 检查 0：空间一致性（代码级 · AI 强制执行 · 在目测之前）

这一项不需要浏览器。从代码即可验证 5 个层是否共用同一坐标系统：

```
1. 坐标原点统一：
   - grep 'position:\s*fixed' → 计数。应 = 1（仅 #pixel-stage）。
     若 > 1 → 致命：有子层脱离 wrapper 坐标系 → 不同屏幕比例下必然错位。
   
2. 尺寸锚点统一：
   - grep 'vw\|vh' → 是否出现在 .glass-bg / .glass-shell / #interact-layer 中？
     若是 → 致命：这些层用视口单位，wrapper 用像素单位 → 不一致。
     应全部使用 %（相对于 wrapper）或 px（与 canvas 一致）。
   
3. blur 层级正确：
   - grep 'backdrop-filter' → 确认只在 .glass-bg { z-index: 2 } 中出现。
     若出现在 .glass-shell 或任何 z-index ≥ 3 的层 → 致命。
   
4. wrapper 裁剪溢出：
   - #pixel-stage 必须有 overflow: hidden。
     若缺失 → 警告：::after 菲涅尔高光会溢出到 wrapper 外部。
   
5. 容器尺寸 = 画布尺寸：
   - sizeStage() 中: scale = Math.min(windowWidth/CW, windowHeight/CH)
     wrapper.width = CW * scale, wrapper.height = CH * scale
     → wrapper 的 aspect-ratio = CW:CH = 画布 aspect-ratio ✓
```

**通过标准**：5 项全部 ✅。任何致命项 → 回 STEP 4 修复。不依赖浏览器，AI 可以在代码中直接验证。

**为什么这一步必须放在目测之前**：如果坐标系统不统一，后续 4 项视觉检查（像素可见性、颜色对比度、viewport 响应、运动稳定性）看到的结果本身就是错的——不同层在物理上不重叠，颜色对比度、像素大小都没有意义。

#### 检查 1：像素可见性

对抗式检查脚本提取了所有 `scale` 值并计算了实际像素。本步骤**逐项目测每一个 WARN 项**：

```
对于每个 scale < 阈值的元素：
  1. 计算实际像素 = 基准尺寸 × scale
  2. < 8px  → 致命：用户看不见这个元素。增大 scale 或增大基准尺寸
  3. 8-15px → 目测确认：在 1280×800 视口下，这个元素是一个"形状"还是"一个点"？
             如果是"一个点" → 增大 scale 或增大基准尺寸
             如果是"一个可辨识的形状" → 通过（如 12px 的像素蝴蝶在 640×960 画布上是可辨识的）
```

**通过标准**：所有 WARN 项均已目测确认可辨识，或已修复。

#### 检查 2：颜色对比度

相邻层的颜色对必须可分辨。使用色差公式 `Δ = |ΔR|+|ΔG|+|ΔB|`：

```
对于每个相邻层对（如 L1 vs L2 / 元素 vs 背景 / 文字 vs 底衬）：
  1. 计算色差 Δ
  2. Δ < 30 → 致命：两层在普通屏幕上看起来是同一层。增大色差——改其中一层的颜色
  3. Δ 30-60 → 目测确认：在屏幕亮度 50% 下能否分辨？
             如果不能 → 增大色差
  4. Δ > 60 → 通过
```

**特殊规则**：
- 毛玻璃底板上的文字：Δ 必须 > 80（`backdrop-filter: blur()` 会进一步降低对比度）
- 极远层（L1）：B 通道必须 > G 通道（蓝移——大气透视正确）
- 近景层（L5）：G 通道必须 > B 通道（绿移——近景饱和正确）

**通过标准**：所有层对的 Δ > 30，目测确认可分辨。

#### 检查 3：viewport 响应

固定画布（如 640×960）通过 `#pixel-stage` wrapper + `sizeStage()` 适配屏幕。验证不同视口下的视觉：

```
模拟 3 个关键视口（用浏览器 DevTools 或手动 resize）：
  1. 375×812（iPhone SE）——最小屏
  2. 1280×800（桌面基准）
  3. 1920×1080（大屏）

每个视口下检查：
  - 画布是否完全可见（不被裁剪）？
  - 像素是否因放大而严重锯齿化？（>2.5x 放大时有明显锯齿 → 需调整画布基准尺寸）
  - FPS 是否在各视口下 ≥ 50？（小屏 = 渲染负担小，大屏 = CSS scale 不增加绘制像素）
  - 毛玻璃 z-index 是否正确？（Safari stacking context bug — z=3 canvas 是否夹在 z=2 底板和 z=4 外壳之间）
```

**通过标准**：3 个视口下画布完整可见、无不合理锯齿、FPS ≥ 50、z-index 正确。

#### 检查 4：运动稳定性

FSM 生命体和粒子系统在长时间运行后是否退化：

```
30 秒模拟运行（在 1280×800 视口下）：
  - FSM 生命体：是否卡在某个状态不切换？是否飞出画面边界后消失？
  - Perlin 粒子：是否均匀分布（无聚集/空洞）？总数是否稳定（不耗尽/不累积）？
  - 帧率：初始帧率 vs 30 秒后帧率？下降 > 20% → 排查粒子累积或内存泄漏
```

**通过标准**：30 秒后 FSM 仍在正常切换状态、粒子分布均匀、总数稳定、帧率降幅 < 20%。

---

## 十六、第一性原理创作流程（全场景通用）

### 决策链（从情感锚点到代码）

```
情感锚点（这个作品让人感受到什么？）
  ↓
物理隐喻（什么自然现象承载这个感受？）
  ↓
纵深/空间结构（几层？每层什么内容？开放场景用 landscape-composition.md §三）
  ↓
三要素落地（可进入的纵深？尺度参照物？活的细节？开放场景用 landscape-composition.md §四）
  ↓
参数锚定（每个 scale/size/color → 对应多少实际像素？→ 本文件 §十四）
  ↓
交叉验证（元素是否在它应该在的地方？→ 本文件 §十五）
  ↓
对抗式检查（脚本跑一遍 → 本文件 §十五）
  ↓
浏览器实测
```

### 五个铁律

1. **隐喻先于技术**：不要先决定"用什么库画什么"，先决定"让人感受到什么"
2. **参数必须锚定屏幕像素**：`scale = 0.4` 没有意义，`50px × 0.4 = 20px ✓` 才有意义
3. **色差是结构性的，不是微调**：两层的色差必须 ≥ 30（`|ΔR|+|ΔG|+|ΔB|`），否则人眼看不出分层
4. **生物细节的辨识度靠轮廓剪影**：先确保形状读得出来，再加颜色和动画。小尺寸元素的识别依赖外轮廓，不是内部细节
5. **对抗式检查是强制步骤，不是可选**：人脑无法追踪 N 个元素的 scale × M 层背景 × 水体边界 × API 兼容性。脚本能。

### 迭代优先级（效果不好时按顺序排查）

| 优先级 | 检查项 | 投入产出比 |
|--------|--------|----------|
| 1 | 三要素至少缺一个 — 尤其是尺度参照物 | 最高 |
| 2 | 色差不足 — 远近层颜色没有结构性差异 | 高 |
| 3 | 主体元素太小 — scale × 基准尺寸 < 15px | 高 |
| 4 | 引导线不可见 — 路/河宽度不够或颜色太淡 | 中 |
| 5 | 生物细节不"生物" — 运动轨迹是平滑 Perlin 而非分段转向/FSM | 中 |
| 6 | 颜色反差不够 — 元素融入背景 | 中 |
| 7 | 粒子参数微调 | 低（最后 10%，不是前 90%） |

---

## 十七、概念种子→参数偏置（STEP 3 参数决策后强制执行）

概念种子是 pixel-bloom 的情绪锚点。**但它不能只是命名和宏观方向——必须系统化地偏置所有参数选择。**

当前流程：STEP 3 技术决策 → 自问"颜色温度、运动速度、交互节奏是否与概念种子一致？"——这是**事后追问**。如果发现不一致，需要回退重选——模型大概率不会真的回退，而是说服自己"还行"。

**改为事前约束**：STEP 3 参数决策完成后，逐项对照下表。**参数选择不允许在偏置方向上反向。**

### 偏置方向表（按概念种子）

| 概念种子 | 色温 | 运动速度 | 交互响应模式 | 粒子/元素密度 | 音效方向 |
|---------|------|---------|------------|-------------|---------|
| **Always Here**（它会一直在） | **暖** +20%（偏橙/金/奶油白） | **慢** -30%（呼吸级缓动优先） | **回应感**（交互后 300-500ms 内有微妙变化——不是立刻弹，也不是不回应） | **偏疏**（不拥挤——陪伴是空间，不是压迫） | 低频暖底噪 + 单音确认（不喧宾夺主） |
| **Still Growth**（不需观众） | **中性偏冷**（莫兰迪绿/灰蓝） | **极慢** -50%（几乎静止的微动） | **自主变化 > 交互反馈**（用户不碰也在变；碰了反而不一定有回应——它不在乎） | **疏**（每个元素有独立呼吸空间） | 极静或干脆无音效 |
| **Secret Haven**（秘密庇护所） | **中性偏暖**（斑驳阳光透过叶片 + 露水反光，黄绿+暖白） | **慢** -30%（植物微微摇曳，蝴蝶缓慢访花——不匆忙的节奏） | **直接但温和**（轻触开花/长按浇水/滑过有花粉飘起——花园回应你的存在但不依赖你） | **偏密但不拥挤**（多种植物共生，每株有自己的呼吸空间） | 露水滴答 + 轻风铃 + 远处蜜蜂嗡嗡 |
| **Another Tank**（平行存在） | **中性**（水下蓝绿/自然色） | **中速**（自然游动节奏） | **无直接响应**（鱼不在乎你有没有在看——交互不影响运动，最多影响环境光） | **正常**（世界是满的，不是为人留白） | 水下低频闷响 + 气泡音 |
| **Windmill Valley**（可走入） | **Golden Hour 暖**（暖金光源 + 大气透视蓝移） | **自然风变速**（Perlin 噪声驱动，1.0-2.5 级波动） | **滑动 = 感受风**（鼠标/手指滑过有风轨跟随；单击 = 风铃触发） | **偏密**（世界是完整的——该有的都有） | 风底噪 + 风铃五声音阶 + 风速→音高映射 |
| **Slow Woods**（慢下来不是落后） | **中性偏暖**（林间斑驳阳光，黄绿交织） | **慢 -40%**（几乎静止，风过时才微动——树木不追逐任何东西） | **间接回应**（交互改变风/光/季节，树本身不直接回应——它们有自己的节奏） | **偏密**（不同高度层树冠重叠，满但不拥挤） | 叶颤沙沙底噪 + 低频风吟 + 间歇风铃 |

### 使用规则

1. **先选参数，再对表偏置**。不是从表里直接读参数——是先按技术决策走，然后用偏置方向调整。
2. **偏置是"倾向"不是"绝对值"**。"暖 +20%"意思是：在技术决策给出的合理范围内，偏暖 20%。不是把颜色从蓝色变成橙色。
3. **如果概念种子不在表中**（用户自定义了新种子）→ 从最接近的种子类推。如果无法类推 → 问用户：这个种子的色温/速度/密度应该是什么方向？
4. **如果参数选择在偏置方向上反向**（如"Still Growth"选了快摇+高饱和暖色）→ 回退重选。这是致命偏差——概念种子形同虚设。

### 自检（STEP 3 完成后、STEP 4 生成前）

- [ ] 色温方向是否与概念种子偏置一致？
- [ ] 运动速度是否与概念种子偏置一致？（最快的元素/最活跃的 FSM 状态下的速度）
- [ ] 交互响应模式是否与概念种子偏置一致？（"Still Growth"不能有"一碰就开花"的反馈）
- [ ] 如果没有音效，是否与概念种子偏置一致？（"Still Growth"无音效 = 加分，不是缺失）

---

## 十八、全场景风元素统一采样

> 设计哲学源自 OceanThreejs 的"位移场→一切"：泡沫/法线/颜色都从同一个底层场派生。适配到 pixel-bloom：**所有被风驱动的像素元素——树 sway、水面波浪、花粉粒子、蝴蝶——从 vegetation-system.md §七 的同一套风系统采样。**

### 17.1 为什么需要共享风场

`vegetation-system.md` 的三级风很好——但每棵树各自调用 `sin(time * freq + phase)`。`ocean-pixels.md` 的波浪用 `wave.speed * time + phase`。花粉用 `noise(x*0.01, time*0.3)`。**三套时间尺度、三套相位——看起来不是同一阵风。**

反模式场景：树同时向左歪（sin 同步）、水面波浪向右涌（相位偏移不同）、花粉向下漂（noise 梯度方向）→ 三个"风驱动"元素在互相矛盾。用户不会说"风场不统一"——用户会说"感觉不自然"。

### 17.2 统一实现：vegetation-system.md §七 的 WIND 对象

**全场景风元素的唯一数据源**是 `vegetation-system.md §七` 定义的全局 `WIND` 对象（`strength`/`speed`/`angle`/`gustScale`/`turbulence`/`flutter`）和 `windIntensity(x, idx, time, WIND)` 函数。树木的三级风（叶颤/枝摇/干摆）由 `applyWind()` 驱动；其他元素从同一个 `WIND` 对象采样：

| 元素 | 采样方式 | 来源 |
|------|---------|------|
| 树 sway — 三级风 | `applyWind(tree, canopyPixels, WIND.strength, time, px)` | vegetation-system.md §七 |
| 水面波浪 phaseShift | `const shift = WIND.strength * 0.3;` 叠加到波浪 theta | 从 WIND 采样 |
| 花粉/粒子漂移 | `p.vx += WIND.strength * 0.1;` 共享风强 | 从 WIND 采样 |
| 蝴蝶 FSM 航向偏置 | `butterfly.targetAngle += WIND.strength * 0.05;` | 从 WIND 采样 |

**关键原则**：所有元素读取同一个 `WIND` 对象——WIND 在每帧通过 `updateWind(time)` 更新（见 vegetation-system.md §5.3），确保"同一阵风"的一致性。不同元素通过**不同的振幅乘数**体现不同响应（树 3px、花粉 0.1px、波浪 0.3 phase），而非各自定义独立的风参数。

### 17.3 何时不必用共享风场

| 场景 | 原因 |
|------|------|
| 赛博宠物（封闭容器） | 容器内无风——宠物 FSM 不依赖风 |
| 像素盆栽（室内） | 室内微风——如果有，用一个全局标量就够了，不需要空间变化 |
| 只有一个风驱动元素 | 单棵树或单层波浪——跨元素协调优势不存在 |
| Ganzfeld 模式 | 无风——光场场景 |

### 17.4 自检

- [ ] 场景中所有风驱动元素是否从同一个 `WIND` 对象读取 `strength`（非各自独立 `sin`/`noise`）？
- [ ] 树木是否使用 `vegetation-system.md §七` 的 `applyWind()`（三级频率：叶颤/枝摇/干摆）？
- [ ] 不同元素是否用了不同的振幅乘数（树 3px，花粉 0.1px，波浪 0.3 phase）——共享风场，不共享振幅？
- [ ] `WIND.strength` 是否与概念种子偏置一致（§十七）？
- [ ] 如果场景只有一个风驱动元素——共享风场不是必需的（不要过度工程）？

---

## 十九、大面积填充性能铁律（Full-Surface Fill）

> 开放风景场景的天空/地形/水面/稻田——任何需要覆盖 ≥ 30% 画布的区域——禁止用 `rect()` 逐格填充。三条铁律覆盖所有场景。

### 19.1 铁律一：纯色或垂直渐变 → Canvas Gradient

```javascript
// ❌ 死路：80 条 rect() 模拟天空渐变
for (let i = 0; i < 80; i++) { fill(...); rect(0, y, CW, stripH); }

// ✅ 单次 GPU 调用
let grad = drawingContext.createLinearGradient(0, 0, 0, horizonY);
grad.addColorStop(0, topColor.toString());
grad.addColorStop(1, botColor.toString());
drawingContext.fillStyle = grad;
drawingContext.fillRect(0, 0, CW, horizonY);
```

**适用**：天空、大范围水体底色、任何垂直渐变。

### 19.2 铁律二：大面积同色底色 + 稀疏噪声叠加 → 两段式

```javascript
// ✅ 整块底色（单次 rect）
fill(baseColor);
rect(0, horizonY, CW, CH - horizonY);

// ✅ 稀疏叠加——只在高噪声区加纹路（~95% 像素不画）
fill(highlightColor);
for (let y = horizonY; y < CH; y += PX * 4) {
  for (let x = 0; x < CW; x += stepX(y)) {
    if (noise(...) > 0.55) rect(x, y, len, h); // 仅在噪声峰触发
  }
}
```

**性能差距**：逐格 ~12K rect/帧 → 两段式 ~800 rect/帧（约 15×）。

**适用**：稻田、草地、沙地、雪地——任何带纹理的大面积。

### 19.3 铁律三：带状不规则区域 → `beginShape()` 单次路径

```javascript
// ❌ 死路：逐列 rect() 填充河流
for (let x = 0; x < CW; x += PX) {
  let b = getRiver(x); rect(x, b.top, PX, b.h);
}

// ✅ beginShape + endShape 单次路径
fill(riverColor);
beginShape();
for (let y = horizon; y <= CH; y += PX) {
  let b = getRiver(y); if (b) vertex(b.left, y);
}
for (let y = CH; y >= horizon; y -= PX) {
  let b = getRiver(y); if (b) vertex(b.right, y);
}
endShape(CLOSE);
```

**性能差距**：逐列 ~960 rect/帧 → 单次路径 1 draw call（约 500×）。

**适用**：河流、溪流、道路、任何由两侧边界定义的带状区域。

### 19.4 自检

- [ ] 天空是否用了 Canvas Gradient（而非 `rect()` 条带）？
- [ ] 地形/稻田底色是否是单次 `rect()`（而非逐格填充）？
- [ ] 纹理叠加是否用 `noise() > threshold` 稀疏触发？
- [ ] 河流/道路是否用 `beginShape()`/`endShape()`（而非逐列 `rect()`）？

---

## 二十、像素星空与夜景天空

> 设计哲学源自 threejs-environment-water-and-sky 的星星自动显现和大气消光模型。星星的可见性不由 `if (isNight)` 二元切换——从天空亮度连续派生。星星在天顶密集、地平线稀疏——用 `pow(heightRatio, 3.5)` 模拟大气消光。适配到 Pixel Bloom：纯 Canvas2D 像素绘制，确定性 hash 生成星点位置，Perlin 微动模拟闪烁。

### 20.1 天空亮度 → 星星可见性（数据驱动，非状态驱动）

```javascript
// === 天空亮度计算（驱动所有夜景元素） ===
// skyBrightness: 0.0 = 纯黑夜空, 1.0 = 白天蓝天
// 从天空渐变的 topColor 和 bottomColor 的 BT.709 luma 派生
function calcSkyBrightness(topColor, bottomColor) {
  const topLuma = topColor._getRed() * 0.2126 + topColor._getGreen() * 0.7152 + topColor._getBlue() * 0.0722;
  const botLuma = bottomColor._getRed() * 0.2126 + bottomColor._getGreen() * 0.7152 + bottomColor._getBlue() * 0.0722;
  return (topLuma + botLuma) / (2 * 255); // 归一化到 [0, 1]
}

// 场景初始化时计算一次（或天空颜色变化时更新）
let skyBrightness = 0.35; // 示例：黄昏天空

// === 星星可见性：连续函数，不是 if(isNight) ===
// 天空亮度 > 0.35 → 无星星（白天/黄昏初期）
// 天空亮度 < 0.15 → 满星（深夜）
// 0.15-0.35 → 连续过渡（黄昏→夜晚）
const starsAlpha = constrain((0.35 - skyBrightness) * 5.0, 0, 1);
```

### 20.2 像素星星生成（确定性 + 大气消光）

```javascript
// === 像素星星系统 ===
const STAR_COUNT = 200;        // 200 颗星——在 640×960 画布上不拥挤
const STAR_SIZE = 1;          // 1px——像素艺术的最小可见单位（亮星可变大）
const STAR_COLOR_BRIGHT = '#ffffff';  // 亮星（天顶）
const STAR_COLOR_DIM = '#aabbcc';    // 暗星（地平线）

function generateStars(seed, horizonY) {
  const stars = [];
  for (let i = 0; i < STAR_COUNT; i++) {
    // 确定性位置：用 hf() 而非 random()
    const x = hf(i * 12.9898) * width;
    const y = hf(i * 37.373 + 7) * horizonY;  // 仅在地平线以上
    
    // 大气消光：地平线附近 (y 接近 horizonY) 的星星更暗更稀疏
    const heightRatio = 1.0 - (y / horizonY);  // 0 = 地平线, 1 = 天顶
    const extinction = Math.pow(heightRatio, 3.5);  // pow(h, 3.5) 大气消光
    
    // 只有通过消光筛选的星星才保留——地平线附近自动稀疏
    if (hf(i * 73.37) > extinction * 0.9) continue;
    
    // 星星亮度：消光 + 个体亮度变异
    const brightness = extinction * (0.5 + hf(i + 13.37) * 0.5);  // 0.5-1.0
    
    // 亮星（~5%）可能变大到 2px — 模拟亮星/行星
    const isBright = hf(i + 137) > 0.95;
    const size = isBright ? 2 : STAR_SIZE;
    
    stars.push({ x: Math.round(x), y: Math.round(y), brightness, size });
  }
  return stars;
}
```

### 20.3 星星闪烁（Perlin 微动）

```javascript
// === 每帧更新 —— 星星不闪烁，但微弱的 Perlin 亮度变化模拟"大气闪烁" ===
function drawStars(stars, time, starsAlpha) {
  if (starsAlpha <= 0.01) return;  // 白天——不画
  
  for (const s of stars) {
    // 闪烁：Perlin 噪声在每颗星上产生 ±20% 的亮度微变
    const twinkle = 0.8 + noise(s.x * 0.05, s.y * 0.05, time * 0.3) * 0.4;
    const alpha = s.brightness * twinkle * starsAlpha;
    
    const c = lerpColor(
      hexToColor(STAR_COLOR_DIM), 
      hexToColor(STAR_COLOR_BRIGHT), 
      s.brightness
    );
    c.setAlpha(Math.round(alpha * 255));
    fill(c);
    rect(Math.round(s.x), Math.round(s.y), s.size * PX, s.size * PX);
  }
}

// 在 draw() 中：
// drawStars(stars, millis() * 0.001, starsAlpha);
```

### 20.4 月亮（可选）

```javascript
// === 像素月亮 — 天顶附近，确定性和 seed 绑定 ===
const MOON_RADIUS = 18;  // px — 在 640px 宽画布上约占 3%

function generateMoon(seed) {
  // 月亮位置——天顶偏右或偏左，由 seed 决定
  const moonX = width * (0.6 + hf(seed + 999) * 0.3);  // 0.6-0.9
  const moonY = horizonY * (0.15 + hf(seed + 997) * 0.2);  // 天顶 15-35%
  return { x: Math.round(moonX), y: Math.round(moonY) };
}

function drawMoon(moon, starsAlpha) {
  if (starsAlpha <= 0.3) return;  // 仅在天足够暗时出现
  
  // 月亮本体——粉彩白
  fill(lerpColor(color(0, 0, 0, 0), color(252, 248, 240, 255), starsAlpha));
  circle(moon.x, moon.y, MOON_RADIUS * 2 * PX);
  
  // 月亮光晕（可选）——微弱的径向渐变月华
  // 用 CSS radial-gradient 叠加在玻璃层（z=1 环境光斑层）比 canvas 内绘制更高效
}
```

### 20.5 夜景天空配色

Frutiger Aero 调色板中可以加入夜景模式：

```javascript
// 夜景天空渐变 — 深蓝到深紫，保持 Frutiger Aero 的柔和发光感
const NIGHT_SKY_TOP = '#0a1628';    // 深蓝黑——天顶
const NIGHT_SKY_BOT = '#1a2a3a';    // 稍浅——地平线光污染
// 黄昏过渡（日落时）：天空从白天色板平滑过渡到夜景
// → 用 skyBrightness 作为 lerp 因子：topColor = lerp(dayTop, nightTop, 1-starsAlpha)
```

### 20.6 反模式

| # | 反模式 | 级别 | 表现 | 修复 |
|---|--------|------|------|------|
| 1 | 星星用 `random()` 生成 | **致命** | 每次刷新星星位置不同 → 不可复现 | 用 `hf(i * prime1 + prime2)` 确定性 hash |
| 2 | 星星均匀分布 | 警告 | 地平线和天顶星星密度相同 → 平面感 | 用 `pow(heightRatio, 3.5)` 大气消光 |
| 3 | `if(skyBrightness < 0.2) showStars()` | 警告 | 硬阈值切换 → 星星突然出现 | `starsAlpha = clamp((0.35 - skyBrightness) * 5.0, 0, 1)` |
| 4 | 星星闪烁用 `random()` | 警告 | 每帧随机 → 像"故障噪点"而非"闪烁" | 用 `noise(x, y, time)` Perlin 微动 |
| 5 | 忘记 `starsAlpha` 守卫 | 警告 | 白天也在画星星 → 浪费性能 | `if (starsAlpha <= 0.01) return;` 放在 `drawStars()` 顶部 |

### 20.7 自检

- [ ] 星星位置是否用确定性 hash 生成（同一 seed = 同一星空）？
- [ ] 是否使用了大气消光 `pow(heightRatio, 3.5)`（非均匀分布）？
- [ ] 星星可见性是否从 `skyBrightness` 连续派生（非 `if(isNight)`）？
- [ ] 闪烁是否使用 Perlin noise（非 `random()`）？
- [ ] 白天是否跳过绘制（`starsAlpha <= 0.01` 守卫）？
- [ ] 星空是否与场景其他元素（月亮、云彩）协调共存？

### 20.8 夜景元素的统一数据派生

所有夜景元素从 `skyBrightness` 连续派生——不引入额外的二元状态（`isNight`/`isDusk`）：

```javascript
const fireflyAlpha  = clamp((0.4 - skyBrightness) * 4, 0, 1) * (0.5 + sin(time * 0.3) * 0.5);
const glowPlantAlpha = clamp((0.3 - skyBrightness) * 3, 0, 1);
const moonAlpha      = clamp((0.25 - skyBrightness) * 4, 0, 1) * moonPhase;
```

**⚠️ 伪数据驱动反模式**：`skyBrightness < 0.2 ? 1.0 : 0.0` 是二元分支伪装——用 `clamp` 提供连续过渡区间。

---

## 廿一、Aero-Ganzfeld 光空间模式

当用户提到"沉浸""冥想""光浴""漂浮感"时启用。
**核心原则：用 Ganzfeld 消除杂乱（静心），用 Aero 色调填补虚无（乐观治愈）。**

### 铁律
- **禁止深紫、纯黑、暗色**——光场必须是极高明度的 Aero 色系
- **交互必须正向**——反馈是泡泡/爱心/生长，不是惊吓/破坏
- **光变是奖励**——用户安抚宠物时背景变亮变暖，不是宗教肃穆的色相漂移

### 背景：Aero 光场
```css
/* 只使用高明度 Aero 色系，配合模糊气泡模拟水下/天空感 */
@keyframes aeroGlow {
  0%,100% { background: radial-gradient(ellipse, #c8e8f8 0%, #a8d8f0 40%, #e8f4f8 100%); }
  50%     { background: radial-gradient(ellipse, #d8f0e8 0%, #b8e8d8 40%, #f0f8f4 100%); }
}
body { animation: aeroGlow 25s ease-in-out infinite; }
```

### Aero 光场调色盘
- 天蓝→薄荷白：`#c8e8f8` `#e8f4f8`（清透天空）
- 极光粉→暖白：`#f8d8e8` `#f8f0f4`（温柔光浴）
- 薄荷绿→奶白：`#d8f0e8` `#f0f8f4`（水下呼吸）

### 流动水光感（光学补偿）
光场背景中叠加 CSS 极度模糊（`blur(30px)`）的巨大半透明气泡或极光条带，缓慢漂浮——模拟水下/天空的均质生机感。
```css
.water-orb {
  position: fixed; border-radius: 50%; filter: blur(30px); opacity: .25;
  background: rgba(255,255,255,.6); animation: orbDrift 18s ease-in-out infinite;
}
@keyframes orbDrift {
  0%,100% { transform: translate(0,0) scale(1); }
  50%     { transform: translate(40px,-30px) scale(1.3); }
}
```

### 运动拖影（Trail Effect）
不全清画布 → 像素物体留下梦幻残影，模拟感官剥夺中的视觉残留。
```javascript
// 替代 clear()：半透明背景叠加，旧帧缓慢消隐
fill(10, 8, 20, 12); rect(0, 0, width, height);
```

### 声音：轻柔氛围（非感官剥夺）
配合 432Hz 正弦波底噪 + 极低音量粉红噪音（≤ 0.04 gain）。双耳节拍为可选项——仅在用户明确需要深度冥想时启用。

### 交互：正向光浴（Positive Color Bathing）
用户安抚宠物时，背景光场变为**更亮更暖的奖励色**——天蓝→暖白，薄荷绿→极光粉。这是"被爱"的环境光反馈，不是宗教仪式。宠物同时吐透明泡泡/冒像素爱心。

### 容器即透镜（Skyspace Lens）
在此模式下，玻璃容器的高光不反射白光——反射**背景光场的颜色**。容器的 `::after` 伪元素渐变色跟随光场色相。容器内部比外部光场暗 10-20%，产生"透过玻璃看到另一个光维度"的视错觉。

### 情绪流体背景（Mood Flow Field）
在 Canvas 底层叠加一个 Perlin 噪声向量场驱动的粒子层。粒子的**流向、密度、速度**编码情绪——不同情绪 = 不同向量场参数。

```javascript
// z-index: 1 的独立 Canvas 或 draw() 中最早渲染
for (let p of flowParticles) {
  let angle = noise(p.x * 0.003, p.y * 0.003, frameCount * 0.002) * TWO_PI;
  p.vx += cos(angle) * 0.05; p.vy += sin(angle) * 0.05;
  p.vx *= 0.96; p.vy *= 0.96; // 阻尼
  p.x += p.vx; p.y += p.vy;
  fill(180, 200, 230, 30); circle(p.x, p.y, 2); // 极淡粒子
}
```

**情绪→向量场映射：**
- 雨/忧郁：`noise` 主方向向下（`vy += 0.02` 微重力），水平波动小，粒子稀疏
- 春/希望：`noise` 主方向向上旋（`vy -= 0.01`），横向波动大，粒子密集成束
- 焦虑/湍流：`noise` 频率加倍（`* 0.006`），速度上限提高，粒子快速穿梭
- 宁静/冥想：`noise` 频率减半（`* 0.001`），粒子密度降低，近乎静止

粒子层永远是**背景**——不抢夺主体像素生命体的视觉权重，但为场景注入不可见的情绪信息。

---

## 引用索引

| 主题 | 文件 |
|------|------|
| 完整五维像素规范 | `references/pixel-grid-system.md` |
| 防御性骨架 + wrapper | `references/code-templates.md §防御性前端骨架` |
| 玻璃容器三榻饼管线 | `references/code-templates.md §玻璃容器渲染` |
| 像素工具函数（Bayer/snap/字体） | `references/code-templates.md §像素实体系统` |
| 海洋波浪完整系统 | `references/ocean-pixels.md` |
| 程序化植被系统 | `references/vegetation-system.md` |

