# Pixel Bloom 通用方法论

> 不穷举场景。掌握这些原则，任意新场景都能自主做对决策。

## 一、架构

### 固定画布
像素艺术用固定像素尺寸 + `transform:scale()` 适配屏幕。尺寸由用户选择的画幅比例决定（如 3:4 → 640×960，16:9 → 960×540），不传 `windowWidth/windowHeight`。

```javascript
const CW=640,CH=960;  // 示例：3:4 竖幅，根据所选比例调整
createCanvas(CW,CH);noSmooth();
```

`noSmooth()` 在固定画布上单独生效（不需要 `pixelDensity(1)`，高 DPI 下后者反而可能发虚）。

### 玻璃容器三层分离（全场景统一 Z-index，不得更改）

```
z=1  环境极光光斑（CSS 径向渐变，fixed，缓慢漂浮）
z=2  毛玻璃底板（唯一有 backdrop-filter:blur 的层）
z=3  Canvas 像素渲染层（JS 强控：c.style('z-index','3') + drop-shadow 内部投影）
z=4  玻璃外壳（::after 菲涅尔高光，绝对不加 blur，pointer-events:none）
z=5  交互拦截层（#interact-layer，原生 pointerdown 事件）
```

**铁律：blur 只在 z=2 底板层，永远不在 canvas 上层或玻璃壳层。** 无玻璃的开放场景中 z=2 和 z=4 不存在，其余层级保持不变。

容器尺寸固定时，穹顶/球体的 border-radius 用精确数学值：
- 穹顶 `border-radius: <玻璃宽度的一半>px <玻璃宽度的一半>px 0 0`
- 球体 `border-radius: 50%`（正方形元素）
- 玻璃高光用 `::after` 斜切 `linear-gradient`（模拟菲涅尔反射）

### 无玻璃的开放场景
全视口天空渐变 + `position:fixed` 极光光斑 + canvas 填满视口。无玻璃壳层。

---

## 二、形状

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

## 三、运动（仿生数学三法则）

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

### Perlin 粒子 + 双圈发光
```javascript
let ang=noise(s.x*.01,s.y*.01,frameCount*.02)*TWO_PI*2;
s.vx+=cos(ang)*.1;s.vy+=sin(ang)*.1;s.vx*=.95;s.vy*=.95;s.vy-=.02;
// 渲染
blendMode(SCREEN);
fill(100,200,255,a*.3);circle(x,y,sz*4);   // 外光晕
fill(255,255,255,a);   circle(x,y,sz*1.5); // 内亮点
blendMode(BLEND);
```

---

## 四、材质

### 玻璃光泽
- 边框不等宽（上 3px 厚 / 下 1px 薄）
- `::after` 对角白色渐变高光
- `inset` 内发光（厚度感）
- 水珠挂载到玻璃 DOM 元素内：`dome.appendChild(drop)`

### 水珠透镜
```css
.water-drop{backdrop-filter:brightness(1.2) contrast(1.3) blur(2px);
  box-shadow:inset 2px 2px 4px rgba(255,255,255,.8),0 5px 5px rgba(0,0,0,.1)}
```

### 底座质感
3 段渐变（亮面→固有色→暗面）+ 强外投影 + 顶部高光线 = 物体重量感。

---

## 五、交互（防冲突法则）

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

## 六、色彩

- 预设调色板数组，不为每个物体独立 random RGB
- Frutiger Aero 底色：`linear-gradient(160deg,#a8e6f8,#cdf0fa,#e4f8f0,#f4fcf9)`
- 场景内 2-3 套调色板统一色调

---

## 七、音效

所有声音 Web Audio API 纯代码合成，零音频文件。
- AudioContext 在首次用户交互时初始化并 resume
- masterGain 起始值 0，linearRampToValueAtTime 淡入防爆音
- 174Hz 三角波 drone 作为治愈底噪（可选）
- 交互反馈音效：sine wave pop/chime

---

## 八、三大系统性反模式

### 反模式 1：p5.js Y 轴方向陷阱

p5.js 的 Y 轴指向**下方**（与数学坐标系相反）。所有角度计算必须用 `+sin(ang)` 而非 `-sin(ang)`。

```javascript
// ✅ p5.js 正确
ey = by + sin(angle) * length;

// ❌ 数学坐标系（p5 中会反向）
ey = by - sin(angle) * length;
```

