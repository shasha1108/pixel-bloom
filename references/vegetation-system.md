# 像素植被系统 — 从"树形符号"到"有生长的有机个体"

> 设计哲学源自 Three.js Awesome Graphics 的 `threejs-procedural-vegetation` 技能（物种表 → 迭代生长 → 分层子节点 → 叶法线 → 三级风）。适配到 pixel-bloom：**不画 3D 环/UV/法线，画像素线段+像素簇。但生长逻辑——物种表、队列迭代、分层出芽、拓扑稳定后生叶、三级风——完全适用。**
>
> 本文件建立在 `code-templates.md` 的四大程序化模型之上（模型 A 堆叠摇摆做树干/分支，模型 B 网格剔除做树冠，模型 D 扇形展开做棕榈/蕨叶）。**不替代那些模型——用生长逻辑去编排它们。**
>
> **加载时机**：STEP 1 场景模式判定为"像素森林"或"像素花园"时，STEP 2-4 必读。
>
> **触发条件**：用户描述含树木/森林/花园/灌木/藤蔓/花草等植被元素。

---

## 一、核心哲学

**树不是"一个棕色长方形 + 一个绿色圆形"。树是"一个生长过程在空间中的化石"。**

像素画中画一棵树和 3D 中生成一棵树的本质区别：3D 生成的是几何体（顶点+面），像素画生成的是像素块的位置。但**生长逻辑是相同的**——从树干开始，逐级分叉，子节点分布在同一层级的不同高度/角度，树冠在分支稳定后统一生成。

**当前反模式**（生成前必读，避免以下所有情况）：

| 反模式 | 像素画表现 | 为什么失败 |
|--------|-----------|-----------|
| 所有树同一种类 | 20 棵完全相同的树 | 这是"树的图标"的复制粘贴，不是森林 |
| 所有分叉在同一高度 | 树干顶部突然分出 3 根一样长的枝 | 真正的树分叉是参差的——有的高有的低 |
| 树冠 = 实心圆 | 绿色实心圆盖在树干上 | 透光的树冠才有深度——需要像素间隙 |
| 风 = 同步摇摆 | 所有树同时向左、同时向右 | 广播体操，不是风吹过树林 |
| 改 random seed 改变物种 | seed=42 是松树，seed=99 是柳树 | seed 应控制同一物种内的个体差异，不是物种身份 |

---

## 二、像素物种表

每棵树分三层：树干 (trunk) / 分支 (branch) / 树冠 (canopy)。每层定义以下参数：

