# 像素海洋/水面 — Canvas2D 波浪生成

> 数学思想源自 OceanThreejs 的 Gerstner 波 + Jacobian 泡沫，适配到 pixel-bloom 的 Canvas2D 像素渲染。**不用 shader、不用 WebGL、不用 FFT——一切在像素坐标中计算。**
>
> 核心原则继承 OceanThreejs：**泡沫从波浪曲率派生，不是独立叠加。深度从远近色差体现，Fresnel 用视角近似。**
>
> **加载时机**：场景类型为"像素养鱼"或"像素风景"且含水面（海/湖/河/池塘/水族箱水面）时，STEP 2 像素拆解阶段必读。不覆盖"水下"（那是水体内部的蓝色衰减——见 `generation-workflow.md` 像素养鱼 L0→L2 的深度氛围）。
>
> **触发条件**：用户描述含 海/浪/湖面/池塘/水族箱水面/海滩/涟漪。

---

## 一、像素波浪线算法

### 1.1 原则

**不是一条正弦线。是 3~5 条不同频率/振幅/速度的正弦叠加，加 choppiness 水平偏移使波峰尖锐。**

painter's algorithm：从远到近画每一条波浪线（远浪 = 低振幅/高频率/浅色，近浪 = 高振幅/低频率/深色）。近浪覆盖远浪——自然产生深度。

### 1.2 波浪参数定义

```javascript
// 像素海浪——5 层波浪叠加（从远到近）
const PIXEL_WAVES = {
  // 远浪（地平线附近——小、快、浅色）
  far: [
    { amp: 1.5, freq: 0.06, speed: 2.5, phase: 0.0 },
    { amp: 1.0, freq: 0.08, speed: 3.0, phase: 1.2 },
  ],
  // 中浪
  mid: [
    { amp: 2.5, freq: 0.04, speed: 1.8, phase: 0.5 },
    { amp: 2.0, freq: 0.05, speed: 2.2, phase: 2.0 },
  ],
  // 近浪（前景——大、慢、深色）
  near: [
    { amp: 4.0, freq: 0.025, speed: 1.2, phase: 0.0 },
  ],
};

// choppiness 参数——全局控制波峰尖锐度
// 0 = 纯正弦(塑料水), 0.3 = 自然浪, 0.7 = 风暴尖峰
let choppiness = 0.3;
```

### 1.3 单条波浪线的像素绘制

```javascript
/**
 * 画一条像素波浪线——Gerstner 的 Canvas2D 等价
 * @param {number} baseY - 波浪基线 Y（水平面）
 * @param {object} wave - { amp, freq, speed, phase }
 * @param {number} choppiness - 0~0.7，波峰水平偏移量
 * @param {number} time - 全局时间
 * @param {string} color - 波浪线颜色
 * @param {number} px - 像素单位
 */
function drawWaveLine(baseY, wave, choppiness, time, color, px) {
  const CW = width;   // 画布宽度
  const CH = height;  // 画布高度

  fill(color);
  noStroke();

  // 沿 X 轴逐像素绘制
  for (let x = 0; x < CW; x += px) {
    // 相位
    const theta = wave.freq * x + wave.speed * time + wave.phase;

    // 垂直位移（sin 分量）
    const dy = wave.amp * Math.sin(theta);

    // choppiness 水平偏移——波峰处 (cos>0) 像素向右聚集
    // Gerstner: x' = x - Q*A*cos(θ)*dirX
    // Canvas2D: 通过调整像素间距模拟
    const cosT = Math.cos(theta);
    const chopOffset = choppiness * wave.amp * cosT;

    // 实际绘制位置
    const drawX = x + chopOffset;
    const drawY = baseY + dy;

    // 像素块
    rect(round(drawX), round(drawY), px, px);
  }
}
```

**choppiness 的关键作用**：当 `cosT > 0`（波峰右侧），`chopOffset` 为正 → 像素向右移动 → 波峰处像素聚集（更密/更亮）。当 `cosT < 0`（波谷），像素向左散开 → 波谷处像素稀疏 → 露出更深的底色。**这就是像素版的波峰尖锐化。**

### 1.4 多层波浪叠加绘制

