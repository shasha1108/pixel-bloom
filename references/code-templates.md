# Pixel Bloom — 代码模板

> 防御性骨架 + 程序化模型 + FSM + 交互模板 + 质检清单。直接复制，不要从零发明。

**叠加公式**：Z-index 层级规范见 `design-principles.md §一`，不得更改。

**入场序列（分层错开）：**

1. 底板层先渲染（毛玻璃 + 渐变底色），0.3s
2. Canvas 像素层淡入（生命体逐个出现），再 0.5s
3. 玻璃壳 + UI 层最后浮现（光泽 + 引导文字），再 0.4s

```css
.bg-layer    { animation: fadeIn 0.6s ease-out 0s both; }
.canvas-layer { animation: fadeIn 0.8s ease-out 0.3s both; }
.glass-layer  { animation: fadeIn 0.6s ease-out 0.8s both; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
```

---

## 防御性前端骨架 — Unified Pixel Stage（全视口 / 固定画布双模式）

### 架构铁律：Wrapper 统一坐标系统

**旧反模式**：每个层各自 `position: fixed` + 视口单位（vw/vh），canvas 用 JS 独立定位。各层尺寸不同、坐标系统不同 → 固定画布 640×960 被 90vw×88vh 的玻璃壳 `::after` 白色渐变彻底盖死。

**新铁律**：所有视觉层（光斑 → 玻璃底板 → canvas → 玻璃外壳 → 交互层）必须在同一个容器 `#pixel-stage` 内，使用 `position: absolute` + 百分比单位。容器尺寸 = 画布显示尺寸，由 JS 统一计算。**任何 layer 不得单独使用 `position: fixed`。**

```
#pixel-stage (position:fixed, 居中于视口, overflow:hidden)
├── .ambient-light   (position:absolute, z=1, % 单位)
├── .glass-bg        (position:absolute, z=2, % 单位, 唯一有 backdrop-filter:blur 的层)
├── <canvas>         (position:absolute, z=3, 填满容器, c.parent('pixel-stage'))
├── .glass-shell     (position:absolute, z=4, % 单位, 禁止 backdrop-filter)
└── #interact-layer  (position:absolute, z=5, inset:0)
```

**模式切换只需改两处**：CSS 中 `#pixel-stage` 的尺寸规则 + JS 中 `createCanvas()` 参数和 `windowResized()` 逻辑。其余所有层无需修改。

```html
<!DOCTYPE html>
<!--
  Title: <场景名称，如"像素水族箱">
  Concept: <1-2词名字 — 这个作品送给用户的那句话>
  Summary: <主角 + 核心交互，一句话，如"三条像素鱼 + 点击喂食 + 双击敲玻璃">
  Tech: p5.js, Canvas, CSS Glassmorphism, Web Audio API
  Keywords: <pixel, 场景词，如 aquarium, frutiger-aero, cyber-pet>
  Render: <fullViewport | fixedCanvas>
  Audio: <yes | no>
  Touch: <singleTap=行为, doubleTap=行为，无交互则写 none>
  Dependencies: p5.js 1.9.0
  Repo: pixel-bloom
-->
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Pixel Bloom</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.0/p5.min.js"></script>
<script>window.p5||document.write('<script src="https://cdn.bootcdn.net/ajax/libs/p5.js/1.9.0/p5.min.js"><\/script>');</script>
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  html, body {
    width: 100vw; height: 100vh; overflow: hidden;
    background: linear-gradient(160deg, #a8e6f8 0%, #cdf0fa 30%, #e4f8f0 65%, #f4fcf9 100%);
    font-family: "Segoe UI", "Frutiger", "Trebuchet MS", "PingFang SC", sans-serif;
    user-select: none; -webkit-user-select: none; touch-action: none;
  }

  /* ═══════════════════════════════════════════════════════════════
     UNIFIED PIXEL STAGE — 所有视觉层的唯一定位容器
     ═══════════════════════════════════════════════════════════════
     固定画布模式：JS 计算 scale 并设置 width/height（保持 aspect-ratio）
     全视口模式：  取消下面的注释，使用 100vw×100vh
     overflow:hidden 裁剪溢出的玻璃效果（::after 菲涅尔高光等）*/
  #pixel-stage {
    position: fixed;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    overflow: hidden;
    /* width / height 由 JS 的 sizeStage() 动态计算 */
  }
  /* ── 切换为全视口模式（取消注释以下 4 行，同时修改 JS 中 createCanvas）──
  #pixel-stage {
    width: 100vw; height: 100vh; top: 0; left: 0; transform: none;
  }
  */

  /* 环境光斑（z-index: 1 — 相对于 #pixel-stage，% 单位）*/
  .ambient-light {
    position: absolute; z-index: 1; pointer-events: none; border-radius: 50%;
    background: radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 60%);
  }

  /* 毛玻璃底板（z-index: 2 — canvas 之下。唯一允许 backdrop-filter 的层）*/
  .glass-bg {
    position: absolute; z-index: 2; pointer-events: none;
    top: 3%; left: 3%; right: 3%; bottom: 3%;
    border-radius: 24px;
    background: rgba(255,255,255,0.12);
    backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
  }

  /* 透明玻璃外壳（z-index: 4 — canvas 之上。禁止 backdrop-filter）*/
  .glass-shell {
    position: absolute; z-index: 4; pointer-events: none;
    top: 3%; left: 3%; right: 3%; bottom: 3%; border-radius: 24px;
    border-top: 2px solid rgba(255,255,255,0.85);
    border-left: 2px solid rgba(255,255,255,0.5);
    border-right: 1px solid rgba(255,255,255,0.25);
    border-bottom: 1px solid rgba(255,255,255,0.15);
    box-shadow: inset 0 0 20px rgba(255,255,255,0.35),
                inset 0 50px 50px rgba(255,255,255,0.15);
  }
  .glass-shell::after {
    content: ''; position: absolute;
    top: -5%; left: -2%; width: 104%; height: 35%;
    background: linear-gradient(180deg, rgba(255,255,255,0.4) 0%, transparent 100%);
    border-radius: 50%; transform: rotate(-8deg);
    /* #pixel-stage 的 overflow:hidden 裁剪溢出部分，防止覆盖画布外部 */
  }

  /* 交互拦截层（z-index: 5，填满整个容器）*/
  #interact-layer { position: absolute; inset: 0; z-index: 5; }
</style>
</head>
<body>

<div id="pixel-stage">
  <!-- ⚠️ 开放场景（像素风景/森林·开放模式）：删除以下三板——毛玻璃是封闭容器专属 -->
  <div class="ambient-light" style="width:30%;height:30%;top:-5%;left:5%;"></div>
  <div class="ambient-light" style="width:22%;height:22%;bottom:8%;right:5%;"></div>
  <div class="glass-bg"></div>
  <div class="glass-shell"></div>
  <div id="interact-layer"></div>
</div>

<script>
// ═══════════════════════════════════════════════════════════════
// 固定画布模式：设置像素分辨率 → canvas CSS 填满 wrapper → 像素级缩放
// 全视口模式：  注释 CW/CH，createCanvas(windowWidth,windowHeight)
// ═══════════════════════════════════════════════════════════════
let CW = 640, CH = 960;

function setup() {
  let cvs = createCanvas(CW, CH);
  cvs.parent('pixel-stage');

  // Canvas 填满父容器 #pixel-stage（CSS 缩放，image-rendering:pixelated 保持锐利）
  cvs.style('display', 'block');
  cvs.style('position', 'absolute');
  cvs.style('top', '0'); cvs.style('left', '0');
  cvs.style('width', '100%'); cvs.style('height', '100%');
  cvs.style('z-index', '3');
  cvs.style('pointer-events', 'none');
  cvs.style('image-rendering', 'pixelated');
  cvs.style('filter', 'drop-shadow(0px 8px 6px rgba(0,80,120,0.15))');

  noSmooth();
  pixelDensity(1);

  CW = width; CH = height;  // 确认实际分辨率
  sizeStage();  // 计算 wrapper CSS 显示尺寸

  // ⚠️ 所有依赖画布尺寸的实体初始化放在 sizeStage() 之后
}

// ── Wrapper 尺寸计算 ──
// 根据画布像素尺寸 × 视口大小，计算 #pixel-stage 的 CSS 显示尺寸。
// 结果：wrapper 居中于视口，保持画布 aspect-ratio，所有子层自动对齐。
function sizeStage() {
  const stage = document.getElementById('pixel-stage');
  const scale = Math.min(windowWidth / CW, windowHeight / CH);
  stage.style.width  = Math.floor(CW * scale) + 'px';
  stage.style.height = Math.floor(CH * scale) + 'px';
}

function draw() {
  clear(); // 透明背景 → body 渐变 → glass-bg blur → canvas 像素层
}

// 固定画布模式：只重算 wrapper 尺寸，不改变 canvas 分辨率。
// 全视口模式：改为 resizeCanvas(windowWidth, windowHeight); pixelDensity(1);
function windowResized() {
  sizeStage();
}
</script>
</body>
</html>
```