```javascript
// 像素物种表 —— 一个物种 = 一个三层参数对象
const SPECIES = {
  // === 针叶树（松/柏/杉） ===
  conifer: {
    trunk: {
      heightMin: 12, heightMax: 18,    // 树干高度（px 单位，不含树冠）
      radius: 2,                        // 树干粗细（px）
      color1: '#3d2b1f',               // 主色（深褐）
      color2: '#5c3d2e',               // 辅色（交替条纹）
      taper: 0.85,                      // 每段锥度——越往上越细
      sections: 6,                      // 纵向分段数
    },
    branch: {
      levels: 3,                        // 分支层级数（1=仅主干分叉，3=分叉上再分叉）
      childCountMin: 2, childCountMax: 4, // 每层产生的子分支数
      emergenceLo: 0.3, emergenceHi: 0.8, // 子分支在父分支的哪一段出现（0=基部，1=顶端）
      angleMin: 15, angleMax: 35,       // 分叉角度（度）——针叶树角度小，枝条上扬
      twistMin: 0, twistMax: 60,        // 绕父分支的旋转角度（度）
      lengthRatio: 0.65,                // 子分支长度 = 父分支 × 0.65
      radiusRatio: 0.5,                 // 子分支粗细 = 父分支 × 0.5
      gnarliness: 0.15,                 // 扭曲度——0=笔直，0.3=明显弯曲
      sections: 4,                      // 每分支的像素分段数
    },
    canopy: {
      model: 'B',                       // 使用模型 B（网格剔除）——针叶树冠 = 锥形像素簇
      gridW: 12, gridH: 20,             // 网格尺寸（px）
      density: 0.55,                    // 像素保留率——0.55 = 有 45% 间隙（透光）
      colors: ['#1a3a1a', '#2d5a2d', '#3a6b3a', '#4a7a3a'], // 深绿→浅绿
      shape: 'cone',                    // 锥形——上窄下宽
    },
  },

  // === 阔叶树（橡/枫/榆） ===
  broadleaf: {
    trunk: {
      heightMin: 8, heightMax: 14,
      radius: 3,
      color1: '#4a3520', color2: '#6b4c30',
      taper: 0.75,
      sections: 5,
    },
    branch: {
      levels: 2,
      childCountMin: 2, childCountMax: 5,
      emergenceLo: 0.4, emergenceHi: 0.9,
      angleMin: 25, angleMax: 55,       // 阔叶树角度大——枝条横向展开
      twistMin: 0, twistMax: 120,
      lengthRatio: 0.7,
      radiusRatio: 0.55,
      gnarliness: 0.25,                // 阔叶树更扭曲
      sections: 5,
    },
    canopy: {
      model: 'B',                       // 模型 B（网格剔除）——球形/椭球形像素簇
      gridW: 20, gridH: 16,
      density: 0.45,                   // 更低密度——阔叶树冠透光更多
      colors: ['#2d5a1e', '#3d7a2a', '#5a9a3a', '#7aba4a'],
      shape: 'ellipse',                 // 椭圆形——横向延展
    },
  },

  // === 灌木（杜鹃/黄杨/冬青） ===
  shrub: {
    trunk: {
      heightMin: 2, heightMax: 5,       // 灌木几乎无可见主干
      radius: 2,
      color1: '#3d3025', color2: '#5a4530',
      taper: 0.6,
      sections: 3,
    },
    branch: {
      levels: 1,                        // 灌木分支层级少
      childCountMin: 3, childCountMax: 7, // 但分叉多——丛生
      emergenceLo: 0.1, emergenceHi: 0.7,
      angleMin: 30, angleMax: 70,       // 大角度——横向丛生
      twistMin: 0, twistMax: 180,
      lengthRatio: 0.5,
      radiusRatio: 0.7,
      gnarliness: 0.2,
      sections: 3,
    },
    canopy: {
      model: 'C',                       // 模型 C（圆域筛选）——半球形灌木
      radius: 10,
      density: 0.65,                    // 高密度——灌木更密实
      colors: ['#3a5a2a', '#4a7a3a', '#5a8a4a', '#6a9a5a'],
      shape: 'dome',
    },
  },
};
```

**物种表使用规则**：
- 每个物种的每个参数都是**区间**（min/max）——每棵树的实际值在区间内用 `random()` 随机取值 = 物种内的个体差异
- 改 seed 不改物种 → 另一片同物种的树林（个体不同但仍是同一种）
- 改物种不改 seed → 不同种类的树（用同一个随机序列生成）

---

## 三、迭代分支生长（队列驱动）

**核心算法**：用一个队列按层级生长分支，而非递归。递归会丢失预算可见性。

