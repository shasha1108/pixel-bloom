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
- **输出位置**：所有 H5 文件写到 `/Users/zhangwensha/Documents/h5/`

## 生成流程

### 1. 场景拆解

从用户描述中提取 4 个要素。任一不明确 → 反问。

| 要素 | 示例 |
|------|------|
| 容器 | 玻璃水族箱 / 花盆 / 天气瓶 / 窗口 / 自定义 |
| 生命体 | 鱼 / 珊瑚 / 多肉 / 宠物 / 自定义 |
| 交互 | 投食 / 浇水 / 敲玻璃 / 抚摸 / 无交互 |
| 核心隐喻 | 这个场景"在现实世界中对应做什么"（擦拭=净化，投食=关怀，浇水=滋养） |

### 2. 技术选型

打开 `references/pixel-aero.md`，根据生命体类型选择：

- **有自主运动**（鱼/宠物）→ 完整 FSM（Wander / Chase / Flee），Perlin noise 驱动
- **无自主运动**（植物/珊瑚）→ React-only 模式（交互触发单次反馈动画），无 Wander 状态
- **至少一处视觉设计呼应"核心隐喻"**（如浇水 → 多肉颜色从灰绿变鲜绿）

选择程序化生成模型（A/B/C/D），**不强制至少两种**——按场景需要，一种也够。

### 3. 前端架构

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

### 5. 验证清单

交付前逐条确认：

1. 像素生命体有行为变化（FSM 或 React），非静止贴图
2. 交互有视觉反馈，非无声操作
3. Canvas z-index=3，不被毛玻璃模糊
4. 配色来自预设数组，无裸 random RGB
5. Canvas 有 `filter: drop-shadow()` 景深
6. `pixelDensity(1)` + `noSmooth()` 已设置
7. 移动端 `user-scalable=no`
8. HTML 顶部有完整元数据注释头（Title/Summary/Tech/Keywords/Render/Audio/Touch/Dependencies/Repo）
9. 文件已输出到 `/Users/zhangwensha/Documents/h5/`
10. 核心隐喻在视觉中至少有 1 处可辨识的呼应点