**关键点：**
- 所有层（光斑/玻璃底板/玻璃外壳/交互层）使用 `position: absolute` + `%` 单位，相对于 `#pixel-stage`
- **`backdrop-filter: blur()` 只存在于 `.glass-bg`（z=2，canvas 之下）**——外壳层（z=4）绝对禁止
- Canvas 通过 `c.parent('pixel-stage')` 挂入容器，CSS `width:100%; height:100%` 填满
- `#pixel-stage` 的 `overflow: hidden` 裁剪 `::after` 菲涅尔高光溢出，防止覆盖画布外部
- 固定画布模式：`windowResized()` 只调 `sizeStage()`，不改 canvas 分辨率 → 像素永远锐利
- 全视口模式：取消 CSS 注释 + `createCanvas(windowWidth, windowHeight)` + `resizeCanvas(windowWidth, windowHeight)`

---

## 玻璃容器渲染（Canvas-Only Frutiger Aero Glass Pipeline）

> **铁律：玻璃的形状、折射与高光必须 100% 在 Canvas 内部绘制。禁止使用 CSS `backdrop-filter` / `border-radius` / `box-shadow` 模拟玻璃容器。**

### 理论基石（为什么 CSS 永远做不出真玻璃）

Frutiger Aero 拟物玻璃不是"半透明白色 + 模糊"。它由三个物理光学效应叠加而成：

| 效应 | 物理原理 | CSS 能做什么 | Canvas 能做什么 |
|------|---------|-------------|----------------|
| **菲涅尔反射** | 视线越贴近曲面切线 → 反射率越高。正对时反射 ~4%（F0），掠射时反射 ~100% | `linear-gradient` 固定角度，不随曲面曲率变化 | 沿曲面法线计算 `schlick(cosθ)`，边缘自动亮起 |
| **比尔吸收** | 光穿过玻璃的路径越长 → 被吸收越多。边缘路径 > 中心路径 → 边缘更暗/更绿 | 无厚度概念，只能 `box-shadow: inset` 均匀内发光 | 计算每个像素的光程 `thickness = 2√(r²-d²)`，边缘指数衰减 |
| **曲面高光** | 环境光源在曲面上的镜像反射。柱面玻璃 = 条带状，球面玻璃 = 点状，瓶口 = 环状 | `::after` 对角线固定渐变，不随曲面曲率走向 | `beginShape()` + `bezierCurveTo()` 沿曲面绘制条带状高光 + `globalCompositeOperation: screen` |

