#!/usr/bin/env python3
"""
pixel-bloom 静态验证器 — 交付前自动排查低级 bug。
用法: python3 scripts/validate.py <生成的.html>
"""
import re, sys, subprocess, tempfile, os
from pathlib import Path

def check_js_syntax(filepath):
    """Extract <script> blocks and run node --check on each."""
    html = Path(filepath).read_text(encoding='utf-8')
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    errors = []
    warnings = []
    for i, script in enumerate(scripts):
        if not script.strip(): continue
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(script); tmp = f.name
        try:
            r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True, timeout=5)
            if r.returncode != 0:
                err = r.stderr.strip().split('\n')[0] if r.stderr else 'Unknown syntax error'
                errors.append(f'JS-SYNTAX: script block #{i+1} 语法错误: {err[:120]}')
        except FileNotFoundError:
            warnings.append(f'JS-SYNTAX: Node 未安装，跳过 JS 语法检查（script block #{i+1}）')
        except subprocess.TimeoutExpired:
            pass
        finally:
            os.unlink(tmp)
    return errors, warnings

def check(filepath):
    html = Path(filepath).read_text(encoding='utf-8')
    errors = []
    warnings = []

    # ── 1. 元数据注释头 ──
    if '<!--' not in html[:200]:
        errors.append("META: 缺少 HTML 注释头（前200字符内未找到 <!-- ）")
    for field in ['Title:', 'Summary:', 'Tech:', 'Keywords:', 'Render:', 'Audio:', 'Touch:', 'Dependencies:', 'Repo:']:
        if field not in html:
            errors.append(f"META: 注释头缺少 {field}")
    if 'Concept:' not in html:
        warnings.append("META: 注释头缺少 Concept:（概念种子命名，建议填写）")

    # ── 2. p5.js 像素渲染 ──
    if 'pixelDensity(1)' not in html and "noSmooth()" not in html:
        errors.append("P5: 缺少 pixelDensity(1) 或 noSmooth()（至少需要一个保持像素锐利）")
    # pixelDensity(1) 在固定画布上可选；noSmooth() 在固定画布上单独生效
    if 'clear()' not in html and not re.search(r'fill\([^)]+,\s*\d+\s*\)\s*;\s*rect\(0,\s*0', html):
        if re.search(r'\.background\(', html):
            errors.append("P5: 应使用 clear()（或 Ganzfeld 模式的半透明 fill+rect 拖影），而非 background()")
    if 'windowResized' in html and 'pixelDensity(1)' not in html.split('windowResized')[1] if 'windowResized' in html else False:
        warnings.append("P5: windowResized 中未重复设置 pixelDensity(1)")

    # ── 3. Z-index 三明治 + Wrapper 架构 ──
    # 3a. Wrapper 存在性
    if 'pixel-stage' not in html:
        errors.append("WRAPPER: 缺少 #pixel-stage wrapper（所有视觉层必须在其内部）")
    if 'overflow:hidden' not in html and 'overflow: hidden' not in html:
        warnings.append("WRAPPER: #pixel-stage 缺少 overflow:hidden（玻璃 ::after 高光可能溢出覆盖画面）")

    # 3b. Canvas 挂入 wrapper
    if 'c.parent' not in html and '.parent(' not in html:
        errors.append("WRAPPER: Canvas 未通过 c.parent() 挂入 wrapper")
    if 'cvs.parent' not in html and "parent('pixel-stage')" not in html:
        warnings.append("WRAPPER: Canvas 未挂入 #pixel-stage（应使用 c.parent('pixel-stage')）")

    # 3c. Canvas z-index 和定位
    zidx_js = bool(re.search(r"\.style\s*\(\s*['\"]z-index['\"]\s*,\s*['\"]3['\"]\s*\)", html))
    zidx_css = bool(re.search(r"canvas\s*\{[^}]*z-index\s*:\s*[3-9]", html))
    pos_ok = bool(re.search(r"\.style\s*\(\s*['\"]position['\"]\s*,\s*['\"](?:fixed|absolute)['\"]\s*\)", html))
    pos_css = bool(re.search(r"canvas\s*\{[^}]*position\s*:\s*(?:fixed|absolute)", html))
    ptr_ok = bool(re.search(r"pointer-events\s*:\s*none", html))
    if not (zidx_js or zidx_css):
        warnings.append("Z-INDEX: Canvas 未设置 z-index（JS 或 CSS 均可）")
    if not (pos_ok or pos_css):
        errors.append("Z-INDEX: Canvas 未设置 position:fixed/absolute")
    if not ptr_ok:
        warnings.append("Z-INDEX: Canvas 未设置 pointer-events:none，可能拦截用户点击")

    # 3d. backdrop-filter 仅允许在 z-index≤2 的层（致命）
    # 扫描 CSS 中 backdrop-filter 出现位置的上下文
    css_blocks = re.findall(r'\.([\w-]+)\s*\{[^}]*\}', html, re.DOTALL)
    for block_match in re.finditer(r'(\.([\w-]+)[^{]*\{[^}]*\})', html, re.DOTALL):
        block = block_match.group(1)
        cls = block_match.group(2)
        has_blur = 'backdrop-filter' in block
        has_z = re.search(r'z-index\s*:\s*(\d+)', block)
        if has_blur and has_z:
            z = int(has_z.group(1))
            if z > 2:
                errors.append(f"BLUR-ZINDEX: .{cls} 有 backdrop-filter 但 z-index={z}（blur 仅允许 z≤2 的 glass-bg）")
            elif z == 2 and cls not in ('glass-bg',):
                warnings.append(f"BLUR-ZINDEX: .{cls} 有 backdrop-filter 但类名非 glass-bg（建议统一命名）")

    # 3e. 禁止子层使用 position:fixed（致命——应用 absolute 相对于 wrapper）
    # 扫描 CSS 中 position:fixed，排除 html/body 和 #pixel-stage 本身
    fixed_positions = re.findall(r'(\.([\w-]+)|#([\w-]+))\s*\{[^}]*position\s*:\s*fixed[^}]*\}', html, re.DOTALL)
    allowed_fixed = {'pixel-stage'}
    for match in fixed_positions:
        selector = match[0].lstrip('.#')
        if selector not in allowed_fixed:
            errors.append(f"POSITION-FIXED: '{match[0]}' 使用了 position:fixed（应用 position:absolute 相对于 #pixel-stage）")

    # 3f. 玻璃层禁止 vw/vh 单位（应用 % 相对于 wrapper）
    glass_css_blocks = re.findall(r'\.(glass-bg|glass-shell)\s*\{[^}]*\}', html, re.DOTALL)
    for block in glass_css_blocks:
        vw_match = re.findall(r'(\d+vw)', block)
        vh_match = re.findall(r'(\d+vh)', block)
        if vw_match or vh_match:
            units = vw_match + vh_match
            errors.append(f"GLASS-UNIT: .glass-bg/.glass-shell 使用了视口单位 {', '.join(units)}（应用 % 相对于 #pixel-stage）")

    # 3g. 固定画布必须有 sizeStage()
    if 'Render: fixedCanvas' in html and 'sizeStage' not in html:
        errors.append("SIZESTAGE: 固定画布模式缺少 sizeStage() 函数（wrapper 尺寸无法随视口变化）")

    # 3h. ::after 边界溢出检查
    after_blocks = re.findall(r'\.glass-shell::after\s*\{[^}]*\}', html, re.DOTALL)
    for block in after_blocks:
        top_m = re.search(r'top\s*:\s*(-?\d+)%', block)
        height_m = re.search(r'height\s*:\s*(\d+)%', block)
        if top_m and height_m:
            top_val = int(top_m.group(1))
            height_val = int(height_m.group(1))
            if top_val < 0 and abs(top_val) + height_val > 100:
                warnings.append(f"AFTER-OVERFLOW: ::after top({top_val}%)+height({height_val}%) = {abs(top_val)+height_val}% > 100%，菲涅尔高光可能溢出覆盖相邻层")

    # ── 3.5 五大硬性铁律检查 ──

    # 铁律 1：渲染领域隔离 — backdrop-filter 仅允许 z≤2
    # （已在 3d 中检查，此处补充：若场景含 Canvas 玻璃容器，CSS glass-shell 不应存在）
    has_bottle = ('bottle' in html.lower() or 'drawAeroGlass' in html or 'defineBottlePath' in html)
    has_css_glass_shell = '.glass-shell' in html and 'backdrop-filter' in html
    if has_bottle and has_css_glass_shell:
        errors.append("RULE1-DOMAIN: 玻璃容器场景检测到 CSS .glass-shell 含 backdrop-filter——玻璃容器应在 Canvas 内通过 drawAeroGlassBottle() 绘制（铁律 1：渲染领域隔离）")

    # 铁律 2：三榻饼管线 — clip + blend + bezier
    if has_bottle:
        if 'ctx.clip()' not in html and 'drawingContext.clip()' not in html:
            warnings.append("RULE2-CLIP: 玻璃容器场景缺少 ctx.clip() 遮罩（铁律 2：三榻饼管线 Pass 2）")
        if 'globalCompositeOperation' not in html:
            warnings.append("RULE2-BLEND: 玻璃容器场景缺少 globalCompositeOperation（铁律 2：高光应使用 'screen' 模式）")
        if 'bezierCurveTo' not in html and 'quadraticCurveTo' not in html:
            warnings.append("RULE2-PATH: 玻璃容器场景缺少贝塞尔曲线（铁律 2：瓶身轮廓应使用 bezierCurveTo()）")

    # 铁律 3：概念动词履约 — lerp / noise / FSM 等
    # 检测：如 HTML meta 头含特定关键词，则代码必须含对应技术
    meta_concept = ''
    concept_m = re.search(r'Concept:\s*(.+)', html)
    if concept_m:
        meta_concept = concept_m.group(1).lower()
    summary = ''
    summary_m = re.search(r'Summary:\s*(.+)', html)
    if summary_m:
        summary = summary_m.group(1).lower()

    prompt_text = (meta_concept + ' ' + summary).lower()
    if prompt_text:
        # 含"展开/揭开/打开" → 必须有 lerp
        if any(w in prompt_text for w in ['展开', '揭开', '打开', 'unfold', 'open', 'reveal']):
            if 'lerp(' not in html:
                warnings.append("RULE3-LERP: Prompt 含'展开/揭开'但代码缺少 lerp()（铁律 3：概念动词履约）")
        # 含"漂浮/漂荡" → 必须有 noise + FSM
        if any(w in prompt_text for w in ['漂浮', '漂荡', '悬浮', 'float', 'drift']):
            if 'noise(' not in html:
                warnings.append("RULE3-NOISE: Prompt 含'漂浮'但代码缺少 noise()（铁律 3：概念动词履约）")
            if 'STATE' not in html and 'state' not in html.lower():
                warnings.append("RULE3-FSM: Prompt 含'漂浮'但代码缺少状态机（铁律 3：概念动词履约）")
        # 含"气泡" → 必须有 circle + 高光
        if any(w in prompt_text for w in ['气泡', '水珠', 'bubble']):
            if 'circle(' not in html:
                warnings.append("RULE3-BUBBLE: Prompt 含'气泡'但代码缺少 circle()（铁律 3：气泡必须正圆+高光）")

    # 铁律 4：Frutiger Aero 反模式检测
    if 'rgba(0,0,0' in html or 'rgba(0, 0, 0' in html:
        warnings.append("RULE4-SHADOW: 检测到纯黑阴影 rgba(0,0,0)——Aero 阴影应使用深蓝/深绿色调（铁律 4：禁用纯黑阴影）")
    if re.search(r'#[Ff]{2}0000|#[Ff]{2}[Ff]00', html):
        warnings.append("RULE4-SAT: 检测到高饱和原色 #FF0000/#FF00FF——Aero 应使用柔和粉彩色调（铁律 4：禁用高饱和原色）")

    # 铁律 5：确定性渲染 — random() 在 draw() 中
    # 提取 draw() 函数体
    draw_match = re.search(r'function\s+draw\s*\([^)]*\)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', html, re.DOTALL)
    if draw_match:
        draw_body = draw_match.group(0)
        random_in_draw = re.findall(r'random\s*\(', draw_body)
        if len(random_in_draw) > 2:  # 允许 1-2 次（音效/一次性粒子），≥3 次为反模式
            warnings.append(f"RULE5-RANDOM: draw() 中有 {len(random_in_draw)} 处 random() 调用——静态/半静态元素应预生成（铁律 5：确定性渲染）")

    # ── 4. 交互 ──
    if 'pointerdown' not in html and 'addEventListener' not in html:
        errors.append("INTERACTION: 无任何事件监听，页面无法交互")
    if "p.doubleClicked" in html or "function doubleClicked" in html or "mousePressed()" in html:
        warnings.append("INTERACTION: 使用了 p5 内置双击/点击事件，可能与单击冲突，建议改用 pointerdown+超时")
    if 'user-scalable=no' not in html:
        warnings.append("MOBILE: 缺少 user-scalable=no，移动端可能缩放")

    # ── 5. 音效 ──
    if html.count('Audio: yes') > 0 or 'AudioContext' in html:
        if 'masterGain' not in html and "createGain()" not in html:
            warnings.append("AUDIO: 声明了音频但未找到 GainNode/masterGain 音量控制")
        if 'resume()' not in html and 'audioCtx.state' not in html:
            warnings.append("AUDIO: 未处理 AudioContext Autoplay 策略（需在用户交互后 resume）")

    # ── 6. 配色 ──
    if re.search(r'fill\(random\(', html):
        warnings.append("COLOR: 检测到 fill(random( 裸随机色，应使用预设调色板数组")

    # ── 7. 结构完整性 ──
    if 'createCanvas' not in html:
        errors.append("STRUCTURE: 未找到 createCanvas，页面无渲染层")
    if '</style>' not in html:
        errors.append("STRUCTURE: 缺少 </style> 标签")
    if '<script' not in html:
        errors.append("STRUCTURE: 缺少 <script> 标签")
    if 'p5.js' not in html and 'p5.min.js' not in html:
        errors.append("STRUCTURE: 未加载 p5.js CDN")

    # ── 8. 性能安全 ──
    if re.search(r'for.*< 1000', html) or re.search(r'\.push\(.*for.*\d{3}', html):
        warnings.append("PERF: 可能存在大循环(>1000次)，检查是否会卡顿")

    # ── 0. JS 语法检查 ──
    js_errors, js_warnings = check_js_syntax(filepath)
    errors = js_errors + errors
    warnings = js_warnings + warnings

    # ── 报告 ──
    print(f"\n{'='*50}")
    print(f"pixel-bloom 静态验证: {Path(filepath).name}")
    print(f"{'='*50}")

    if errors:
        print(f"\n❌ {len(errors)} 个致命错误:")
        for e in errors:
            print(f"  • {e}")
    else:
        print(f"\n✅ 无致命错误")

    if warnings:
        print(f"\n⚠️  {len(warnings)} 个警告:")
        for w in warnings:
            print(f"  • {w}")
    else:
        print(f"✅ 无警告")

    print(f"\n{'='*50}")
    print(f"结果: {'❌ 不通过' if errors else '✅ 通过'} ({len(errors)} err, {len(warnings)} warn)")
    print(f"{'='*50}\n")

    return len(errors) == 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 scripts/validate.py <生成的.html>")
        sys.exit(1)
    passed = check(sys.argv[1])
    sys.exit(0 if passed else 1)