```javascript
/**
 * 从物种表生成一棵树的完整拓扑
 * @param {object} sp - 物种定义（SPECIES.conifer / broadleaf / shrub）
 * @param {number} baseX - 根部 x 坐标
 * @param {number} baseY - 根部 y 坐标
 * @param {function} rng - 确定性随机函数（seeded）
 * @returns {object} 树的完整拓扑 — { trunk, branches: [...] }
 */
function growTree(sp, baseX, baseY, rng) {
  // 1. 树干
  const trunkH = sp.trunk.heightMin + random() * (sp.trunk.heightMax - sp.trunk.heightMin);
  const trunk = {
    x: baseX, y: baseY,
    height: trunkH,
    radius: sp.trunk.radius,
    direction: { x: 0, y: -1 },  // 向上
    level: 0,
    parent: null,
  };

  // 2. 队列驱动分支生长
  const branches = [];
  const queue = [trunk];  // 从树干开始

  while (queue.length > 0) {
    const parent = queue.shift();
    if (parent.level >= sp.branch.levels) continue;  // 到达最大层级

    const childCount = sp.branch.childCountMin +
      Math.floor(random() * (sp.branch.childCountMax - sp.branch.childCountMin + 1));

    for (let i = 0; i < childCount; i++) {
      const child = growBranch(parent, i, childCount, sp, rng);
      branches.push(child);
      queue.push(child);  // 子分支继续生长
    }
  }

  return { trunk, branches };
}

/**
 * 生成单个子分支
 */
function growBranch(parent, childIndex, totalChildren, sp, rng) {
  // 分层纵向槽位——每个子分支在父分支的不同高度出芽
  const emergenceRange = sp.branch.emergenceHi - sp.branch.emergenceLo;
  const slotCenter = sp.branch.emergenceLo +
    (childIndex + 0.5) / totalChildren * emergenceRange;
  // 加微小随机偏移——避免子分支排成完美等距线
  const emergenceT = slotCenter + (random() - 0.5) * emergenceRange / totalChildren * 0.5;

  // 角度置换——每个子分支绕父分支的旋转角度不同
  const baseTwist = (childIndex / totalChildren) * 360;
  const twist = baseTwist + (random() - 0.5) * sp.branch.twistMax;

  // 分叉角度——在物种范围内随机
  const angle = sp.branch.angleMin + random() * (sp.branch.angleMax - sp.branch.angleMin);
  const angleRad = (angle * Math.PI) / 180;

  // 父分支在出芽点的位置
  const parentLen = parent.height;
  const emergeY = parent.y - parentLen * emergenceT;
  const emergeX = parent.x + parent.direction.x * parentLen * emergenceT;

  // 子分支方向——从父分支方向 + 分叉角度 + 扭转
  const parentDir = parent.direction;
  const childDir = {
    x: parentDir.x * Math.cos(angleRad) - parentDir.y * Math.sin(angleRad),
    y: parentDir.x * Math.sin(angleRad) + parentDir.y * Math.cos(angleRad),
  };
  // 应用扭曲扰动
  const gnarl = sp.branch.gnarliness;
  childDir.x += (random() - 0.5) * gnarl * 2;
  childDir.y += (random() - 0.5) * gnarl * 2;
  // 归一化
  const len = Math.sqrt(childDir.x ** 2 + childDir.y ** 2);
  childDir.x /= len;
  childDir.y /= len;

  // 子分支长度与粗细——按比例从父分支继承
  const childLen = parentLen * sp.branch.lengthRatio * (0.85 + random() * 0.3);
  const childRadius = Math.max(1, Math.round(parent.radius * sp.branch.radiusRatio));

  return {
    x: emergeX,
    y: emergeY,
    height: childLen,
    radius: childRadius,
    direction: childDir,
    level: parent.level + 1,
    twist: twist,
    parent: parent,
  };
}
```

**算法保证**：
- 子分支分布在不同高度（分层槽位 `slotCenter` + 随机偏移）→ 不会所有分叉在同一高度
- 子分支绕父分支旋转角度不同（`baseTwist` 按 `childIndex/totalChildren` 分布）→ 不会所有分支在同一方向
- 扭曲度 `gnarliness` 提供自然的非直线性
- 同一物种内每棵树的参数在 min/max 区间内随机 → 个体差异但不改变物种身份

---

## 四、树冠生成（分支拓扑稳定后）

**树冠不能在分支生长过程中同步生成——因为树冠的形态取决于所有分支的最终位置。**