**关键公式（2D 简化版）：**

```javascript
// Schlick Fresnel 近似
// cosTheta = 曲面法线与视线夹角。中心=1（正对），边缘=0（掠射）
// F0 = 0.04（玻璃 IOR ≈ 1.5）
function fresnel(cosTheta) {
  return 0.04 + 0.96 * Math.pow(1 - cosTheta, 5);
}

// Beer-Lambert 吸收
// thickness = 2 * sqrt(radius² - distFromCenter²)（球体光程）
// sigma = 吸收系数（玻璃越绿，G 通道 sigma 越小）
function beerAttenuation(thickness, sigma) {
  return Math.exp(-sigma * thickness);
}
```

### 渲染管线：三榻饼（Sandwich）结构

全部在 Canvas 内部完成，与 CSS 彻底隔绝：

```
1. ctx.save() → defineBottlePath() → 瓶后体块（径向渐变底色）→ ctx.restore()
2. ctx.save() → defineBottlePath() → ctx.clip() → [瓶内水体/信纸/小船/气泡] → ctx.restore()
3. ctx.save() → [瓶底沉淀厚度] → [菲涅尔边缘描边] → [曲面条带高光screen] → [瓶口反射环] → ctx.restore()
4. ctx.save() → [软木塞3D圆柱体] → ctx.restore()
```

---

### 完整代码模板