**预防：** 写完任何涉及角度的绘制代码后，脑中默念 "p5 Y-down, +sin = down, -sin = up"。

### 反模式 2：CSS 与 p5.js canvas 属性冲突

p5.js 在 `createCanvas()` 时自己设置 `style` 属性。CSS 用 `!important` 或 `inset` 覆盖时与 p5 内部逻辑冲突，导致 canvas 完全消失。

**正解：** 用 `c.parent('containerId')` 把 canvas 挂到指定 DOM 元素下，样式全部用 JS 设置（`c.style(...)`），**不用 CSS 选择器覆盖 canvas 属性**。需要 `border-radius` 或 `overflow:hidden` 时也在 JS 中设。

```javascript
let c = createCanvas(CW, CH);
c.parent('myContainer');
c.style('position', 'absolute');
c.style('top', '20px');
c.style('left', '20px');
c.style('z-index', '2');
```

### 反模式 3：校验通过 ≠ 页面正常

两步质检链必须**强制执行**——缺了浏览器实测的 validate.py 是假绿灯。

- **validate.py**（静态结构 + JS 语法检查）→ 查结构缺失和语法错误
- **浏览器实测** → 点一下看有没有反应，树是不是正的，猫是不是在树后面

**铁律：两步全完成才交付。跳任一步 = 白屏/倒树/无响应。**

---

## 九、听觉心理学（Web Audio 疗愈频段）

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

## 十、排版（Frutiger Aero 字体法则）

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

## 十一、Aero-Ganzfeld 光空间模式

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

## 十二、参数设计思考框架

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

## 十三、屏幕像素锚定法则（全场景通用）

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

## 十四、对抗式检查 SOP（全场景通用 · 强制执行）

**写完代码后，用脚本做结构性检查。人脑无法同时追踪所有参数的一致性。**

### 检查项

| # | 检查项 | 方法 | 级别 |
|---|--------|------|------|
| 1 | JS 语法 | `new Function(script)` | 致命 |
| 2 | API 兼容性 | 扫描 `fill(hex+'cc')` 等字符串拼接 α 值 → 替换为 `rgba()` | 致命 |
| 3 | 地形/背景参数一致性 | 元素放置函数与场景绘制函数的参数交叉比对 | 致命 |
| 4 | 元素坐标冲突 | 提取所有地面元素的 (x,y) 与水体/障碍边界交叉计算 | 致命 |
| 5 | 跨浏览器兼容性 | 扫描 `rect(x, y, w, -h)` 等负尺寸 → 替换为正尺寸 | 警告 |
| 6 | 缩放可见性 | 提取所有 `scale` 值，计算实际像素，标记 < 15px 的 | 警告 |
| 7 | 颜色可见性 | 提取元素颜色与背景颜色，计算反差，标记 < 60 的 | 警告 |

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

console.log(issues.length ? issues.join('\n') : 'All checks passed');
```

### 14.5 像素视觉验证（对抗式检查之后 · 质检之前 · 强制执行）

对抗式检查验证了"代码结构安全"——但它不能验证**运行时视觉正确**。以下 4 项是脚本扫描不到的、必须由人脑+计算确认的视觉硬指标。**WARN 不是"可以忽略"——WARN 的项目必须在本步骤逐项目测确认。**

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

固定画布（如 640×960）通过 `transform: scale()` 适配屏幕。验证不同视口下的视觉：

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

## 十五、第一性原理创作流程（全场景通用）

### 决策链（从情感锚点到代码）

```
情感锚点（这个作品让人感受到什么？）
  ↓
物理隐喻（什么自然现象承载这个感受？）
  ↓
纵深/空间结构（几层？每层什么内容？开放场景用 landscape-composition.md §一）
  ↓
三要素落地（可进入的纵深？尺度参照物？活的细节？开放场景用 landscape-composition.md §二）
  ↓
参数锚定（每个 scale/size/color → 对应多少实际像素？→ 本文件 §十三）
  ↓
交叉验证（元素是否在它应该在的地方？→ 本文件 §十四）
  ↓
对抗式检查（脚本跑一遍 → 本文件 §十四）
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

## 十六、概念种子→参数偏置（STEP 3 参数决策后强制执行）

概念种子是 pixel-bloom 的情绪锚点。**但它不能只是命名和宏观方向——必须系统化地偏置所有参数选择。**

当前流程：STEP 3 技术决策 → 自问"颜色温度、运动速度、交互节奏是否与概念种子一致？"——这是**事后追问**。如果发现不一致，需要回退重选——模型大概率不会真的回退，而是说服自己"还行"。

