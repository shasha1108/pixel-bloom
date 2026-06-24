# Pixel Aero 通用方法论

> 不穷举场景。掌握这些原则，任意新场景都能自主做对决策。

## 一、架构

### 固定画布
像素艺术用固定像素尺寸（320×480 或类似），`transform:scale()` 适配屏幕。不传 `windowWidth/windowHeight`。

```javascript
const CW=320,CH=480;
createCanvas(CW,CH);noSmooth();
```

`noSmooth()` 在固定画布上单独生效（不需要 `pixelDensity(1)`，高 DPI 下后者反而可能发虚）。

### CSS Z-index 优于 JS
p5.js 会覆盖 JS 设置的 canvas style。固定画布场景用 CSS `!important`。

```css
canvas{position:absolute!important;z-index:7!important;pointer-events:none}
```

### 玻璃容器三层分离（三明治架构锁死）
```
z=1: 环境极光光斑 (CSS 径向渐变, fixed, 缓慢漂浮)
z=2: 容器后背板 (毛玻璃 backdrop-filter:blur, 仅此层有模糊)
z=3: Canvas 像素渲染层 (position:fixed, drop-shadow 内部投影)
z=4: 容器前玻璃壳 (::after 曲面高光, 无模糊, pointer-events:none)
z=10: 交互拦截层 (#interact-layer, 原生 pointerdown 事件)
```
**铁律：blur 只在 z=2 底板层，永远不在 canvas 上层或玻璃壳层。**

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
**像素呼吸：方向符号推，禁止 scale()。** 边缘块沿自身方向外推 1PX；蘑菇/荧光体用颜色明暗交替。

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
原生 `pointerdown` + 300ms 时间戳隔离：
```javascript
let lt=0,to;layer.addEventListener('pointerdown',e=>{
  let n=Date.now();if(n-lt<300){clearTimeout(to);onDouble();lt=0}else{lt=n;to=setTimeout(onSingle,300)}
});
```
不用 p5 内置双击事件。

### 反馈要求
交互至少产生一种视觉反馈（涟漪/粒子/颜色变化/缩放）和一种听觉反馈（Web Audio 合成音效）。

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

## 八、三大系统性反模式（来自 time-tree 的 7 轮返工教训）

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

三步质检链必须**强制执行**——缺了 JS 语法检查和浏览器实测的 validate.py 是假绿灯。

- **validate.py**（静态模式匹配）→ 查结构缺失，查不了语法错误和渲染 bug
- **`node --check`**（JS 语法）→ 阻止白屏，每次必跑
- **浏览器实测** → 点一下看有没有反应，树是不是正的，猫是不是在树后面

**铁律：三步全绿才交付。跳任一步 = 白屏/倒树/无响应。**

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

## 十一、架构级 Prompt 模板

以下压缩版可复制到任何模型，跳过解释直接产出高质量代码：

```
角色：顶级生成艺术家 + 图形学前端专家 + 交互声效设计师。
用 p5.js + 原生 HTML/CSS 写一个 [场景] 的 H5。严守以下底线：

1. 运动：禁用 random() 和线性运动。用 Perlin noise() 做有机运动，
   sin() 做呼吸，lerp() 做阻尼跟随。
2. 层级：毛玻璃绝不遮挡 Canvas。三层分离：底板模糊 → Canvas 锐利 →
   顶层 ::after 斜切渐变高光（模拟菲涅尔反射）。
3. 交互：禁用 p5.js 内置鼠标事件。原生 pointerdown + 300ms 时间戳
   隔离单击/双击。
4. 音效：Web Audio API。174Hz/432Hz 三角波底噪，ADSR 包络 2-3秒
   长尾泛音模拟风铃/颂钵。
5. 像素：noSmooth()。运动用浮点，translate 时 round() 取整防发虚。
```

---

## 十二、Ganzfeld × Turrell 光空间模式

当用户提到"沉浸""冥想""光浴""漂浮感"时启用。本质上是用代码模拟**感官剥夺 + 光场锚定**。

### 背景：无边界光场
不用天空渐变（有方向暗示）。用 `radial-gradient` 消除地平线和深度参照。
```css
/* Ganzfeld 光场：20-30s 极缓慢色相呼吸 */
@keyframes fieldBreath {
  0%,100% { background: radial-gradient(ellipse, #2a1a3a 0%, #0a0a1a 100%); }
  50%     { background: radial-gradient(ellipse, #3a1a2a 0%, #0a0a1a 100%); }
}
body { animation: fieldBreath 25s ease-in-out infinite; }
```

### Turrell 调色盘
- 蓝紫→深黑：`#2a1a3a` `#0a0a1a`（深渊）
- 日落橙→暖粉：`#3a2018` `#5a2a28`（光浴）
- 荧光粉→紫红：`#4a1a3a` `#2a0a1a`（霓虹）

### 运动拖影（Trail Effect）
不全清画布 → 像素物体留下梦幻残影，模拟感官剥夺中的视觉残留。
```javascript
// 替代 clear()：半透明背景叠加，旧帧缓慢消隐
fill(10, 8, 20, 12); rect(0, 0, width, height);
```

### 双耳节拍（Binaural Beats）
左右耳频率差产生 Theta 波（4Hz）共振，强制深度放松。
```javascript
// 左 432Hz / 右 436Hz → 4Hz Theta 波
let left = ac.createOscillator(); left.frequency.value = 432;
let right = ac.createOscillator(); right.frequency.value = 436;
let merger = ac.createChannelMerger(2);
left.connect(merger, 0, 0); right.connect(merger, 0, 1);
merger.connect(ac.destination);
```
配合粉红噪音（Pink Noise）底噪，消除环境干扰。

### 交互即光变（Light Shift）
长按不触发生长/投食，而是触发**全局光场色相缓慢漂移**——从深蓝渐变到暖粉。用户不是在操作物体，是在进行"数字光浴"。

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
