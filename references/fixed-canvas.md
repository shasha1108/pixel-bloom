# 固定画布架构 — 像素艺术的唯一正确做法

> 像素艺术需要固定网格。响应式缩放是像素的敌人。

## 核心铁律

**像素画布必须是固定像素尺寸。** 用 CSS `transform: scale()` 适配屏幕，不用百分比 `width/height`。

```javascript
const CW = 320, CH = 480; // 固定画布尺寸
function setup() {
  createCanvas(CW, CH);   // 永远不传 windowWidth/windowHeight
  noSmooth();             // 固定画布上 noSmooth() 单独生效，不需要 pixelDensity(1)
}
```

**为什么不用 `pixelDensity(1)`：** 固定画布上 `noSmooth()` 已足够保持锐利。多设 `pixelDensity(1)` 在高 DPI 屏反而可能触发 sub-pixel 渲染导致发虚。

## Z-index 用 CSS 优于 JS

固定画布场景下，CSS `!important` 比 JS `.style()` 更可靠——p5.js 会覆盖 JS 设置的 style。

```css
canvas {
  position: absolute !important;
  z-index: 7 !important;
  pointer-events: none;
}
```

## 三层分离架构

```
背景层 (fixed, 填满视口)          → 极光、渐变
  ↓
毛玻璃底板 (absolute, z:6, blur)  → 仅模糊背景，不模糊像素
  ↓
Canvas 像素层 (absolute, z:7)     → 绝对锐利，drop-shadow 景深
  ↓
玻璃外壳 (absolute, z:8, 无blur)  → 纯透明边框 + 内发光高光
  ↓
底座 (absolute, z:9)              → 3段渐变 + 强投影 = 重量感
```

**致命错误：** 玻璃壳加 `backdrop-filter: blur()` → 像素层被模糊。
**正确：** blur 只在底板层，玻璃壳零模糊。

## 容器尺寸与穹顶数学

固定容器让 `border-radius` 计算变成精确数学题：

```css
.jar-container { width: 320px; height: 480px; }  /* 固定尺寸 */
.bell-glass {
  left: 10px; right: 10px;    /* 玻璃宽 = 300px */
  border-radius: 150px 150px 0 0;  /* 150 = 300/2 → 完美半圆 */
}
```

**原则：** 固定容器宽度 → 穹顶 `border-radius` = 玻璃宽度的一半 → 永远正半圆，不需要百分比 hack。

## 岛屿用数学公式，不用噪声

```javascript
// ✅ 椭圆公式：精确可控
let r = 130;
for (let dy = 0; dy > -80; dy -= PX) {
  let limit = round(sqrt(1 - pow(dy/80, 2)) * r);
  for (let dx = -limit; dx <= limit; dx += PX) { /* ... */ }
}

// ❌ 噪声：不可预测，容易丑陋
let h = noise(x * 0.05) * 40;
```

**原则：** 地形用数学曲线（椭圆、正弦、抛物线），装饰细节用噪声。

## Perlin 粒子的正确配方

```javascript
// 每帧更新
let angle = noise(s.x * 0.01, s.y * 0.01, frameCount * 0.02) * TWO_PI * 2;
s.vx += cos(angle) * 0.1;
s.vy += sin(angle) * 0.1;
s.vx *= 0.95;  // 阻尼：自然减速
s.vy *= 0.95;
s.vy -= 0.02;  // 微重力：缓慢下沉

// 双圈发光渲染
blendMode(SCREEN);
fill(100, 200, 255, alpha * 0.3); circle(x, y, PX * 4);   // 外层光晕
fill(255, 255, 255, alpha);       circle(x, y, PX * 1.5); // 内层亮点
```

**三个关键参数：**
- `noise 空间频率 0.01` — 粒子间运动协调，不会各自乱飞
- `vx *= 0.95` — 阻尼让运动像流体而非弹球
- `vy -= 0.02` — 极微弱重力产生缓慢下沉，不是硬弹跳

## 像素呼吸：方向符号推

```javascript
// ✅ 方向符号推：像素永远对齐 PX 网格
if (breathe > 0.5) {
  ox = (b.dx > 0 ? 1 : -1) * PX;  // 沿块自身方向外推 1 格
  oy = (b.dy > 0 ? 1 : -1) * PX;
}

// ✅ 蘑菇发光：颜色明暗交替（不推位置）
if (b.isGlow) {
  let a = map(breathe, -1, 1, 150, 255);
  col = color(red(c), green(c), blue(c), a);
}

// ❌ scale() 或浮点偏移 → 像素发虚
```

## 水珠：玻璃 DOM 元素的子节点

```javascript
let dome = document.getElementById('glassDome');
let drop = document.createElement('div');
drop.className = 'water-drop';
drop.style.left = random(10, domeWidth - 20) + 'px';
dome.appendChild(drop); // ← 关键：挂载到玻璃元素内
```

**原因：** 水珠在玻璃内滑动 → 它应该是玻璃 DOM 的子元素，CSS 定位相对于玻璃左上角，天然限于玻璃范围。

## 底座质感

```css
.bell-base {
  background: linear-gradient(180deg, #cbdce0 0%, #8baeb8 40%, #567e8a 100%);
  border-radius: 50% / 15px;                        /* 椭圆弧边 */
  box-shadow: 0 15px 30px rgba(0,50,70,.5),         /* 厚重外投影 */
              inset 0 2px 5px rgba(255,255,255,.9); /* 顶部高光线 */
}
```

**三段渐变含义：** 亮面(顶) → 固有色(中) → 暗面(底)，模拟圆柱体光照。