**改为事前约束**：STEP 3 参数决策完成后，逐项对照下表。**参数选择不允许在偏置方向上反向。**

### 偏置方向表（按概念种子）

| 概念种子 | 色温 | 运动速度 | 交互响应模式 | 粒子/元素密度 | 音效方向 |
|---------|------|---------|------------|-------------|---------|
| **Always Here**（它会一直在） | **暖** +20%（偏橙/金/奶油白） | **慢** -30%（呼吸级缓动优先） | **回应感**（交互后 300-500ms 内有微妙变化——不是立刻弹，也不是不回应） | **偏疏**（不拥挤——陪伴是空间，不是压迫） | 低频暖底噪 + 单音确认（不喧宾夺主） |
| **Still Growth**（不需观众） | **中性偏冷**（莫兰迪绿/灰蓝） | **极慢** -50%（几乎静止的微动） | **自主变化 > 交互反馈**（用户不碰也在变；碰了反而不一定有回应——它不在乎） | **疏**（每个元素有独立呼吸空间） | 极静或干脆无音效 |
| **Another Tank**（平行存在） | **中性**（水下蓝绿/自然色） | **中速**（自然游动节奏） | **无直接响应**（鱼不在乎你有没有在看——交互不影响运动，最多影响环境光） | **正常**（世界是满的，不是为人留白） | 水下低频闷响 + 气泡音 |
| **Windmill Valley**（可走入） | **Golden Hour 暖**（暖金光源 + 大气透视蓝移） | **自然风变速**（Perlin 噪声驱动，1.0-2.5 级波动） | **滑动 = 感受风**（鼠标/手指滑过有风轨跟随；单击 = 风铃触发） | **偏密**（世界是完整的——该有的都有） | 风底噪 + 风铃五声音阶 + 风速→音高映射 |

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

## 十七、像素风速场 — 全场景风元素统一采样

> 设计哲学源自 OceanThreejs 的"位移场→一切"：泡沫/法线/颜色都从同一个底层场派生。适配到 pixel-bloom：**所有被风驱动的像素元素——树 sway、水面波浪、花粉粒子、蝴蝶——从同一个 Perlin 风速场 `windField(x, y, time)` 采样。**

### 17.1 为什么需要共享风场

`vegetation-system.md` 的三级风很好——但每棵树各自调用 `sin(time * freq + phase)`。`ocean-pixels.md` 的波浪用 `wave.speed * time + phase`。花粉用 `noise(x*0.01, time*0.3)`。**三套时间尺度、三套相位——看起来不是同一阵风。**

反模式场景：树同时向左歪（sin 同步）、水面波浪向右涌（相位偏移不同）、花粉向下漂（noise 梯度方向）→ 三个"风驱动"元素在互相矛盾。用户不会说"风场不统一"——用户会说"感觉不自然"。

### 17.2 风速场定义

```javascript
/**
 * 像素风速场——全场景共享
 * @param {number} x - 世界 X 坐标（像素空间）
 * @param {number} y - 世界 Y 坐标
 * @param {number} time - 全局时间（秒）
 * @param {number} strength - 全局风速 0~1（从概念种子偏置或外部 Perlin 噪声驱动）
 * @returns {{vx: number, vy: number}} 风速向量（-1~1 范围，未乘振幅）
 */
function windField(x, y, time, strength = 1.0) {
  // 双层 Perlin 噪声——大尺度风带 + 小尺度阵风
  const sx1 = x * 0.005;
  const sy1 = y * 0.005;
  const sx2 = x * 0.02;
  const sy2 = y * 0.02;

  const t = time * 0.3;  // 风速变化速度

  // 大尺度——持续风向（变化慢）
  const vx1 = noise(sx1 + t, sy1) * 2 - 1;
  const vy1 = noise(sx1 + t + 100, sy1 + 100) * 2 - 1;

  // 小尺度——阵风（变化快）
  const vx2 = (noise(sx2 - t * 2, sy2) - 0.5) * 1.5;
  const vy2 = (noise(sx2 - t * 2 + 50, sy2 + 50) - 0.5) * 1.5;

  // 混合：大尺度 70% + 小尺度 30%
  return {
    vx: (vx1 * 0.7 + vx2 * 0.3) * strength,
    vy: (vy1 * 0.7 + vy2 * 0.3) * strength,
  };
}
```