```javascript
/**
 * 在所有分支生长完成后，统一生成树冠
 * @param {object} tree - growTree() 的返回结果
 * @param {object} sp - 物种定义
 * @param {number} px - 像素单位大小
 * @param {function} rng - 确定性随机函数
 */
function generateCanopy(tree, sp, px, rng) {
  const canopy = sp.canopy;
  const pixels = [];

  if (canopy.model === 'B') {
    // 模型 B（网格剔除）—— 针叶树锥形 / 阔叶树球形
    const gridW = canopy.gridW;
    const gridH = canopy.gridH;

    // 树冠中心 = 树干顶端
    const cx = tree.trunk.x;
    const cy = tree.trunk.y - tree.trunk.height;

    for (let gy = 0; gy < gridH; gy++) {
      // 形状函数——决定每行的有效宽度
      let rowW;
      if (canopy.shape === 'cone') {
        rowW = gridW * (1 - gy / gridH);  // 锥形：越往上越窄
      } else if (canopy.shape === 'ellipse') {
        const t = gy / gridH;
        rowW = gridW * Math.sqrt(1 - ((t - 0.5) * 2) ** 2);  // 椭圆形
      } else {
        rowW = gridW;
      }

      for (let gx = -Math.round(rowW); gx <= Math.round(rowW); gx++) {
        // 网格剔除
        if (random() > canopy.density) continue;

        // 颜色从调色板中按高度加权选取
        const t = gy / gridH;
        const ci = Math.floor(t * (canopy.colors.length - 1) + random() * 1.5);
        const color = canopy.colors[Math.min(ci, canopy.colors.length - 1)];

        pixels.push({
          x: cx + gx * px,
          y: cy - gy * px + (canopy.shape === 'cone' ? 0 : gridH * px * 0.3),  // 椭圆下移让树冠重心在树干上方
          color: color,
        });
      }
    }
  } else if (canopy.model === 'C') {
    // 模型 C（圆域筛选）—— 灌木半球形
    const r = canopy.radius;
    for (let dy = 0; dy < r; dy++) {
      const limit = Math.round(Math.sqrt(r * r - dy * dy));
      for (let dx = -limit; dx <= limit; dx++) {
        if (random() > canopy.density) continue;
        const ci = Math.floor((dy / r) * (canopy.colors.length - 1) + random());
        pixels.push({
          x: tree.trunk.x + dx * px,
          y: tree.trunk.y - tree.trunk.height - dy * px,
          color: canopy.colors[Math.min(ci, canopy.colors.length - 1)],
        });
      }
    }
  }

  // 分支末端加像素簇——每根分支终点周围额外分布少量叶子像素
  for (const branch of tree.branches) {
    if (branch.level < tree.trunk.level + 1) continue;  // 最粗的近干分支不加——那是结构枝
    const tipX = branch.x + branch.direction.x * branch.height;
    const tipY = branch.y + branch.direction.y * branch.height;
    const tipCount = Math.floor(3 + random() * 6);
    for (let i = 0; i < tipCount; i++) {
      const angle = random() * Math.PI * 2;
      const dist = random() * 3 * px;
      pixels.push({
        x: Math.round(tipX + Math.cos(angle) * dist),
        y: Math.round(tipY + Math.sin(angle) * dist),
        color: canopy.colors[Math.floor(random() * canopy.colors.length)],
      });
    }
  }

  return pixels;
}
```

**树冠生成规则**：
- 在**所有分支生成完毕后**才调用 `generateCanopy()`——不是每生成一个分支就加叶子
- 树冠密度 `density` < 1 → 像素间隙 = 透光 = 有空气的树冠
- 分支末端像素簇 = 树枝末梢的嫩叶丛——让树冠和树枝有视觉联系
- 颜色从调色板中按高度加权选取——树冠顶部颜色浅（新叶），底部颜色深（老叶）

---

## 五、三级像素风

> **全场景风元素统一数据源**：本节的全局 `WIND` 对象和 `windIntensity()` 是 pixel-bloom 中所有风驱动元素（树/水面波纹/花粉粒子/蝴蝶）的统一采样源。非树木元素从同一个 `WIND` 对象读取 `strength`/`speed`/`angle`，确保"同一阵风"的一致性——详见 `design-principles.md §十七`。

**风不是一棵树的属性——是三种不同尺度的像素偏移，分别作用于叶、枝、干。**

