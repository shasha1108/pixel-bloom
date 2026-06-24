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

# Pixel × Frutiger Aero

生成 p5.js 像素渲染 + Frutiger Aero 毛玻璃美学的独立 H5 页面。
**执行前必须阅读 `references/pixel-aero.md`**（4 种生成模型、FSM、Z-index 三明治、防坑清单）。

## 边界规则

- **范围上限**：单页 H5，最多 10 个自主生命体。超过 → 建议分批
- **拒绝场景**：完整游戏、多页应用、非像素风格 → 告知本 skill 覆盖范围并拒绝
- **信息不足时反问**：用户只说"做个好玩的"→ 反问："你想象的是一个玻璃容器里的场景吗？水里游的、土里长的、还是桌面摆件？"
- **输出位置**：所有 H5 文件写到 `~/Documents/h5/`（用户可自定义 `$H5_OUTPUT_DIR`）

## 生成流程

### 1. 尺寸选择

**生成前必须先询问用户画幅比例。** 提供以下选项：

| # | 比例 | 适用场景 |
|---|------|---------|
| 1 | 3:4 | 小红书竖屏 |
| 2 | 9:16 | 抖音/快手竖屏 |
| 3 | 1:1 | Instagram 方形 |
| 4 | 4:3 | 标准平板 |
| 5 | 16:9 | 桌面横屏 |
| 6 | 2:3 | 手机竖屏 |
| 7 | 3:2 | 摄影横屏 |

用户选择后，CSS 容器使用 `aspect-ratio` 锁定画幅，Canvas 尺寸按比例计算。

### 2. 场景拆解

从用户描述中提取 4 个要素。任一不明确 → 反问。

| 要素 | 示例 |
|------|------|
| 场景类型 | **封闭容器**（水族箱/花盆/天气瓶）\| **开放景观**（沙漠/草原/海底/天空） |
| 生命体 | 鱼 / 仙人掌 / 多肉 / 宠物 / 珊瑚 / 自定义 |
| 交互 | 投食 / 浇水 / 敲玻璃 / 抚摸 / 无交互 |
| 核心隐喻 | 这个场景"在现实世界中对应做什么"（擦拭=净化，投食=关怀，浇水=滋养） |

**场景类型决定视觉架构：**
- **封闭容器**：Z-index 三明治（毛玻璃底板 + Canvas + 玻璃外壳），有容器边框和反光
- **开放景观**：无边界的 Frutiger Aero 天空渐变 + 环境光斑 + 像素地表，无玻璃壳。用 CSS 渐变 + 太阳/云朵/星辰等元素构建空间感

### 3. 技术选型

打开 `references/pixel-aero.md`（技法配方）和 healing-space 的 `references/audio-engine.md`（音效武器库），根据生命体类型选择：

- **有自主运动**（鱼/宠物）→ 完整 FSM + 表情系统 + 音效反馈
- **无自主运动**（植物/珊瑚）→ React-only 模式 + 生长动画 + 音效反馈
- **角色深度**：生命体必须有表情/情绪变化（颜文字/颜色 lerp/肢体变形至少一种），不同状态下视觉不同
- **音效系统**（遵循 audio-engine.md 的铁律）：
  - 所有声音用 Web Audio API 纯代码合成，零音频文件
  - AudioContext 在首次用户交互时初始化并 `resume()`
  - `masterGain` 起始值为 0，通过 `linearRampToValueAtTime` 淡入，禁止直接设满音量
  - 至少包含一种交互反馈音效（pop/chime/drone），按场景情绪选配方
- **核心隐喻驱动 ≥2 个机制**：如"投食=关怀"→追食动画+表情变化+音效+生长

选择程序化生成模型（A/B/C/D），按场景需要选，一种也够。

### 4. 前端架构

必须实现 Z-index 三明治（pixel-aero.md §防御性前端骨架）：

```
背景渐变 → 毛玻璃底板(z:2,blur) → Canvas(z:3,drop-shadow) → 玻璃壳(z:4,无blur) → 交互层(z:5)
```

配色默认使用 Frutiger Aero 清透色系，除非用户指定：
- 底色 `linear-gradient(160deg, #a8e6f8, #cdf0fa, #e4f8f0, #f4fcf9)`
- 玻璃边框 `rgba(255,255,255,0.7)`，上厚下薄
- 生命体使用预设调色板数组，不为每个物体独立随机 RGB

### 4. 交互实现

复制 pixel-aero.md §防坑铁律 的标准模板：
- 单击/双击分离：自定义 `pointerdown` + 300ms 超时
- 触发反馈：CSS ripple / 粒子 / 颜色变化 / 缩放（至少一种）
- 移动端：`user-scalable=no`, `touch-action: none`

### 5. 三步质检链

生成 HTML 后，按顺序执行。**任一步不通过 → 修复 → 重跑 → 全部通过才交付。**

**Step 5a · 静态分析**

```bash
python3 scripts/validate.py <输出文件.html>
```
8 类 28 项自动检查。修复所有 ❌ 致命错误和 ⚠️ 警告。

**Step 5b · 代码审查**

调用 `/code-review` 审查生成的 HTML 文件，effort 设为 `high`。聚焦：
- 交互事件是否正确绑定（pointerdown 回调、事件穿透、preventDefault）
- 状态切换逻辑是否完整（rain→bloom、toggle→spawn）
- 边界条件（窗口缩放后坐标更新、粒子回收）

**Step 5c · 浏览器实测（强制，不可跳过）**

调用 `/verify`，在浏览器中打开生成的 HTML，**必须逐项操作并观察**：
- 页面正常渲染，无白屏或布局错乱
- 单击交互 → 确认状态切换生效（文字/视觉均变化）
- 双击交互 → 确认特效触发
- 检查视觉元素是否符合描述（云是像素云不是白球、花可见、数量正确）
- 移动端视口缩放正确

**实测不通过 → 修复 → 重新实测 → 通过后才交付。**

### 6. 人工验证清单

三步自动化通过后，逐条确认：

1. 生命体有 ≥3 个状态的 FSM，或 React-only 模式有 ≥2 种不同反馈
2. 生命体有表情/情绪变化系统（像素颜文字/颜色变化/形状变化至少一种），随状态切换
3. 生命体有平滑动画（呼吸缩放/stretch/lerp 颜色过渡至少一种），非刚性平移
4. 交互有视觉 + 听觉双重反馈——Web Audio 纯代码合成，零音频文件，masterGain 淡入不爆音
5. Canvas z-index=3，不被毛玻璃模糊
6. 配色来自预设数组，无裸 random RGB
7. Canvas 有 `filter: drop-shadow()` 景深
8. `pixelDensity(1)` + `noSmooth()` 已设置
9. 移动端 `user-scalable=no`
10. HTML 顶部有完整元数据注释头（Title/Summary/Tech/Keywords/Render/Audio/Touch/Dependencies/Repo）
11. 文件已输出到 `~/Documents/h5/`
12. 核心隐喻驱动 ≥2 个机制（如"投食=关怀"→追食+表情变化+音效+长大）