```javascript
/**
 * 画整个海面——远浪到近浪逐层绘制
 * @param {number} horizonY - 地平线 Y 坐标
 * @param {number} shoreY - 沙滩线 Y 坐标
 * @param {number} time - 全局时间
 * @param {number} px - 像素单位
 */
function drawOceanSurface(horizonY, shoreY, time, px) {
  const oceanHeight = shoreY - horizonY;

  // 1. 远浪——小、快、浅色（接近天空色）
  const farBaseY = horizonY + oceanHeight * 0.25;
  const farColor = color(160, 190, 210);  // 浅蓝灰——接近天空
  for (const w of PIXEL_WAVES.far) {
    drawWaveLine(farBaseY, w, choppiness * 0.4, time * 0.7, farColor, px);
  }

  // 2. 中浪——中等振幅、中等速度
  const midBaseY = horizonY + oceanHeight * 0.55;
  const midColor = color(70, 130, 170);  // 中蓝
  for (const w of PIXEL_WAVES.mid) {
    drawWaveLine(midBaseY, w, choppiness * 0.7, time * 0.85, midColor, px);
  }

  // 3. 近浪——大、慢、深色
  const nearBaseY = horizonY + oceanHeight * 0.8;
  const nearColor = color(30, 80, 130);  // 深蓝绿
  for (const w of PIXEL_WAVES.near) {
    drawWaveLine(nearBaseY, w, choppiness, time, nearColor, px);
  }
}
```

**深度效果原理**：远浪先画→近浪后画（覆盖在远浪上）+ 远浪颜色更浅更接近天空（大气透视）+ 近浪振幅更大（透视缩放）。三层叠加 = 免费的海面纵深。

---

## 二、像素泡沫

### 2.1 波峰曲率检测

泡沫不在每个波峰出现——只在最尖锐的波峰。判断标准：**波浪曲线的二阶导数（曲率）在波峰处为正且超过阈值 → 泡沫。**

```javascript
/**
 * 在波浪线上检测波峰并绘制泡沫像素
 * @param {number} baseY - 波浪基线
 * @param {object} wave - 波参数
 * @param {number} time - 全局时间
 * @param {number} px - 像素单位
 * @param {number} foamThreshold - 曲率阈值（0~1，越高越难触发泡沫）
 */
function drawWaveFoam(baseY, wave, time, px, foamThreshold) {
  const CW = width;
  fill(255);  // 泡沫始终是白色

  for (let x = 0; x < CW; x += px) {
    const theta = wave.freq * x + wave.speed * time + wave.phase;
    const sinT = Math.sin(theta);
    const cosT = Math.cos(theta);

    // 一阶导数（斜率）
    const dy1 = wave.amp * wave.freq * cosT;

    // 二阶导数（曲率）——波峰处 = 负最大值（向下弯曲）
    const dy2 = -wave.amp * wave.freq * wave.freq * sinT;

    // 泡沫条件：波峰（sinT > 0.7 即接近峰顶）+ 曲率足够（|dy2| > threshold）
    const peakSharpness = Math.abs(dy2);
    if (sinT > 0.7 && peakSharpness > foamThreshold) {
      // 泡沫像素：沿波峰分布——x 方向散布
      const foamSpread = px * 2;  // 泡沫宽度
      const dy = wave.amp * sinT;
      const chopOffset = choppiness * wave.amp * cosT;
      const fx = x + chopOffset;
      const fy = baseY + dy;

      // 泡沫不是实线——是随机散布在波峰周围的白色像素
      for (let fx2 = fx - foamSpread; fx2 <= fx + foamSpread; fx2 += px) {
        // 概率密度：越靠近波峰中心，泡沫概率越高
        const distFromPeak = Math.abs(fx2 - fx) / foamSpread;
        if (Math.random() < 1.0 - distFromPeak * 0.7) {
          // 微小垂直偏移——泡沫漂浮在水面
          const foamY = fy + (Math.random() - 0.5) * px * 2;
          rect(round(fx2), round(foamY), px, px);
        }
      }
    }
  }
}
```

**泡沫参数映射（calm / 概念种子 → foamThreshold）**：

| 场景情绪 | foamThreshold | 效果 |
|---------|---------------|------|
| 风暴（愤怒/焦虑） | 0.02 | 几乎所有波峰都产生泡沫——白浪滔天 |
| 微风（平静） | 0.15 | 只有大浪尖有少量泡沫 |
| 平静如镜（治愈） | 0.50 | 几乎无泡沫 |

---

## 三、水面渐变与深度

### 3.1 远近色差

像素水面从地平线（远）到海岸线（近）的颜色渐变——这是 **Fresnel 的像素等价**。