```javascript
// ============================================================
// § 玻璃容器渲染 (Frutiger Aero Glass Container System)
// 基于 Schlick Fresnel + Beer-Lambert + Clip Mask Pipeline
// 依赖：p5.js (noSmooth + pixelDensity(1))
// ============================================================

/**
 * 绘制完整的拟物化玻璃漂流瓶及其内部生态
 * @param {Object} cfg — { x, y, w, h, liquidLevel, time, drawContents }
 *   x, y      — 瓶子包围盒中心
 *   w, h      — 瓶子包围盒宽高（瓶身最大宽度 × 总高度）
 *   liquidLevel — 水面高度 0.0(空)~1.0(满)，默认 0.5
 *   time      — 时间参数（秒），用于波浪动画
 *   drawContents(ctx, bounds) — 回调：在 clip 遮罩内绘制瓶内物体
 *     bounds = { x, y, w, h, waterY, bottlePath }
 */
function drawAeroGlassBottle(cfg) {
  const { x, y, w, h, liquidLevel = 0.5, time = 0 } = cfg;
  const ctx = drawingContext; // p5.js 暴露的原生 Canvas2D 上下文

  // ═══════════════════════════════════════════════════════
  // 1. 瓶身路径（贝塞尔曲线 — 类药瓶/漂流瓶形状）
  // ═══════════════════════════════════════════════════════
  function defineBottlePath() {
    ctx.beginPath();
    // 瓶颈 — 直线段
    const neckW = w * 0.18;          // 瓶颈半宽
    const neckTop = y - h * 0.48;    // 瓶口顶部 Y
    const neckBot = y - h * 0.30;    // 瓶颈底部 Y
    const bodyTop = y - h * 0.12;    // 瓶肩结束 Y
    const bodyBot = y + h * 0.38;    // 瓶底 Y
    const bodyW = w * 0.48;          // 瓶身半宽
    const baseR = w * 0.05;          // 瓶底圆角半径

    // 瓶口左上 → 瓶颈左上
    ctx.moveTo(x - neckW, neckTop);
    ctx.lineTo(x - neckW, neckBot);

    // 左肩曲线（瓶颈 → 瓶身）
    ctx.bezierCurveTo(
      x - neckW, bodyTop,           // 控制点 1
      x - bodyW * 1.05, bodyTop,    // 控制点 2
      x - bodyW, y + h * 0.05       // 终点（瓶身左侧）
    );

    // 左壁 → 瓶底左圆角
    ctx.lineTo(x - bodyW, bodyBot - baseR);
    ctx.quadraticCurveTo(x - bodyW, bodyBot + baseR, x - bodyW + baseR, bodyBot + baseR);

    // 瓶底弧线
    ctx.quadraticCurveTo(x, bodyBot + baseR * 1.8, x + bodyW - baseR, bodyBot + baseR);

    // 瓶底右圆角 → 右壁
    ctx.quadraticCurveTo(x + bodyW, bodyBot + baseR, x + bodyW, bodyBot - baseR);
    ctx.lineTo(x + bodyW, y + h * 0.05);

    // 右肩曲线（瓶身 → 瓶颈）
    ctx.bezierCurveTo(
      x + bodyW * 1.05, bodyTop,
      x + neckW, bodyTop,
      x + neckW, neckBot
    );

    // 瓶颈右上 → 瓶口右上
    ctx.lineTo(x + neckW, neckTop);

    // 瓶口顶线
    ctx.lineTo(x - neckW, neckTop);
    ctx.closePath();
  }

  // ═══════════════════════════════════════════════════════
  // 2. 瓶后体块 — 玻璃背壁的透光底色
  // ═══════════════════════════════════════════════════════
  ctx.save();
  defineBottlePath();

  // 径向渐变：中心透亮（冰蓝-青绿），边缘向深绿过渡
  const backGrad = ctx.createRadialGradient(x, y - h * 0.05, w * 0.08, x, y, h * 0.55);
  backGrad.addColorStop(0, 'rgba(210, 245, 255, 0.12)');   // 中心 — 极淡冰蓝
  backGrad.addColorStop(0.5, 'rgba(160, 225, 210, 0.18)');  // 中间 — 淡青绿
  backGrad.addColorStop(0.85, 'rgba(80, 170, 150, 0.30)');  // 近边缘 — 中绿（比尔吸收）
  backGrad.addColorStop(1, 'rgba(30, 100, 85, 0.45)');      // 极边缘 — 深绿
  ctx.fillStyle = backGrad;
  ctx.fill();
  ctx.restore();

  // ═══════════════════════════════════════════════════════
  // 3. 遮罩裁剪管线 — 所有瓶内物体在此闭包内绘制
  // ═══════════════════════════════════════════════════════
  ctx.save();
  defineBottlePath();
  ctx.clip();

  // —— 3a. 瓶内水体 ——
  const waterTop = y + h * 0.38 - (h * 0.65 * liquidLevel);

  // 水体底色（自上而下：浅蓝 → 深海蓝）
  const waterGrad = ctx.createLinearGradient(0, waterTop, 0, y + h * 0.45);
  waterGrad.addColorStop(0, 'rgba(120, 215, 240, 0.70)');
  waterGrad.addColorStop(0.3, 'rgba(60, 170, 210, 0.80)');
  waterGrad.addColorStop(1, 'rgba(15, 80, 140, 0.92)');
  ctx.fillStyle = waterGrad;
  ctx.fillRect(x - w, waterTop, w * 2, y + h * 0.5 - waterTop);

  // 水面波浪线
  ctx.fillStyle = 'rgba(180, 230, 250, 0.55)';
  ctx.beginPath();
  ctx.moveTo(x - w, waterTop);
  for (let lx = -w; lx <= w; lx += 4) {
    const waveY = waterTop + Math.sin(lx * 0.035 + time * 2.5) * 5
                           + Math.sin(lx * 0.07 + time * 1.7) * 3;
    ctx.lineTo(x + lx, waveY);
  }
  ctx.lineTo(x + w, y + h * 0.5);
  ctx.lineTo(x - w, y + h * 0.5);
  ctx.closePath();
  ctx.fill();

  // 水面高光环（椭圆形，模拟瓶内水面反光）
  ctx.fillStyle = 'rgba(255, 255, 255, 0.35)';
  ctx.beginPath();
  ctx.ellipse(x, waterTop + 4, w * 0.40, 8, 0, 0, Math.PI * 2);
  ctx.fill();

  // —— 3b. 上升气泡 ——
  for (let i = 0; i < 8; i++) {
    const bx = x + Math.sin(time * 1.3 + i * 1.9) * (w * 0.32);
    const rise = ((time * 22 + i * 47) % (h * 0.55));
    const by = waterTop + 12 + rise;
    if (by < y + h * 0.45 && by > waterTop + 4) {
      // 气泡高光
      ctx.fillStyle = 'rgba(255, 255, 255, 0.55)';
      ctx.beginPath();
      ctx.arc(bx, by, 1.5 + (i % 3) * 0.8, 0, Math.PI * 2);
      ctx.fill();
      // 高光点
      ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
      ctx.beginPath();
      ctx.arc(bx - 0.8, by - 0.8, 0.6, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  // —— 3c. 用户自定义内容（信纸/小船等）——
  if (cfg.drawContents) {
    cfg.drawContents(ctx, { x, y, w, h, waterY: waterTop, bottlePath: defineBottlePath });
  }

  ctx.restore(); // ★ 结束 clip

  // ═══════════════════════════════════════════════════════
  // 4. 瓶前玻璃曲面 — 拟物核心（按绘制顺序叠加）
  // ═══════════════════════════════════════════════════════

  // —— 4a. 瓶底沉淀厚度（Thick Glass Base）——
  // 玻璃底部最厚 → 颜色最深 → 径向椭圆渐变
  ctx.save();
  const baseGrad = ctx.createLinearGradient(0, y + h * 0.32, 0, y + h * 0.46);
  baseGrad.addColorStop(0, 'rgba(0, 0, 0, 0)');
  baseGrad.addColorStop(0.4, 'rgba(25, 85, 70, 0.28)');
  baseGrad.addColorStop(0.75, 'rgba(10, 60, 50, 0.50)');
  baseGrad.addColorStop(1, 'rgba(5, 35, 30, 0.65)');
  ctx.fillStyle = baseGrad;
  ctx.beginPath();
  ctx.ellipse(x, y + h * 0.40, w * 0.44, h * 0.06, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // —— 4b. 菲涅尔边缘厚度描边（Fresnel Dark/Green Edge Rim）——
  // 玻璃边缘 = 光程最长 → 最暗最绿
  ctx.save();
  defineBottlePath();
  const edgeGrad = ctx.createLinearGradient(x - w * 0.5, 0, x + w * 0.5, 0);
  edgeGrad.addColorStop(0, 'rgba(15, 70, 60, 0.55)');    // 左边缘 — 深绿
  edgeGrad.addColorStop(0.08, 'rgba(255, 255, 255, 0.75)'); // 左侧内亮线
  edgeGrad.addColorStop(0.2, 'rgba(255, 255, 255, 0.06)'); // 过渡
  edgeGrad.addColorStop(0.5, 'rgba(255, 255, 255, 0.0)');  // 中心 — 透明
  edgeGrad.addColorStop(0.8, 'rgba(255, 255, 255, 0.05)'); // 过渡
  edgeGrad.addColorStop(0.92, 'rgba(255, 255, 255, 0.40)'); // 右侧内亮线
  edgeGrad.addColorStop(1, 'rgba(12, 55, 45, 0.45)');     // 右边缘 — 深绿
  ctx.strokeStyle = edgeGrad;
  ctx.lineWidth = 3.5;
  ctx.stroke();
  ctx.restore();

  // —— 4c. 曲面主高光条（Curved Specular Bar）——
  // ★ 关键：使用 globalCompositeOperation = 'screen' 实现光叠加
  // 高光沿左侧瓶身曲面弯曲，模拟环境矩形光源在柱面上的镜像反射
  ctx.save();
  ctx.globalCompositeOperation = 'screen';

  const specGrad = ctx.createLinearGradient(x - w * 0.45, 0, x - w * 0.05, 0);
  specGrad.addColorStop(0, 'rgba(255, 255, 255, 0.0)');
  specGrad.addColorStop(0.25, 'rgba(255, 255, 255, 0.88)'); // 刺眼强高光峰
  specGrad.addColorStop(0.55, 'rgba(210, 245, 255, 0.35)'); // 扩散
  specGrad.addColorStop(1, 'rgba(255, 255, 255, 0.0)');

  ctx.fillStyle = specGrad;
  ctx.beginPath();
  // 沿左侧瓶身曲面走势的高光条带
  const bodyTop = y - h * 0.12;
  const bodyBot = y + h * 0.38;
  const bodyW = w * 0.48;
  const hlInner = w * 0.14;    // 高光内缘距中心距离
  const hlOuter = w * 0.42;    // 高光外缘距中心距离

  ctx.moveTo(x - hlInner, y - h * 0.45);
  ctx.bezierCurveTo(x - hlInner * 0.9, bodyTop, x - hlOuter * 0.95, bodyTop, x - hlOuter, y + h * 0.08);
  ctx.lineTo(x - hlOuter, bodyBot - w * 0.06);
  ctx.quadraticCurveTo(x - hlOuter * 0.9, bodyBot + w * 0.02, x - hlInner * 0.7, bodyBot);
  ctx.lineTo(x - hlInner * 0.7, y + h * 0.08);
  ctx.bezierCurveTo(x - hlInner * 0.8, bodyTop, x - hlInner * 0.3, bodyTop, x - hlInner * 0.3, y - h * 0.45);
  ctx.closePath();
  ctx.fill();

  ctx.restore(); // 恢复 blend mode

  // —— 4d. 瓶口全反射光环（Mouth Ring Reflection）——
  // 圆形瓶口边缘 = 光线在玻璃-空气界面全反射 → 亮环
  ctx.save();
  const mouthY = y - h * 0.48;
  const mouthW = w * 0.18;
  const mouthGrad = ctx.createLinearGradient(x - mouthW, 0, x + mouthW, 0);
  mouthGrad.addColorStop(0, 'rgba(255, 255, 255, 0.85)');   // 左 — 刺眼
  mouthGrad.addColorStop(0.25, 'rgba(255, 255, 255, 0.25)'); // 左中 — 衰减
  mouthGrad.addColorStop(0.5, 'rgba(255, 255, 255, 0.10)');  // 中心 — 几乎透明
  mouthGrad.addColorStop(0.75, 'rgba(255, 255, 255, 0.30)'); // 右中
  mouthGrad.addColorStop(1, 'rgba(255, 255, 255, 0.75)');    // 右 — 亮
  ctx.strokeStyle = mouthGrad;
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.ellipse(x, mouthY, mouthW, h * 0.018, 0, 0, Math.PI * 2);
  ctx.stroke();

  // 瓶口内缘第二圈（稍细、稍暗）
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.30)';
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.ellipse(x, mouthY, mouthW * 0.88, h * 0.013, 0, 0, Math.PI * 2);
  ctx.stroke();
  ctx.restore();

  // ═══════════════════════════════════════════════════════
  // 5. 软木塞层（3D Cork Stopper）
  // ═══════════════════════════════════════════════════════
  ctx.save();
  const corkW = w * 0.32;
  const corkH = h * 0.07;
  const corkX = x - corkW / 2;
  const corkTop = y - h * 0.48 - corkH * 0.75;

  // 木塞本体 — 3D 圆柱侧面渐变（亮面→固有色→暗面→反光→暗面）
  const corkGrad = ctx.createLinearGradient(corkX, 0, corkX + corkW, 0);
  corkGrad.addColorStop(0, '#7a4e2d');    // 左阴影边
  corkGrad.addColorStop(0.15, '#c49464'); // 高光脊（左上光源）
  corkGrad.addColorStop(0.4, '#d4a878');  // 固有色亮部
  corkGrad.addColorStop(0.6, '#b8845c');  // 固有色暗部
  corkGrad.addColorStop(0.85, '#e0c098'); // 右反光带（环境光反射）
  corkGrad.addColorStop(1, '#5a3520');    // 右深阴影边

  // 圆角矩形（上圆角大、下圆角小 — 模拟上大下小的瓶塞）
  ctx.fillStyle = corkGrad;
  ctx.beginPath();
  const crTop = 5, crBot = 3;
  ctx.moveTo(corkX + crTop, corkTop);
  ctx.lineTo(corkX + corkW - crTop, corkTop);
  ctx.quadraticCurveTo(corkX + corkW, corkTop, corkX + corkW, corkTop + crTop);
  ctx.lineTo(corkX + corkW, corkTop + corkH - crBot);
  ctx.quadraticCurveTo(corkX + corkW, corkTop + corkH, corkX + corkW - crBot, corkTop + corkH);
  ctx.lineTo(corkX + crBot, corkTop + corkH);
  ctx.quadraticCurveTo(corkX, corkTop + corkH, corkX, corkTop + corkH - crBot);
  ctx.lineTo(corkX, corkTop + crTop);
  ctx.quadraticCurveTo(corkX, corkTop, corkX + crTop, corkTop);
  ctx.closePath();
  ctx.fill();

  // 木塞竖向纹理（软木孔隙线）
  ctx.strokeStyle = 'rgba(80, 40, 15, 0.20)';
  ctx.lineWidth = 1.0;
  const seamCount = 5;
  for (let i = 1; i <= seamCount; i++) {
    const sx = corkX + (corkW / (seamCount + 1)) * i;
    // 轻微随机偏移（确定性 hash）
    const jitter = ((i * 17 + 3) % 7 - 3) * 0.6;
    ctx.beginPath();
    ctx.moveTo(sx + jitter, corkTop + 2);
    ctx.lineTo(sx - jitter * 0.5, corkTop + corkH - 2);
    ctx.stroke();
  }

  ctx.restore();
}
```