```javascript
/**
 * 三级像素风 —— 每帧计算
 * @param {object} tree - 树的完整拓扑
 * @param {object} canopyPixels - generateCanopy() 的返回结果
 * @param {number} windStrength - 风速（0~1，由外部风场/Perlin 噪声驱动）
 * @param {number} time - 全局时间
 * @param {number} px - 像素单位
 */
function applyWind(tree, canopyPixels, windStrength, time, px) {
  const w = windStrength;

  // === 第一级：叶颤（leaf flutter）—— 树冠像素 ±1px 高频微颤 ===
  const leafFlutterAmp = 1 * w;          // 最大 1px
  const leafFlutterFreq = 12 + w * 8;    // 12-20Hz（感知为"沙沙作响"）
  for (const p of canopyPixels) {
    // 每个像素的相位不同——不是所有叶子同时颤
    p.windOffsetX = Math.round(
      Math.sin(time * leafFlutterFreq + p.x * 0.5 + p.y * 0.3) * leafFlutterAmp
    );
    p.windOffsetY = Math.round(
      Math.cos(time * leafFlutterFreq * 1.3 + p.x * 0.4 + p.y * 0.6) * leafFlutterAmp * 0.5
    );
  }

  // === 第二级：枝摇（branch sway）—— 分支端点 ±3px 低频缓动 ===
  const branchSwayAmp = 3 * w;           // 最大 3px
  const branchSwayFreq = 1.5 + w * 0.5; // 1.5-2.0Hz（可见的慢摇）
  for (const branch of tree.branches) {
    // 分支越远（层级越高）摇摆幅度越大
    const levelMultiplier = 1 + branch.level * 0.6;
    branch.swayOffset = Math.sin(
      time * branchSwayFreq + branch.twist * 0.05
    ) * branchSwayAmp * levelMultiplier;
  }

  // === 第三级：树干摆（trunk sway）—— 整树 x 偏移 ===
  const trunkSwayAmp = 1.5 * w;          // 最大 1.5px
  const trunkSwayFreq = 0.8 + w * 0.3;  // 0.8-1.1Hz（很慢——大树不会快速摇摆）
  tree.trunkSwayOffset = Math.sin(time * trunkSwayFreq) * trunkSwayAmp;
}
```

**三级风的绘制集成**（每帧渲染时）：

```javascript
function drawTree(tree, canopyPixels, sp, px) {
  const tx = tree.trunkSwayOffset || 0;  // 第三级：树干偏移

  // 1. 画树干
  const trunkSegments = sp.trunk.sections;
  for (let i = 0; i < trunkSegments; i++) {
    const t = i / trunkSegments;
    const segY = tree.trunk.y - tree.trunk.height * t;
    const segR = Math.round(tree.trunk.radius * (1 - t * (1 - sp.trunk.taper)));
    // 树干每段在 sway 上叠加自己的缓动
    const segSway = tx * t;  // 树干顶端偏移更大
    const x = Math.round(tree.trunk.x + segSway);
    fill(i % 2 === 0 ? sp.trunk.color1 : sp.trunk.color2);
    rect(x - segR * px, Math.round(segY), segR * 2 * px, px);
  }

  // 2. 画分支
  for (const branch of tree.branches) {
    const bSway = branch.swayOffset || 0;
    const startX = branch.x + tx * (branch.y / tree.trunk.y);  // 继承树干偏移
    const startY = branch.y;
    // 分支方向 + 风偏移
    const endX = startX + branch.direction.x * branch.height + bSway;
    const endY = startY + branch.direction.y * branch.height;

    // 用像素线段画分支（沿方向逐段画）
    const len = Math.sqrt((endX - startX) ** 2 + (endY - startY) ** 2);
    const segs = sp.branch.sections;
    for (let i = 0; i < segs; i++) {
      const t = i / segs;
      const sx = Math.round(startX + (endX - startX) * t);
      const sy = Math.round(startY + (endY - startY) * t);
      const sr = Math.max(1, Math.round(branch.radius * (1 - t * 0.5)));
      fill(i % 2 === 0 ? sp.trunk.color1 : sp.trunk.color2);
      rect(sx - sr * px, sy, sr * 2 * px, px);
    }
  }

  // 3. 画树冠像素（应用第一级叶颤偏移）
  for (const p of canopyPixels) {
    fill(p.color);
    rect(
      Math.round(p.x + (p.windOffsetX || 0) + tx),
      Math.round(p.y + (p.windOffsetY || 0)),
      px, px
    );
  }
}
```

**三级风的关键差异**：

| 级别 | 对象 | 频率 | 振幅 | 视觉感受 |
|------|------|------|------|---------|
| 第一级 | 叶像素 | 12-20Hz | ±1px | "沙沙响"——高频微颤 |
| 第二级 | 分支 | 1.5-2.0Hz | ±3px | "风吹枝摇"——可见的慢摆动 |
| 第三级 | 树干 | 0.8-1.1Hz | ±1.5px | "整树微倾"——几乎不可见但能感觉到 |

