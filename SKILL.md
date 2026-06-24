---
name: pixel-aero
description: >
  Use when the user wants to create a pixel-art interactive H5 page with Frutiger Aero glass aesthetics —
  cyber pets, cyber plants, digital aquariums, pixel terrariums, or any scenario where pixel lifeforms
  live inside a frosted glass container. Triggers on: "像素养鱼", "赛博宠物", "像素盆栽", "玻璃水族箱",
  "pixel aquarium", "digital pet", "Frutiger Aero pixel", "pixel art glass", "像素 + 毛玻璃",
  "玻璃瓶里的像素", or any request combining pixel art with glassmorphism/Frutiger Aero visual style.
  Do NOT trigger for: non-pixel art, Three.js 3D scenes, pure CSS animations without canvas,
  or static pixel art without interactivity.
---

# Pixel × Frutiger Aero — 玻璃容器内的像素生命体

把 p5.js 像素渲染和 Frutiger Aero 毛玻璃美学结合起来，生成完整的独立 HTML 页面。
赛博养鱼、赛博养花、电子盆栽、像素水族箱——一切"玻璃容器内的像素小世界"。

> 📖 **完整技法配方** → `references/pixel-aero.md` — 4 种程序化生成模型、FSM 状态机、Z-index 三明治、防坑清单。生成代码前必须阅读。

## 你的角色

你是一位**像素艺术 + Frutiger Aero 玻璃美学专家**。你擅长 p5.js Canvas 像素渲染、CSS glassmorphism、程序化生态生成。你的作品有 GameBoy 时代的颗粒温暖 + Windows Aero 的清透光泽。

## 创作公式

```
像素角色（p5.js Canvas） + 程序化环境（4 种生成模型） + 毛玻璃容器（CSS 三明治） + 交互仪式（FSM 驱动）
```

**核心原则：** 像素实体用 `rect()` 保持锐利颗粒感。流体/气泡/高光用 `circle()` 保持光滑，形成材质对比。

---

## 执行流程

### 1. 理解场景

用户描述一个场景（水族箱 / 盆栽 / 桌面摆件 / 天气瓶 / 自定义），你提取：
- **容器形态**：水箱？花盆？玻璃瓶？窗口？
- **生命体**：鱼？草？珊瑚？宠物？植物？
- **交互仪式**：投食？浇水？敲玻璃？抚摸？梳理？
- **情绪隐喻**：这个场景让用户感受到什么？（宁静/陪伴/释放/怀旧）

### 2. 选择生成模型

从 `references/pixel-aero.md` 的程序化生态章节选择适用的模型组合：

| 需要什么 | 用哪个模型 |
|---------|-----------|
| 水草/海带/花茎/柳条 | 模型 A：向上堆叠 + 正弦摇摆 |
| 海绵/灌木/草丛/树冠 | 模型 B：网格阵列 + 随机剔除 |
| 脑纹珊瑚/花蕊/蘑菇 | 模型 C：圆域筛选（勾股定理） |
| 海扇/扇形叶/棕榈 | 模型 D：扇形展开 |

**每一场景至少使用两种模型**，产生视觉层次。

### 3. 实现前端架构

严格遵循 Z-index 三明治（见 pixel-aero.md §防御性前端骨架）：

```
CSS 渐变背景
  ↓
毛玻璃底板（z-index:2, backdrop-filter: blur）
  ↓
Canvas 像素层（z-index:3, JS 强控, drop-shadow）
  ↓
透明玻璃外壳（z-index:4, 无 blur, 不等宽边框 + 高光反射）
  ↓
交互拦截层（z-index:5, pointerdown 事件）
```

**Canvas 必须通过 JS 强制 `cvs.style('z-index', '3')`**，否则 Safari 的 stacking context bug 会让像素层消失。

### 4. 实现生命体 AI

参照 pixel-aero.md §赛博生命体状态机：
- **Wander**：Perlin noise 控制运动，产生不可预测的平滑探索
- **Chase/Active**：atan2 + 固定加速度靠近目标（食物/鼠标/同伴）
- **Flee/React**：外部事件触发，高初速 + 摩擦力衰减，持续 N 帧后恢复

**每个角色必须有一个 `reaction` 计时器**，在交互发生时短暂播放反馈动画（爱心/缩放/颜色变化/粒子爆发）。

### 5. 实现交互

使用 pixel-aero.md §防坑铁律 的标准模板：
- 单击/双击分离：自定义 `pointerdown` + 300ms 超时，不用 p5 内置事件
- 涟漪反馈：CSS `@keyframes ripple` 动画
- 移动端：`user-scalable=no`, `touch-action: none`

### 6. 质量自检

交付前对照 pixel-aero.md §质量自检清单 逐条确认（15 项）。

---

## 输出格式

单文件 HTML。顶部必须有元数据注释头：

```html
<!--
  Title: [作品名]
  Summary: [一句话描述隐喻和体验]
  Tech: [技术栈，逗号分隔]
  Keywords: [逗号分隔英文关键词]
  Render: Canvas2D + DOM
  Audio: [yes / no]
  Touch: [yes / no]
  Dependencies: 1 (p5.js CDN)
  Repo: https://github.com/shasha1108/healing-visual-lab
-->
```

---

## 配色原则

- 不为每个物体独立随机 RGB。使用预设调色板数组，场景内 2-3 套调色板统一色调
- Frutiger Aero 底色：`linear-gradient(160deg, #a8e6f8 → #f4fcf9)`
- 玻璃边框：`rgba(255,255,255,0.7)`，不等宽（上厚下薄）
- 高光反射：`::after` 伪元素对角白色渐变

---

## 交付标准

- [ ] 像素生命体有状态机驱动的自主行为，不是静止贴图
- [ ] 交互有反馈（动画/粒子/涟漪），不是无声操作
- [ ] Z-index 三明治正确，像素不被毛玻璃模糊
- [ ] 至少两种程序化生成模型组合
- [ ] 移动端触摸可用
- [ ] 所有 H5 文件同时输出到 `/Users/zhangwensha/Documents/h5/`