### 集成到 setup() 中的调用方式

```javascript
// 在 draw() 中调用 — 瓶子绘制在 Canvas 内部，与其他像素元素共享同一画布
function draw() {
  clear(); // 透明背景 → body CSS 渐变透出

  // 1. 先绘制瓶后背景元素（远处波浪、天空等，如有）
  // drawDistantBackground();

  // 2. 绘制瓶子及其内部生态
  drawAeroGlassBottle({
    x: CW / 2,        // 瓶子中心 X（画布中央）
    y: CH * 0.55,     // 瓶子中心 Y（偏下，给软木塞留空间）
    w: CW * 0.38,     // 瓶身宽度
    h: CH * 0.72,     // 瓶子高度
    liquidLevel: 0.55,
    time: millis() * 0.001,
    drawContents: (ctx, bounds) => {
      // 在此 callback 内绘制瓶内自定义物体
      // 所有绘制自动被瓶身 clip 遮罩裁剪
      // drawPaperBoat(ctx, bounds);
      // drawFoldedLetter(ctx, bounds);
    }
  });

  // 3. 绘制瓶外元素（前景波浪、泡沫等）
  // drawForegroundWaves();
}
```

### 铁律（Iron Law）

**三条禁止**：
1. ❌ 禁止使用 CSS `backdrop-filter: blur()` 或 `border-radius` 模拟玻璃容器形状或质感
2. ❌ 禁止将玻璃高光放在独立 CSS 层（`::after` / `.glass-shell`）— 高光必须沿 Canvas 曲面路径绘制
3. ❌ 禁止在无 `ctx.save()`/`ctx.restore()` 保护下调用 `ctx.clip()` — 裁剪区域不可逆