**如果三种风用一个 windAngle 做同步摆动 → 塑料假树。** 每级风的频率/振幅/相位独立 → 有机的树。

### 5.1 升级：四组分频率叠加（替换单频 sin）

当前三级风每个级别用单一 `sin(time * freq)` 驱动——这在单棵树时足够，但多棵树时缺乏**空间传播感**（"风以波的形式扫过田野"）。引入四组分频率叠加：

> `hf()` 确定性 hash 函数定义见 `seeded-exploration.md`。

```javascript
/**
 * 四组分风强计算 —— 替代单频 sin，用于所有风级别
 * @param {number} x — 元素世界 X 坐标（决定空间相位）
 * @param {number} elemIdx — 元素索引（决定逐元素相位偏移）
 * @param {number} time — 全局时间
 * @param {object} w — 风参数 { gustScale, speed, turbulence }
 * @returns {number} 归一化风强 0~1（驱动各级振幅）
 */
function windIntensity(x, elemIdx, time, w) {
  const bladePhase = hf(elemIdx) * Math.PI * 2;
  const ampVar = 0.65 + hf(elemIdx + 7) * 0.7;  // 0.65-1.35
  
  // 空间相位：沿 X 轴的投影决定阵风到达时间
  const along = x * w.gustScale;
  const noiseJitter = (noise(x * 0.03, 0) - 0.5) * 2.0;
  
  // 阵风：低频大振幅，以波的形式沿 X 传播
  const gustPhase = along - time * w.speed * 0.6 + noiseJitter * 1.5;
  const gust = Math.pow(Math.sin(gustPhase) * 0.5 + 0.5, 1.6);
  
  // 碎浪：中频中振幅，叠加在阵风上
  const chopPhase = along * 2.7 - time * w.speed * 1.3 + bladePhase;
  const chop = Math.sin(chopPhase) * 0.5 + 0.5;
  
  // 微风地板：永远有轻微的风（逐元素独立）
  const breeze = (Math.sin(time * w.speed * 0.6 + bladePhase) * 0.5 + 0.5) * w.turbulence * 0.4;
  
  return (0.25 + gust * 0.85 + chop * 0.18 + breeze) * ampVar;
}
```

**集成方式**：在 `applyWind()` 中，用 `windIntensity(tree.trunk.x, treeIndex, time, windParams)` 替代裸的 `windStrength`。三级风的频率和振幅不变——但驱动它们的强度现在来自空间传播的四组分风场。

**关键差异**：

| | 旧（单频 sin） | 新（四组分） |
|---|---|---|
| 相邻两棵树 | 相位取决于各自 `twist` 随机值——可能同步也可能反向 | 相位由世界 X 坐标决定——相邻的树自然相近，远处的树错相 |
| 阵风感 | 无——风强均匀 | 有——阵风以波的形式扫过，间歇性强风 |
| 逐树差异 | 仅 `twist` 偏移 | `hf(idx)` 振幅变异 + `hf(idx+7)` 相位偏移 + 空间相位 |

**⚠️ 2D 像素适配注意事项**：
- 圆形弧线弯曲公式（`u = R(1-cos a)`, `dv = R·sin a - dy`）是 3D 的——在 2D 像素画中**只使用水平偏移分量**，忽略垂直下垂（`dv`）。2D 侧视图中"叶片弯曲时的垂直缩短"用 `scaleY` 调整而非 `dv`。
- 颤振 (`flutter`) 的频率在像素画中降低——12-20Hz 在 60fps 显示器上每个像素只偏移 1px，低于 p5.js 的整数像素精度 → 高频颤振在 2D 像素中不可见。**2D 颤振降频到 6-10Hz，振幅提到 ±2px** 才可见。

### 5.2 空间传播：每棵树的相位 = f(世界 X 坐标)

当前多棵树使用各自的 `twist` 值做相位偏移——但 `twist` 是每棵树的独立随机值，相邻两棵树可能完全不同步。

**升级**：每棵树的基础相位由其在场景中的 X 坐标决定：

> `hf()` 确定性 hash 函数定义见 `seeded-exploration.md`。