**关键设计**：
- **双层噪声**：大尺度（0.005）产生持续风向——一整片区域的元素朝同一方向偏。小尺度（0.02）产生阵风——单棵树可能有额外的微颤
- **time 乘以不同的系数**：大尺度变化慢（`*0.3`），小尺度变化快（`*2`）→ 风向整体持续但不断有小阵风叠加
- **返回向量，非标量**：风向 + 强度在一个返回值中——元素可以计算"风在推我往哪个方向"

### 17.3 各元素从风速场采样

#### 树 sway（替代 vegetation-system.md §五 的独立 sin）

```javascript
// 旧：每棵树独立 sin
// tree.swayOffset = sin(time * 1.5 + tree.phase) * 3.0 * windStrength;

// 新：从风速场采样——同一阵风，不同树有不同偏移
const wind = windField(tree.trunk.x, tree.trunk.y, time, windStrength);
tree.swayOffset = wind.vx * 3.0;  // 树干 sway ±3px
// 叶颤：叠加风速场的小尺度高频——直接用 noise 的第二层
const gust = windField(tree.trunk.x + 5, tree.trunk.y + 5, time, windStrength);
tree.leafFlutter = gust.vx * 1.0;  // 叶颤 ±1px
```

#### 水面波浪相位偏移（替代 ocean-pixels.md 的独立 speed）

```javascript
// 旧：每条波浪独立 speed
// const theta = wave.freq * x + wave.speed * time + wave.phase;

// 新：从风速场采样——风的局部方向影响波浪相位
const wind = windField(x, horizonY, time, windStrength);
const phaseShift = wind.vx * 0.3;  // 风向改变波浪的视觉相位
const theta = wave.freq * x + wave.speed * time + wave.phase + phaseShift;
```

#### 花粉/粒子漂移

```javascript
// 旧：独立 Perlin 漂移
// p.vx += (noise(p.x * 0.01, time * 0.3) - 0.5) * 0.1;

// 新：从风速场采样——和树/水面共享同一阵风
const wind = windField(p.x, p.y, time, windStrength);
p.vx += wind.vx * 0.1;  // 花粉被风推着走
p.vy += wind.vy * 0.05; // 垂直分量更小——风主要水平吹
```

#### 蝴蝶 FSM 风向偏置

```javascript
// 蝴蝶的 targetAngle 被风推偏——它逆风飞行时更吃力
const wind = windField(butterfly.x, butterfly.y, time, windStrength);
butterfly.targetAngle += wind.vx * 0.05;  // 轻微的航向偏置
butterfly.speed *= (1.0 - Math.abs(wind.vx) * 0.3);  // 逆风减速
```

### 17.4 统一 windStrength 来源

`windStrength` 本身可以从概念种子偏置 + 一个慢速 Perlin 噪声驱动：

```javascript
// 全局风速——0.5~2.0 的自然波动
function globalWindStrength(time) {
  const base = 0.5 + noise(time * 0.1) * 1.5;  // 10 秒周期——风速自然变化
  // 概念种子偏置：
  //   Always Here: base * 0.5 (微风)
  //   Windmill Valley: base (自然风)
  //   Still Growth: base * 0.2 (几乎无风)
  return base * CONCEPT_SEED_WIND_BIAS;
}
```

### 17.5 何时不必用风速场

| 场景 | 原因 |
|------|------|
| 赛博宠物（封闭容器） | 容器内无风——宠物 FSM 不依赖风 |
| 像素盆栽（室内） | 室内微风——如果有，用一个全局标量就够了，不需要空间变化 |
| 只有一个风驱动元素 | 单棵树或单层波浪——风速场的跨元素协调优势不存在 |
| Ganzfeld 模式 | 无风——光场场景 |

### 17.6 自检

- [ ] 场景中所有风驱动元素从同一个 `windField()` 采样？
- [ ] 大尺度噪声（持续风向）+ 小尺度噪声（阵风）双层叠加？
- [ ] `windStrength` 从概念种子偏置（不同场景不同风力）？
- [ ] 不同元素用了不同的振幅乘数（树 3px，花粉 0.1px，波浪 0.3 相位）？
- [ ] 如果场景只有一个风驱动元素——风速场不是必需的（不要过度工程）？

---

## 十八、跨模型视觉密度校准

> 设计哲学与 healing-space 跨路线情绪强度校准同构：不同算法在同一参数下产生不同的视觉输出 → 需要校准表在算法之间建立等价映射。