**三条强制**：
1. ✅ 所有瓶内物体（水、船、信纸、气泡）必须包裹在 `ctx.save()` → `defineBottlePath()` → `ctx.clip()` → `[内容]` → `ctx.restore()` 闭包中
2. ✅ 玻璃高光必须包含三项：沿曲面带状渐变条（`globalCompositeOperation = 'screen'`）+ 瓶口椭圆全反射环 + 菲涅尔绿/暗色边缘描边
3. ✅ 曲面高光条带路径必须使用 `bezierCurveTo()` 跟随瓶身曲线走向 — 禁止 `rect()` 或 `circle()` 替代

### 调色板参考：Frutiger Aero 玻璃色

| 用途 | 色值 | 说明 |
|------|------|------|
| 瓶后透光中心 | `rgba(210,245,255,0.12)` | 冰蓝 — 极淡，模拟薄玻璃中心透光 |
| 瓶后透光边缘 | `rgba(30,100,85,0.45)` | 深绿 — 比尔吸收后边缘色 |
| 菲涅尔边缘描边 | `rgba(15,70,60,0.55)` | 深墨绿 — 光程最长处 |
| 高光峰 | `rgba(255,255,255,0.88)` | 纯白 — screen 混合下刺眼亮 |
| 瓶底沉淀 | `rgba(5,35,30,0.65)` | 暗绿褐 — 最厚玻璃底 |
| 软木塞固有色 | `#d4a878` | 暖木色 — 与玻璃冷色形成冷暖对比 |
| 软木塞阴影边 | `#5a3520` | 深棕 — 3D 圆柱暗面 |



### 像素角色（通用 Sprite 网格）

```javascript
// 角色像素数据：0=空, 1=身体主色, 2=眼睛/高光, 3=附属色(鳍/翅膀/耳朵)
// 使用时 translate(round(x), round(y)) 后调用
function drawPixelSprite(shape, palette, px) {
  for (let row = 0; row < shape.length; row++) {
    for (let col = 0; col < shape[row].length; col++) {
      const cell = shape[row][col];
      if (!cell) continue;
      const sx = (col - floor(shape[row].length / 2)) * px;
      const sy = (row - floor(shape.length / 2)) * px;
      noStroke();
      if (cell === 1) fill(palette.body);
      else if (cell === 2) fill(palette.eye);
      else if (cell === 3) fill(palette.accent);
      rect(sx, sy, px, px);
    }
  }
}
```

---

## 程序化生态生成（Procedural Flora）

不手画每一个像素，用算法生成具备有机感的聚落。以下四种模型覆盖赛博养花/养宠的绝大部分场景。

### 模型 A：向上堆叠 + 正弦摇摆（水草/海带/花茎/柳条）

```javascript
function drawStackSway(baseX, baseY, segments, px, color1, color2, phase) {
  for (let i = 0; i < segments; i++) {
    let sway = sin(phase + i * 0.3) * (i * px * 0.2);
    fill(i % 2 === 0 ? color1 : color2);
    rect(round(baseX + sway), baseY - i * px, px * 1.5, px);
  }
}
```

### 模型 B：网格阵列 + 随机剔除（灌木/树冠/草丛/云朵）

```javascript
function drawGridCluster(baseX, baseY, gridW, gridH, px, palette, density) {
  for (let by = 0; by < gridH; by++) {
    for (let bx = -gridW; bx <= gridW; bx++) {
      if (random() > density) continue;  // density = 像素保留比例
      fill(random(palette));
      rect(baseX + bx * px, baseY - by * px, px, px);
    }
  }
}
```

> **☁️ 云彩适配**：模型 B 同样用于像素云彩，参数调整——density 0.3-0.5（更蓬松）、噪声频率改用 Perlin noise 驱动（`noise(x*0.04, y*0.04)`，阈值 `= 1 - density`）、调色板用白→淡灰蓝（`['#f8fafc','#e8f0f8','#d0dce8','#b8c8d8']` 或夕阳暖色/阴云灰蓝/夜云暗色）。宽高比横向（宽:高 = 2:1~3:1，与树冠的竖直方向相反）。