```javascript
// 替换：tree.trunkSwayOffset = sin(time * freq + tree.twist)
// 为：
function treePhase(tree, time, WIND) {  // WIND 对象定义见 §5.3
  // 基础相位：世界 X 坐标 → 阵风到达时间
  const spatialPhase = tree.trunk.x * WIND.gustScale;
  // 逐树微调：hf(treeIdx) 提供小幅个体差异（不是完全独立）
  const individualShift = hf(tree.index) * 0.3;  // 仅 ±0.15π
  return spatialPhase + individualShift;
}
```

**效果**：
- 相邻的树（X 差 < 10px）→ 相位差 < 0.2π → 几乎同步摇摆 → "它们被同一阵风吹过"
- 远处的树（X 差 > 50px）→ 相位差 > π → 完全异步 → "风以波的形式穿过树林"
- `individualShift` 仅提供 ±15% 的个体偏差——不会让相邻的树完全反向，但也不至于完全克隆

### 5.3 四级风：为植被场景引入全局风参数

当前 `applyWind` 每次调用时 `windStrength` 是外部传入的单一值。建议引入全局风参数对象，所有植物从同一风场读取：

```javascript
// 全局风参数（所有植物共享——由概念种子偏置 + 时间驱动）
const WIND = {
  strength: 0.25,   // 0-1 总风强 —— 概念种子"慢下来不是落后"→ 0.15
  speed: 2.0,       // 风速
  angle: 45,        // 风向（度）—— 2D 像素画中简化为"从哪侧吹来"
  gustScale: 0.5,   // 阵风空间频率
  turbulence: 0.28, // 逐元素独立摆动幅度
  flutter: 0.28,    // 尖端颤振幅度
};

// 在每帧更新时：
function updateWind(time) {
  // 风力随时间缓慢变化（模拟自然风的变化——不是恒定的）
  WIND.strength = 0.25 + sin(time * 0.3) * 0.08 + sin(time * 0.7) * 0.05;
  // 范围 0.12-0.38 —— 有变化但不过于剧烈
}

// applyWind 内部改为：
function applyWind(tree, canopyPixels, time, px) {
  const intensity = windIntensity(tree.trunk.x, tree.index, time, WIND);
  const w = intensity;  // 替代原来的 windStrength
  
  // ... 三级风逻辑不变，但 w 现在是空间传播的
}
```

**与概念种子偏置的集成**（`design-principles.md §十六`）：
- "每棵树有自己的节奏"（慢下来不是落后）→ `WIND.strength = 0.15`, `WIND.speed = 1.2`
- "被遗忘的花园在呼吸"（神秘/宁静）→ `WIND.turbulence = 0.15`, `WIND.flutter = 0.1`
- "暴风雨后的平静"（治愈/释放）→ Act 2 `WIND.strength = 0.6` → Act 3 `WIND.strength = 0.1`

### 5.4 自检（追加到 §八 风相关项）

- [ ] 多棵树是否使用 `windIntensity(x, idx, time, WIND)` 而非裸的 `windStrength`？
- [ ] 相邻的树（X 差 < 10px）是否自然同步（不是克隆、不是完全反向）？
- [ ] 远处的树（X 差 > 50px）是否有明显的相位差？
- [ ] 2D 像素画是否忽略了垂直下垂（`dv`）分量？
- [ ] 颤振频率在 2D 中是否降到了 6-10Hz（不是 12-20Hz）？
- [ ] 全局 WIND 参数是否与概念种子偏置一致？

---

## 六、林地生成（多棵树的空间编排）

一棵树是单体。一片树林需要编排：