### 18.1 问题

4 种程序化模型对 `density` 参数的解释不同——同一个值产生截然不同的视觉密度：

| 模型 | density 的实际含义 | density=0.5 时的实际像素保留率 |
|------|-------------------|---------------------------|
| **A**（堆叠摇摆） | 无 density 参数——段数控制视觉密度 | N/A |
| **B**（网格剔除） | 每个格子的独立保留概率 | 50% |
| **C**（圆域筛选） | **不读 density 参数**——内部硬编码 `random() > 0.15` | 85%（硬编码） |
| **D**（扇形展开） | **不读 density 参数**——内部硬编码 `random() > 0.4` | 60%（硬编码） |

**模型 C 和 D 的 density 参数不生效**——它们在自己代码中硬编码了筛选阈值。当场景混合使用多种模型时，不能传同一个 density 值。

### 18.2 校准表

**目标视觉密度 → 每个模型应该传的参数**：

| 目标效果 | 视觉感受 | 模型 B density | 模型 C 阈值 | 模型 D 阈值 |
|---------|---------|---------------|------------|------------|
| **极疏**（大量透光/透气） | 轻雾、薄纱、远山树冠 | 0.2 | 0.40 | 0.60 |
| **疏**（明显间隙） | 透光树冠、花簇 | 0.35 | 0.30 | 0.50 |
| **中**（半密实） | 正常灌木、云朵 | 0.5 | 0.20 | 0.40 |
| **密**（少量间隙） | 密实灌木、厚云 | 0.65 | 0.12 | 0.30 |
| **极密**（几乎不透光） | 实心物体、岩石 | 0.8 | 0.06 | 0.20 |

**使用方式**：不是直接传 density 值——是查表得到对应参数：

```javascript
// 目标：中密度灌木（模型 C 半球）
const targetDensity = 'medium';  // 或 0.5
const calibration = {
  B: { sparse: 0.2, light: 0.35, medium: 0.5, dense: 0.65, solid: 0.8 },
  C: { sparse: 0.40, light: 0.30, medium: 0.20, dense: 0.12, solid: 0.06 },
  D: { sparse: 0.60, light: 0.50, medium: 0.40, dense: 0.30, solid: 0.20 },
};

// 查表——不传裸数字
const thresholdC = calibration.C[targetDensity];  // 0.20
drawRadialCluster(x, y, 10, px, palette, thresholdC);
```

### 18.3 模型 C/D 的改造建议

如果修改 `code-templates.md` 中模型 C 和 D 的代码，让它们接受 density 参数（而非硬编码），可以直接使用统一 density 值：

```javascript
// 模型 C 改造——接受 density 参数
function drawRadialCluster(baseX, baseY, radius, px, palette, density = 0.5) {
  const threshold = 1.0 - density;  // density 0.5 → threshold 0.5
  for (let dy = 0; dy < radius; dy++) {
    let limit = round(sqrt(radius * radius - dy * dy));
    for (let dx = -limit; dx <= limit; dx++) {
      if (random() > threshold) {  // 原来: random() > 0.15
        fill(random(palette));
        rect(baseX + dx * px, baseY - dy * px, px, px);
      }
    }
  }
}

// 模型 D 改造——接受 density 参数
function drawFan(baseX, baseY, height, px, color1, color2, density = 0.5) {
  const threshold = 1.0 - density;
  for (let dy = 0; dy < height; dy++) {
    let spread = round(dy * 0.8);
    for (let dx = -spread; dx <= spread; dx++) {
      if (random() > threshold || abs(dx) === spread) {  // 原来: random() > 0.4
        fill(random() > 0.5 ? color1 : color2);
        rect(baseX + dx * px, baseY - dy * px, px, px);
      }
    }
  }
}
```

**如果改造了模型 C/D，校准表仍然有用**——它告诉你不同模型的 density→视觉密度 映射曲线不同（模型 B 是线性、模型 C 是圆形面积、模型 D 是扇形面积），即使参数名统一了，同一个 density 值在不同模型下的视觉密度仍然不同。校准表是持久的。

### 18.4 自检

- [ ] 场景中同时使用多种模型时，没有传同一个裸 density 值？
- [ ] 模型 C/D 的筛选阈值已对照校准表设置？
- [ ] 如果模型 C/D 已被改造接受 density 参数——确认了改造版本在 `code-templates.md` 中？