| 位置 | 原色 | R | G | B | 视觉感受 |
|------|------|---|---|---|---------|
| 地平线（远） | 天空反射色 | 180 | 200 | 220 | 浅灰蓝——反射天空 |
| 中远 | 浅水色 | 100 | 160 | 200 | 蓝——开始看透水面 |
| 中近 | 深水色 | 50 | 110 | 170 | 深蓝绿——看入水体 |
| 近岸（近） | 最深色 | 25 | 70 | 130 | 暗蓝——最深 |

### 3.2 水面底色填充

波浪线之间的空隙需要填充——这是水面本身的颜色。

```javascript
function drawWaterFill(horizonY, shoreY, px) {
  const steps = Math.floor((shoreY - horizonY) / px);
  for (let i = 0; i < steps; i++) {
    const t = i / steps;  // 0=地平线, 1=海岸
    const r = round(180 - 155 * t * t);     // 平方衰减——近岸更快变深
    const g = round(200 - 130 * t * t);
    const b = round(220 - 90 * t);
    fill(color(r, g, b));
    rect(0, round(horizonY + i * px), width, px);
  }
}
```

**绘制顺序（远→近）**：
1. 天空渐变（最底层）
2. 水面底色填充（覆盖天空的下半部分）
3. 远浪层
4. 中浪层
5. 近浪层
6. 泡沫（画在最上面——白色覆盖一切）

---

## 四、像素涟漪交互

### 4.1 点击扩散衰减涟漪

用户点击水面 → 一圈圆环从点击处向外扩散 → 衰减消失。

```javascript
const ripples = [];  // { x, y, radius, maxRadius, alpha, speed }

function spawnRipple(x, y) {
  ripples.push({
    x: x, y: y,
    radius: 2,
    maxRadius: 60 + Math.random() * 40,  // 随机大小——自然变化
    alpha: 0.7,
    speed: 2.5 + Math.random() * 1.5,
  });
}

function updateRipples(px) {
  for (let i = ripples.length - 1; i >= 0; i--) {
    const r = ripples[i];
    r.radius += r.speed;
    r.alpha *= 0.94;  // 衰减
    if (r.alpha < 0.02 || r.radius > r.maxRadius) {
      ripples.splice(i, 1);
    }
  }
}

function drawRipples(px) {
  noFill();
  for (const r of ripples) {
    // 涟漪颜色——白色半透明
    stroke(255, 255, 255, round(r.alpha * 255));
    strokeWeight(px);
    // 画圆环
    const cx = round(r.x);
    const cy = round(r.y);
    const rad = round(r.radius);
    // 像素圆——用 Bresenham 或简单的八分圆
    drawPixelCircle(cx, cy, rad, px);
  }
}
```

### 4.2 持续的波浪漂移

涟漪不只是瞬态——和现有波浪层叠加。涟漪经过的波浪像素被短期抬高 → 产生"水面上有个扰动正在散开"的效果。

---

## 五、海底焦散光斑

### 5.1 原理

当水面有波浪时，波浪的透镜效应将光线聚焦到海底——形成有机的、网状的光斑网络。平静如镜的水面 → 光直射 → 无光斑。微风水面 → 微弱光斑。中等波浪 → 最漂亮的光网。

**Canvas2D 实现方案**：不逐像素计算 Voronoi（太贵）。每 4px 块采样一次多层 value noise——视觉效果与 Voronoi 光网几乎不可区分。

### 5.2 简化 2D 噪声（适配像素粒度）

```javascript
// 简化 value noise — 比 Voronoi 轻，但叠加多层后视觉效果接近焦散网络
function valueNoise(x, y, seed) {
  // 哈希函数
  function hash(x, y) {
    let h = seed + x * 374761393 + y * 668265263;
    h = (h ^ (h >> 13)) * 1274126177;
    return (h ^ (h >> 16)) / 2147483648 + 0.5; // 0~1
  }

  const ix = Math.floor(x);
  const iy = Math.floor(y);
  const fx = x - ix;
  const fy = y - iy;

  // smoothstep 插值
  const sx = fx * fx * (3 - 2 * fx);
  const sy = fy * fy * (3 - 2 * fy);

  // 四角采样
  const n00 = hash(ix,     iy);
  const n10 = hash(ix + 1, iy);
  const n01 = hash(ix,     iy + 1);
  const n11 = hash(ix + 1, iy + 1);

  // 双线性插值
  const nx0 = n00 + (n10 - n00) * sx;
  const nx1 = n01 + (n11 - n01) * sx;
  return nx0 + (nx1 - nx0) * sy;
}
```

### 5.3 三层多尺度叠加（互质 scale + 不同时间偏移）