```javascript
/**
 * 生成一片林地
 * @param {number} count - 树木数量
 * @param {string} speciesKey - 主物种（'conifer' | 'broadleaf' | 'shrub'）
 * @param {number} groundY - 地面 Y 坐标
 * @param {number} areaW - 林地宽度
 * @param {number} px - 像素单位
 * @param {function} rng - 确定性随机函数
 */
function generateGrove(count, speciesKey, groundY, areaW, px, rng) {
  const sp = SPECIES[speciesKey];
  const trees = [];

  for (let i = 0; i < count; i++) {
    // x 位置：非均匀分布——用 Poisson-like 拒绝采样避免树挤在一起
    let x;
    let attempts = 0;
    do {
      x = areaW * 0.1 + random() * areaW * 0.8;  // 左右留 10% 边距
      attempts++;
    } while (
      attempts < 20 &&
      trees.some(t => Math.abs(t.trunk.x - x) < sp.canopy.gridW * px * 0.8)  // 树冠不重叠
    );

    // 深浅排序：远处的树（小、浅）= 先画。近处的树（大、深）= 后画
    const depthFactor = 0.6 + random() * 0.4;  // 0.6=远（小）, 1.0=近（大）
    // 缩放整个物种参数的基准 px
    const scaledPx = Math.round(px * depthFactor);

    const tree = growTree(sp, x, groundY, rng);
    const canopyPixels = generateCanopy(tree, sp, scaledPx, rng);

    trees.push({
      tree: tree,
      canopyPixels: canopyPixels,
      depthFactor: depthFactor,
      scaledPx: scaledPx,
    });
  }

  // 按 depthFactor 排序：远的先画（被近的遮挡）
  trees.sort((a, b) => a.depthFactor - b.depthFactor);

  return trees;
}
```

**林地编排规则**：
- x 位置用拒绝采样——新树不能和前树树冠重叠 > 80%
- `depthFactor` 产生大小差异——远的树小/浅、近的树大/深 = 免费的纵深
- 按 depthFactor 排序绘制——远的先画，近的后画覆盖
- 场景含多种物种时，分别生成各物种的 grove → 统一排序 → 统一绘制

---

## 七、反模式速查

| # | 反模式 | 级别 | 表现 | 修复 |
|---|--------|------|------|------|
| 1 | 所有树同一高度 | 致命 | 森林像梳子——树顶齐平 | 用物种表的 heightMin/heightMax 区间 + random() |
| 2 | 分叉同一高度 | 致命 | 树干顶部同时分出 3 根等长枝 | 分层槽位 + 随机偏移（§三 `growBranch`） |
| 3 | 实心树冠无间隙 | 致命 | 绿色实心块——不真实 | `density` < 0.6 → 像素有间隙 = 透光 |
| 4 | 同步风摆动 | 致命 | 所有树同时左同时右 | 三级风 + 每像素/每枝独立相位（§五） |
| 5 | 树排列成行 | 警告 | 人工种植园，不是森林 | 拒绝采样（§六 `generateGrove`） |
| 6 | 改 seed 变物种 | 警告 | seed=42 松树，seed=99 柳树 | seed 控制个体差异，speciesKey 控制物种身份 |
| 7 | 同一颜色无变异 | 警告 | 每棵树颜色完全相同 | 调色板 + random() 选色 + 高度加权 |
| 8 | 20 棵树 60fps→15fps | 警告 | 像素数无预算控制 | 远树 `depthFactor` 缩像素单位 = 减少总像素数 |
| 9 | 树冠在分支之前生成 | 致命 | 树冠位置和分支终点不对齐 | `generateCanopy()` 在所有分支生成后调用 |

---

## 八、自检清单

- [ ] 使用了物种表（不是硬编码一棵树）？
- [ ] 每棵树的参数在 min/max 区间内用 random() 取值？
- [ ] 分支用队列迭代，非递归？
- [ ] 子分支通过分层槽位 + 角度置换分布在不同的高度/角度？
- [ ] 树冠在分支拓扑稳定后统一生成（不是边生分支边加叶子）？
- [ ] 树冠 `density` < 0.65（有像素间隙 = 透光）？
- [ ] 风实现了三级独立系统（叶颤 Hz/支摇 Hz/干摆 Hz）？
- [ ] 多棵树的风驱动来自 `windIntensity(x, idx, time, WIND)`（四组分空间传播，非裸 windStrength）？
- [ ] 相邻树（X 差 < 10px）自然同步、远处树（X 差 > 50px）有明显相位差？
- [ ] 2D 像素中颤振频率已降为 6-10Hz、忽略 dv 分量？
- [ ] 多棵树用拒绝采样排布 + depthFactor 深浅排序？
- [ ] 改 seed 不改物种 → 个体差异（非物种变化）？