### 模型 C：圆域筛选 / 勾股定理（脑纹珊瑚/花蕊/蘑菇/球形灌木）

```javascript
function drawRadialCluster(baseX, baseY, radius, px, palette, density = 0.85) {
  for (let dy = 0; dy < radius; dy++) {
    let limit = round(sqrt(radius * radius - dy * dy));
    for (let dx = -limit; dx <= limit; dx++) {
      if (random() > density) continue;  // density = 像素保留比例（0.85 = 原默认行为）
      fill(random(palette));
      rect(baseX + dx * px, baseY - dy * px, px, px);
    }
  }
}
```

### 模型 D：扇形展开（海扇/孔雀屏/棕榈叶/扇形珊瑚）

```javascript
function drawFan(baseX, baseY, height, px, color1, color2, density = 0.6) {
  for (let dy = 0; dy < height; dy++) {
    let spread = round(dy * 0.8);
    for (let dx = -spread; dx <= spread; dx++) {
      // 边缘强制保留（维持扇形轮廓），内部按 density 剔除
      if (abs(dx) !== spread && random() > density) continue;
      fill(random() > 0.5 ? color1 : color2);
      rect(baseX + dx * px, baseY - dy * px, px, px);
    }
  }
}
```

**组合原则：** 一次场景中至少使用两种模型（如 A+C 做水草+珊瑚礁，B+D 做灌木+扇形花卉）。每种模型用独立调色板，产生色彩层次。

---

## 赛博生命体状态机（AI FSM）

不论是养鱼、养猫、养史莱姆还是电子盆栽，通用以下状态结构：

```javascript
// 状态枚举
const STATE = { WANDER: 'wander', CHASE: 'chase', FLEE: 'flee' };

function updateCreature(c) {
  // 状态转换逻辑
  if (c.state === STATE.FLEE) {
    c.fleeTimer--;
    if (c.fleeTimer <= 0) c.state = STATE.WANDER;
  } else if (targetNearby(c)) {
    c.state = STATE.CHASE;
    if (reachedTarget(c)) { c.state = STATE.WANDER; c.reaction = 30; }
  } else {
    c.state = STATE.WANDER;
  }

  // Wander: 使用 noise() 产生不可预测的平滑探索运动
  if (c.state === STATE.WANDER) {
    c.vx += (noise(c.x * 0.01, frameCount * 0.005) - 0.5) * 0.1;
    c.vy += (noise(c.y * 0.01, frameCount * 0.005 + 100) - 0.5) * 0.1;
  }
  // Chase: atan2 角度 + 固定加速度靠近目标
  else if (c.state === STATE.CHASE) {
    let angle = atan2(c.targetY - c.y, c.targetX - c.x);
    c.vx += cos(angle) * 0.12; c.vy += sin(angle) * 0.12;
  }
  // Flee: 远离触发源，摩擦力衰减
  else if (c.state === STATE.FLEE) {
    c.vx *= 0.92; c.vy *= 0.92;
  }

  // 速度钳制（不同状态不同上限）
  let limit = c.state === STATE.FLEE ? 8 : (c.state === STATE.CHASE ? 3 : 1.5);
  let spd = sqrt(c.vx * c.vx + c.vy * c.vy);
  if (spd > limit) { c.vx = (c.vx / spd) * limit; c.vy = (c.vy / spd) * limit; }

  c.x += c.vx; c.y += c.vy;

  // reaction 衰减 — 吃到东西/被摸时短暂播放反馈动画
  if (c.reaction > 0) c.reaction--;
}
```

**状态切换规则（通用）：**
- `WANDER → CHASE`：目标（食物/鼠标/同伴）进入检测半径
- `CHASE → WANDER`：到达目标（距离 < 阈值）或超时
- `任意 → FLEE`：外部事件触发（敲玻璃/点击惊吓），持续 N 帧后自动回到 WANDER

---

## 防坑铁律 + 标准交互模板

### 1. 像素渲染与丝滑运动的终极公式

- **物体坐标 (`f.x`, `f.y`)**：保持**浮点数**（如 `10.453`），速度累加才不卡顿。
- **绘制原点 (`translate`)**：包裹 `round()`（如 `translate(round(f.x), round(f.y))`），像素边缘绝对锐利。

```javascript
// ✅ 正确
c.x += c.vx; c.y += c.vy;      // 浮点运动
translate(round(c.x), round(c.y)); // 仅绘制时对齐

// ❌ 错误：直接 snap 坐标 → 一格一格跳跃
c.x = floor(c.x / PX) * PX;
```

### 2. 单击/双击分离模板（直接复制使用）

放弃 p5.js 内置事件（`mousePressed` + `doubleClicked` 必然冲突）。使用原生 DOM `pointerdown` + 时间差判断：

```javascript
let lastTapTime = 0, tapTimeout;
document.getElementById('interact-layer').addEventListener('pointerdown', (e) => {
  let now = Date.now();
  if (now - lastTapTime < 300) {
    clearTimeout(tapTimeout);
    onDoubleTap(e.clientX, e.clientY); // 双击
    lastTapTime = 0;
  } else {
    lastTapTime = now;
    tapTimeout = setTimeout(() => { onSingleTap(e.clientX, e.clientY); }, 300); // 单击
  }
});
```

### 3. 敲击涟漪 CSS（直接复制使用）