```javascript
// 三层焦散——时间偏移 + 方向偏移 + 互质缩放消除视觉重复
function sampleCaustics(worldX, worldY, time, px) {
  // scale 单位：噪声频率（越小 = 越大的光斑）
  // 互质因子 0.03 / 0.05 / 0.12 ——消除视觉重复周期
  const SCALES = [0.03, 0.05, 0.12];

  // 每层有不同的时间偏移速度 + 方向
  // 慢速、不同方向 → 层与层之间缓慢滑动 → 有机干涉
  const SPEEDS = [
    { dx: 0.3,  dy: 0.15, t: 0.8  },
    { dx: -0.2, dy: 0.25, t: 0.55 },
    { dx: 0.1,  dy: -0.3, t: 0.35 },
  ];

  let caustics = 0;

  for (let i = 0; i < 3; i++) {
    const s = SCALES[i];
    const sp = SPEEDS[i];

    // 时间驱动的位置偏移——不同层向不同方向漂移
    const ox = sp.dx * time;
    const oy = sp.dy * time;

    // 噪声采样
    const n = valueNoise(
      worldX * s + ox,
      worldY * s + oy,
      42 + i * 137  // 每层独立 seed
    );

    caustics += n;
  }

  // 归一化到 0~1
  caustics /= 3.0;

  // 对比度曲线：pow(c, 3.0) * 2.5 → 压制暗区、增强亮纹
  // 只有当两层或三层的亮区重叠时，pow 才会把它们推上可见阈值
  caustics = Math.pow(caustics, 3.0) * 2.5;
  caustics = Math.min(caustics, 1.0);

  return caustics;
}
```

### 5.4 海底绘制（含焦散叠加）

```javascript
function drawSeafloorWithCaustics(seafloorY, horizonY, time, px, choppiness) {
  const CW = width;
  const CH = height;

  noStroke();

  // 焦散强度受 choppiness 控制
  // 水面越平静 → 透镜效应越弱 → 焦散越淡
  // choppiness 0 = 镜面 → 0, choppiness 0.3 = 正常 → 1.0, choppiness 0.7 = 风暴 → 0.6 (太乱反而弱)
  const causticIntensity = choppiness < 0.01 ? 0 :
    choppiness < 0.3 ? choppiness / 0.3 :
    1.0 - (choppiness - 0.3) * 0.5;  // choppiness 0.7 → 0.8

  for (let y = seafloorY; y < CH; y += px) {
    for (let x = 0; x < CW; x += px) {
      // 海底深度——越深越暗
      const depth = (y - seafloorY) / (CH - seafloorY); // 0(近) → 1(深)

      // 海底颜色——沙色逐渐变暗蓝
      const r = round(200 - 150 * depth);
      const g = round(180 - 140 * depth);
      const b = round(140 - 80 * depth);

      // 焦散采样（每 px 块一次，不是每像素）
      const c = sampleCaustics(x, y, time, px);
      const causticBoost = c * causticIntensity;

      // 加亮混合——光只增不减，保留沙地基底色
      // 光斑偏暖（阳光聚焦到沙地上）
      const cr = min(255, r + round(40 * causticBoost));
      const cg = min(255, g + round(50 * causticBoost));
      const cb = min(255, b + round(45 * causticBoost));

      fill(cr, cg, cb);
      rect(x, y, px, px);
    }
  }
}
```

### 5.5 绘制顺序（含焦散）

```
整个场景的 painter's algorithm（远→近）：
1. 天空渐变（最底层）
2. 海底 + 焦散 ← 新增。在水面之下、波浪线之前
3. 水面底色填充（覆盖海底——水面不透明区域）
4. 远浪层
5. 中浪层
6. 近浪层
7. 泡沫（最上层）
8. 涟漪（最最上层——交互覆盖一切）
```

**为什么海底在波浪线之前**：海底是"水下的一部分"——波浪线是水面上的反光/泡沫。如果海底画在波浪线之后 → 海底覆盖了波浪 → 水面不见了。

---

## 六、概念种子偏置

