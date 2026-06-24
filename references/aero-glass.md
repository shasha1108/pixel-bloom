# Frutiger Aero 高级技法 — 从 Demo 到艺术品

> 覆盖四个决定作品是"小游戏"还是"赛博艺术品"的核心维度。

## 一、真半球穹顶

**反模式：** `border-radius` 捏造不规则的椭圆或鸭蛋形。

**正解：** 玻璃罩顶部必须是纯数学的半球体。

### 半球穹顶 + 圆柱体架构

**致命陷阱：** `border-radius: 50%` 在宽高不等的元素上，X 半径用宽度的一半、Y 半径用高度的一半，必然产生椭圆。宽 72% 高 52% 的元素 → 上半圆 X=36% Y=26% → 鸭蛋形。

**正解：** 拆分为 `.dome-top`（正方形，高=宽/2）+ `.dome-wall`（直壁）。

```css
/* 穹顶：正方形截半 → 完美正半圆 */
.dome-top {
  width: 72%; height: 36%;         /* height = width/2 ← 关键 */
  border-radius: 999px 999px 0 0;  /* 正方形上 999px = 完美半圆 */
  border: 2.5px solid rgba(255,255,255,.85);
  border-bottom: none;
  box-shadow: inset 0 0 40px rgba(255,255,255,.45),
              inset -8px 0 20px rgba(255,255,255,.15);
}
/* 直圆柱壁 */
.dome-wall {
  top: 46%; left: 14%; width: 72%; height: 24%;
  border-left: 2.5px solid rgba(255,255,255,.7);
  border-right: 2.5px solid rgba(255,255,255,.7);
  border-bottom: 2px solid rgba(255,255,255,.4);
}
```

**三条铁律：**
- 穹顶 `height` 必须恰好等于 `width / 2`，缺一像素都不行
- 必须有木质/金属底座托住生态——无底座=漂浮感
- 玻璃内侧必须有白色 `inset` 内发光（厚度感的唯一来源）

---

## 二、纯正像素呼吸

**反模式：** 用 `scale(pulse)` 缩放像素——像素块变长方形，边缘发虚。

**正解：** 像素的呼吸通过**外围像素块的整数 PX 平移**实现。

```javascript
// 标记边缘块
for (let dy = -radius; dy <= radius; dy++) {
  let lim = round(sqrt(radius * radius - dy * dy));
  for (let dx = -lim; dx <= lim; dx++) {
    let isEdge = abs(dx) >= lim - 1 || abs(dy) >= radius - 1;
    blocks.push({ dx, dy, edge: isEdge, ... });
  }
}

// 呼吸：边缘块沿径向平移 1PX
for (let b of blocks) {
  let offX = 0, offY = 0;
  if (b.edge && breath !== 0) {
    let ang = atan2(b.dy, b.dx);
    offX = round(cos(ang)) * breath * PX;
    offY = round(sin(ang)) * breath * PX;
  }
  rect(b.dx * PX + offX, b.dy * PX + offY, PX, PX);
}
```

**关键：** `offX` 和 `offY` 必须是 `PX` 的整数倍，像素永远对齐网格。

### 备选：颜色明暗呼吸

适合蘑菇伞、荧光体等不适合平移的场景——改变 `fill()` 的 RGB 值而非位置：
```javascript
let glowAmp = sin(frame * 0.03 + phase) * 0.25 + 0.75;
fill(red(col) * glowAmp, green(col) * glowAmp, blue(col) * glowAmp);
```

---

## 三、光学透镜水珠

**反模式：** CSS `radial-gradient` 白圆——像贴纸，不像水。

**正解：** 利用 `backdrop-filter` 制造光学透镜效应。

```css
.lens-drop {
  background: rgba(255,255,255,.08);
  backdrop-filter: brightness(1.2) contrast(1.3);
  box-shadow:
    inset -2px -2px 6px rgba(255,255,255,.4),  /* 底部内高光 */
    inset 2px 2px 4px rgba(0,0,0,.1),           /* 顶部内阴影 */
    0 2px 6px rgba(0,0,0,.15);                  /* 外投影 */
  border: 1px solid rgba(255,255,255,.4);
}
```

**效果：** 水珠滑过玻璃时，背后的植物会被 `brightness(1.2)` 提亮、`contrast(1.3)` 增强对比——像真正的凸透镜折射。

---

## 四、Perlin 漩涡孢子

**反模式：** 粒子加重力——像弹力球在地上弹跳。

**正解：** 零重力 + 2D Perlin Noise 向量场 + `blendMode(SCREEN)` 荧光叠加。

```javascript
// 每帧更新
let angle = noise(spore.x * 0.003, spore.y * 0.003, frame * 0.008) * TWO_PI * 2;
spore.vx += (cos(angle) * 0.06 - spore.vx) * 0.08;
spore.vy += (sin(angle) * 0.06 - spore.vy) * 0.08;
spore.x += spore.vx; spore.y += spore.vy;
// 无重力项！粒子靠 Perlin 向量场自然形成旋涡

// 渲染：SCREEN 混合实现荧光重叠
push(); blendMode(SCREEN);
for (let s of spores) {
  fill(180, 240, 200, alpha);
  circle(s.x, s.y, size);
  // 高光点
  fill(255, 255, 220, alpha * 0.5);
  circle(s.x - size * 0.15, s.y - size * 0.15, size * 0.3);
}
pop();
```

**为什么是 `noise(x*0.003, y*0.003, frame*0.008)`：**
- `0.003` → 空间频率低，粒子间运动协调（不会各自乱飞）
- `frame*0.008` → 时间频率低，漩涡缓慢演化
- `* TWO_PI * 2` → 映射到 0~4π，产生完整的旋涡方向

**叠加作用：** `blendMode(SCREEN)` 使重叠区域颜色相加超过 255，产生刺眼的荧光白色——这才是"发光孢子"的视觉核心。

---

## 质量自检

交付前确认：

- [ ] 玻璃罩为真半球 `border-radius: 50% 50% 0 0`，有底座
- [ ] 无 `scale()` 用于像素物体——呼吸用边缘位移或颜色明暗
- [ ] 水珠有 `backdrop-filter` 透镜效应，非纯渐变圆
- [ ] 粒子无重力，用 Perlin Noise 驱动，`blendMode(SCREEN)` 渲染