```css
.knock-ripple {
  position: fixed; z-index: 6; pointer-events: none;
  border-radius: 50%; border: 3px solid rgba(255,255,255,0.9);
  background: radial-gradient(circle, rgba(255,255,255,0.5) 0%, transparent 60%);
  animation: ripple 0.8s cubic-bezier(0.1, 0.8, 0.3, 1) forwards;
  transform: translate(-50%, -50%);
}
@keyframes ripple {
  0%   { width: 0; height: 0; opacity: 1; border-width: 8px; }
  100% { width: 250px; height: 250px; opacity: 0; border-width: 1px; }
}
```

---

## 颜色配方

### Frutiger Aero 天空/水色

> 天空和水面渐变色见 `assets/palettes.json` 的 `sky_gradient` 数组——用于 Canvas 内 `fill()` 逐像素填充，与 CSS 层的 `base_gradient` 配合使用。

### 调色板

> 调色板从 `assets/palettes.json` 选取——6 套命名色板（Aqua Glass / Botanical Dew / Sunlit Meadow / Coral Reef / Lavender Mist / Cyber Mint），按 scene 匹配。禁止对单个物体独立 random RGB。

---

## 质量自检清单

> **Assume there are problems. Your job is to find them.** 如果初查找到 0 个问题——你看得不够仔细。交付前运行 `python3 scripts/validate.py <output.html>` 做自动检测，然后逐条确认：

交付前逐条确认：

**🔴 架构（致命 — 不通过则页面必然异常）：**

**五大铁律自检（`design-principles.md §二十` — 生成后强制执行）：**
- [ ] **铁律 1**：搜索 `backdrop-filter` → 仅出现在 `.glass-bg`（z=2）？z≥3 的元素禁止
- [ ] **铁律 2**：若场景含玻璃容器 → `ctx.clip()` 存在？`globalCompositeOperation = 'screen'` 在高光中出现？
- [ ] **铁律 3**：逐条对照 Prompt 动词与履约表 → 每个动词都有对应的技术实现？
- [ ] **铁律 4**：无 `rgba(0,0,0` 纯黑阴影？无 `#FF0000` 高饱和原色？无扁平无渐变色块？
- [ ] **铁律 5**：`draw()` 内的 `random(` 调用次数 ≤ 2（音效/一次性粒子）？

**Wrapper + CSS 层：**
- [ ] 存在 `#pixel-stage` wrapper，所有玻璃层 + canvas + 交互层在其内部
- [ ] 所有层（`.ambient-light` / `.glass-bg` / `.glass-shell` / `#interact-layer`）使用 `position: absolute`（非 `fixed`），`%` 单位相对于 wrapper
- [ ] Canvas 通过 `c.parent('pixel-stage')` 挂入 wrapper，CSS `width:100%; height:100%` 填满
- [ ] `#pixel-stage` 有 `overflow: hidden`（裁剪溢出的玻璃效果）
- [ ] `backdrop-filter: blur()` **仅**存在于 `.glass-bg`（z=2，canvas 之下）——外壳层 `.glass-shell`（z=4）绝对禁止 blur
- [ ] 固定画布：`windowResized()` 只调 `sizeStage()`，不改 canvas 分辨率；全视口：`resizeCanvas(windowWidth, windowHeight)` + `pixelDensity(1)`

**🔴 Canvas 玻璃容器（若场景含玻璃瓶/水族箱/玻璃罩）：**
- [ ] 玻璃容器 100% 在 Canvas 内通过 `drawAeroGlassBottle()` 绘制 — 禁止用 CSS `backdrop-filter` / `border-radius` 模拟容器形状
- [ ] 瓶内物体包裹在 `ctx.save()` → `defineBottlePath()` → `ctx.clip()` → `[内容]` → `ctx.restore()` 闭包中
- [ ] 玻璃高光包含三项：曲面带状渐变（`globalCompositeOperation = 'screen'`）+ 瓶口反射环 + 菲涅尔边缘描边
- [ ] 高光路径使用 `bezierCurveTo()` / `quadraticCurveTo()` 跟随瓶身曲面 — 非 `rect()` 或 `circle()` 替代
- [ ] 瓶底有沉淀厚度渐变（`createLinearGradient` 径向椭圆，模拟厚玻璃底）
- [ ] 软木塞有 3D 圆柱渐变（4-5 段 stop：阴→高光脊→固有色→反光→阴）+ 竖向纹理线

**🟡 渲染：**
- [ ] 全视口：`pixelDensity(1)` + `noSmooth()`，`windowResized` 中重设。固定画布：`noSmooth()` + `image-rendering: pixelated`
- [ ] `clear()` 而非 `background()`，CSS 背景透出
- [ ] Canvas 有 CSS `filter: drop-shadow()` 产生景深感
- [ ] 运动浮点计算 + `translate(round())` 对齐，不对坐标做 grid snap
- [ ] 气泡使用 `circle()` + 偏移高光，禁止 `rect()` 气泡

**🟢 交互：**
- [ ] 交互使用自定义 `pointerdown` + 300ms 时间差，非 p5 内置事件
- [ ] 移动端：`user-scalable=no`，`touch-action: none`
- [ ] 主体角色有状态机（≥ 3 个状态：wander / chase / flee）
- [ ] 主体角色有动画反馈（尾巴摆动/爱心/缩放/颜色变化等）

**🔵 视觉：**
- [ ] 环境 ≥ 2 种形态装饰元素（至少使用 2 种程序化生成模型）
- [ ] 颜色来自预设调色板数组，非每个物体独立随机 RGB
- [ ] 字体栈使用 Frutiger Aero 栈（`"Segoe UI","Frutiger","Trebuchet MS","PingFang SC",sans-serif`）
- [ ] 文字带发光白边（`text-shadow:0 1px 2px rgba(255,255,255,.8)`）
- [ ] 无纯黑字体（统一深海蓝 `#1a4a5e` 或半透明白 `rgba(255,255,255,.85)`）
- [ ] 操作提示：底部一行 12px / letter-spacing 3px / 半透明，不抢主视觉