| 场景/概念种子 | 波浪强度 | 水面颜色 | 泡沫 | 涟漪交互 | 焦散光斑 |
|-------------|---------|---------|------|---------|---------|
| **Another Tank**（水族箱） | 极小——amp × 0.15，choppiness = 0 | 蓝绿（水下光衰减） | 无 | 点击产生涟漪——鱼被惊动 | 微弱——choppiness=0 时透镜效应消失，但水族箱顶灯可产生极淡光斑（intensity 0.15） |
| **Windmill Valley**（山谷湖泊） | 小——amp × 0.3，choppiness = 0.1 | 蓝绿+天空反射 | 微风泡沫（threshold 0.2） | 点击产生涟漪 | 轻——choppiness 低导致光斑淡而慢（intensity 0.35，noise speed ×0.6） |
| **Pixel Shore**（海滩·新场景） | 正常——amp × 1.0，choppiness 0.3 | 远浅灰蓝→近深蓝绿 | 正常（threshold 0.08） | 点击 + 拖拽 = 推开波浪 | 最优——choppiness 0.3 = 透镜效应最强 → 清晰的光网在浅滩沙地上舞动 |
| **Storm Sea**（风暴海·愤怒隐喻） | 激——amp × 2.0，choppiness 0.7 | 灰暗蓝 | 狂暴（threshold 0.02） | 长按 = 安抚 → choppiness 降低 | 混乱——choppiness 过高 → 光斑过多过乱 → 焦散强度反而降低（intensity 0.6），且水浑浊 → 海底可见度低 |

---

## 七、反模式

| # | 反模式 | 级别 | 表现 | 修复 |
|---|--------|------|------|------|
| 1 | 单条正弦线 | **致命** | 蓝色正弦线在地平线扭动——示波器 | 至少 3 层不同频率/振幅的波浪叠加 |
| 2 | choppiness = 0 | 警告 | 完美对称正弦——塑料水/果冻 | choppiness ≥ 0.1——波峰像素聚集、波谷稀疏 |
| 3 | 无泡沫 | 警告 | 浪头无白色——油 | 波峰曲率 > 阈值 → 白色像素 |
| 4 | 波浪同一颜色 | 警告 | 所有波浪同一蓝色——无深度 | 远浪浅灰蓝 → 近浪深蓝绿（3 层级联） |
| 5 | 涟漪不衰减 | 警告 | 永动波纹——水面永远在震荡 | `alpha *= 0.94`——5 秒内消失 |
| 6 | 忘记画水面底色 | **致命** | 波浪线之间的空隙露出天空——水面是"线"不是"面" | 波浪线之前先填充水面底色渐变 |
| 7 | 波纹间隔均匀 | 警告 | 一排等距平行线——水渠 | 5 条波的 freq 取互质数（0.025/0.04/0.05/0.06/0.08） |
| 8 | 焦散用 mix 混合 | **致命** | 亮区沙子被洗白——沙底纹理消失 | 始终用加亮：`r + 40*caustics` 而非 `mix(sandR, 255, caustics)` |
| 9 | 焦散三层同 scale | 警告 | 三层层峰重叠 → 光斑呈斑马纹而非有机网络 | 三层 scale 取互质因子（0.03/0.05/0.12）— 与波浪互质同一套哲学 |
| 10 | 镜面水面有焦散 | 警告 | choppiness=0 → 水面是镜子 → 光直射不聚焦 → 但光斑仍在 | 焦散强度 = `choppiness < 0.01 ? 0 : ...` — 镜面水面强制无焦散 |

---

## 八、与 vegetation-system.md 的协作

当场景同时包含树木和水面（如"像素森林里的湖"）：

1. **绘制顺序**：天空 → 远山(vegetation) → 海底+焦散(ocean-pixels) → 远浪(ocean-pixels) → 中浪 → 近树干(vegetation) → 近浪 → 泡沫 → 前景(vegetation)
2. **交互隔离**：点击树干 = 不产生涟漪。点击水面 = 产生涟漪。通过 Y 坐标判断（水面区域 vs 地面区域）
3. **共享风场**（如已实现像素风速场）：波浪 phase 速度 + 树木 sway 频率 + 焦散 noise 漂移方向 = 同一个 `windField(x,y,time)` 驱动

---

## 九、自检清单

- [ ] 水面用了 ≥ 3 层不同频率/振幅的正弦叠加（不是单线）？
- [ ] choppiness > 0（波峰像素聚集、波谷稀疏）？
- [ ] 泡沫从波峰曲率检测产生（不是随机白色像素）？
- [ ] 远浪→近浪颜色有递进（浅灰蓝→深蓝绿）？
- [ ] 水面底色填充在波浪线之前绘制（不露天空）？
- [ ] 涟漪交互有衰减（`alpha *= 0.94`）？
- [ ] 波浪绘制顺序：远→近（painter's algorithm）？
- [ ] 多条波的频率互质（无视觉重复周期）？
- [ ] 焦散在海底/池底绘制（波浪线之前）？
- [ ] 焦散三层 scale 互质（0.03/0.05/0.12）？
- [ ] 焦散使用加亮混合（`r + 40*c`，非 `mix`）？
- [ ] 镜面水面（choppiness=0）焦散强制为 0？

---

## 九、河流模式——Y 轴遍历 + 非线性透视

> §一~§八 覆盖海面/湖泊（开放水面，X 轴遍历 + painter's algorithm）。河流是**带状水体**——从远到近的连续路径，需要不同的遍历方式和透视公式。
>
> **触发条件**：场景含"河流/溪流/运河/水渠"——水体呈带状、从地平线延伸到近景。不触发：海/湖/池塘（→ §一~§八 海面模式）。

### 9.1 核心差异：海面 vs 河流

| 维度 | 海面模式 | 河流模式 |
|------|---------|---------|
| 遍历轴 | X（逐列画波浪线） | Y（逐行算左右边界） |
| 填充方式 | 每条波浪线单独 `rect()` | 单次 `beginShape()`/`endShape()` |
| 透视 | painter's algorithm 远→近覆盖 | `pow(t, 2)` 非线性收窄 |
| 边界 | 海面覆盖整个画布下半 | 河流有明确的左右边界 |

### 9.2 河流边界函数

```javascript
function getRiver(y, horizon) {
  if (y < horizon) return null;               // 地平线以上无河流
  let t = pow((y - horizon) / (CH - horizon), 2.0); // 非线性透视——远近夸张
  let cx = CW * 0.5 + sin(t * PI * 1.2) * CW * 0.15; // S 形蜿蜒中线
  let w = CW * (0.01 + t * 0.5);              // 远端极窄，近端宽
  return { cx, w, left: cx - w/2, right: cx + w/2 };
}
```

**`pow(t, 2)` 的作用**：`t` 是 0→1 的线性深度。平方后近景（t 近 1）几乎不变，远景（t 近 0）被极度压缩 → 河流在远处迅速收窄为一条细线 → 冲击力远超线性 `t`。

**反面教材**：用线性 `t` 替代 `pow(t,2)` → 河流近大远小的透视感消失 → 像"等宽直筒"。

### 9.3 河流填充——单次 `beginShape()`

```javascript
fill(riverColor);
beginShape();
// 左岸——从地平线到画面底部
for (let y = horizon; y <= CH; y += PX * 2) {
  let b = getRiver(y, horizon); if (b) vertex(b.left, y);
}
// 右岸——从底部回到地平线
for (let y = CH; y >= horizon; y -= PX * 2) {
  let b = getRiver(y, horizon); if (b) vertex(b.right, y);
}
endShape(CLOSE);
```

**性能差距**：逐列 `rect()` ~960 次 draw call → 单次 `beginShape()` 1 draw call（~500×）。

### 9.4 河面波纹——水平光带

```javascript
// 水平波纹——随时间从远漂到近
fill(255, 255, 255, 120);
for (let i = 0; i < 6; i++) {
  let t = ((frameCount * 0.002 + i * 0.16) % 1);
  let wy = horizon + t * (CH - horizon);
  let b = getRiver(wy, horizon);
  if (b) {
    let wx = b.cx + sin(frameCount * 0.05 + i) * b.w * 0.2; // 水平偏移
    rect(wx, wy, PX * (2 + t * 8), PX * (1 + t * 2)); // 近处更大更宽
  }
}
```

**为什么是水平光带**：河面波纹是光线在水面的反射——物理上反射光带平行于河岸线。水平绘制比斜向更自然。

### 9.5 稻田/植被的河流避让

```javascript
// 在稻田/草地绘制循环中——跳过河流区域
let r = getRiver(y, horizon);
if (r && abs(x - r.cx) < r.w / 2 + PX * 2) continue; // 留 2px 缓冲区
```

### 9.6 反模式（河流专属）

| # | 反模式 | 级别 | 表现 | 修复 |
|---|--------|------|------|------|
| 1 | X 轴遍历河流 | 警告 | 逐列 rect() 填河 → 性能差且波纹难对齐 | Y 轴遍历 + beginShape |
| 2 | 线性 t 替代 pow(t,2) | 警告 | 河流远近视缺乏冲击力——"直筒" | `pow((y-H)/(CH-H), 2)` |
| 3 | `left/right` 当 Y 坐标用 | **致命** | 河流变成竖条 | `left/right` 是屏幕 X 坐标 |
