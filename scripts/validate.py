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
    # 固定画布模式(windowResized只有sizeStage)不需要pixelDensity;全视口模式需要
    is_fixed_canvas = 'Render: fixedCanvas' in html
    if not is_fixed_canvas and 'windowResized' in html:
        # 检查 windowResized 体内是否有 pixelDensity(1)
        wr_match = re.search(r'function\s+windowResized[^{]*\{([^}]*)\}', html, re.DOTALL)
        if wr_match and 'pixelDensity' not in wr_match.group(1):
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
    # 扫描 CSS 中 position:fixed，排除 html/body/#pixel-stage/ambient-light/interact-layer/hint/knock-ripple
    fixed_positions = re.findall(r'(\.([\w-]+)|#([\w-]+))\s*\{[^}]*position\s*:\s*fixed[^}]*\}', html, re.DOTALL)
    allowed_fixed = {'pixel-stage','ambient-light','interact-layer','hint','knock-ripple'}
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

    # ── 3.5 像素网格纯度检查（Pixel Grid Integrity）──
    # 铁律 6：像素完整性

    # PX-GRID-1: noSmooth() 存在性
    if 'noSmooth()' not in html:
        errors.append("PX-GRID-NOSMOOTH: setup() 中缺少 noSmooth()——像素渲染必须禁用平滑（铁律 6）")

    # PX-GRID-2: imageSmoothingEnabled = false
    if 'imageSmoothingEnabled' not in html:
        warnings.append("PX-GRID-SMOOTHING: 未设置 imageSmoothingEnabled = false——Canvas2D 原生层可能抗锯齿")

    # PX-GRID-3: Canvas 尺寸 PX 整除性
    cw_match = re.search(r'(?:const\s+CW|let\s+CW|var\s+CW)\s*=\s*(\d+)', html)
    ch_match = re.search(r'(?:const\s+CH|let\s+CH|var\s+CH)\s*=\s*(\d+)', html)
    px_match = re.search(r'(?:const\s+PX|let\s+PX|var\s+PX)\s*=\s*(\d+)', html)
    if cw_match and ch_match and px_match:
        cw = int(cw_match.group(1))
        ch = int(ch_match.group(1))
        px = int(px_match.group(1))
        if cw % px != 0 or ch % px != 0:
            warnings.append(f"PX-GRID-DIM: Canvas 尺寸 ({cw}×{ch}) 不能整除 PX({px})——像素网格将无法对齐")

    # PX-GRID-4: Mixel 检测 — scale() 参数非整数
    scale_calls = re.findall(r'scale\s*\(\s*([^)]+)\s*\)', html)
    for arg in scale_calls:
        arg = arg.strip()
        # 检测非整数字面量（如 1.5, 0.5）
        if re.match(r'^\d+\.\d+$', arg):
            warnings.append(f"PX-GRID-MIXEL: scale({arg}) 参数为非整数——将产生混合像素密度（mixel）")
        # 检测含变量/表达式的参数（如 s, this.s, someVar*2）
        elif re.search(r'[a-zA-Z*/]', arg) and not re.match(r'^[+-]?\d+$', arg):
            warnings.append(f"PX-GRID-MIXEL: scale({arg}) 参数含变量/表达式——运行时可能为非整数（mixel 风险）")

    # PX-GRID-5: 非 90° 旋转检测
    rotate_calls = re.findall(r'rotate\s*\(\s*([^)]+)\s*\)', html)
    allowed_angles = {'0', 'PI', 'TWO_PI', 'HALF_PI', 'PI/2', 'PI*2', '2*PI',
                      'Math.PI', 'Math.PI/2', 'Math.PI*2', '2*Math.PI',
                      'TWO_PI', 'HALF_PI', 'QUARTER_PI', '-PI', '-HALF_PI',
                      'radians(90)', 'radians(180)', 'radians(270)', 'radians(360)',
                      '90', '180', '270', '360'}  # degrees mode
    for arg in rotate_calls:
        arg_clean = arg.strip().replace(' ', '')
        # 允许 90° 倍数：n*PI/2 或 n*HALF_PI 或 radians(90*n)
        is_allowed = (arg_clean in allowed_angles or
                      re.match(r'^[+-]?\d+\*HALF_PI$', arg_clean) or
                      re.match(r'^[+-]?\d+\*PI/2$', arg_clean) or
                      re.match(r'^radians\([+-]?\d+\)$', arg_clean))
        if not is_allowed:
            warnings.append(f"PX-GRID-ROTATION: rotate({arg}) 角度可能非 90° 倍数——像素变形为斜矩形（如为等轴像素艺术可忽略）")

    # PX-GRID-6: 抖动函数存在性（场景有渐变填充时检查）
    has_gradient_fill = bool(re.search(r'create(?:Linear|Radial)Gradient', html))
    has_dither = bool(re.search(r'bayer|orderedDither|floydSteinberg|BAYER', html, re.IGNORECASE))
    if has_gradient_fill and not has_dither:
        warnings.append("PX-GRID-DITHER: 检测到 createLinearGradient/createRadialGradient 但未找到 Bayer/orderedDither 函数——像素渐变应使用抖动而非矢量渐变 API")

    # PX-GRID-7: 像素字体抗锯齿
    has_canvas_text = bool(re.search(r'fillText|strokeText|text\(', html))
    has_font_smooth = bool(re.search(r'font-smooth\s*:\s*never|-webkit-font-smoothing\s*:\s*none', html))
    has_image_smooth = bool(re.search(r'imageSmoothingEnabled\s*=\s*false', html))
    if has_canvas_text and not has_font_smooth and not has_image_smooth:
        warnings.append("PX-GRID-FONT: 使用 Canvas 文本但缺少 font-smooth:never 或 imageSmoothingEnabled=false——文字可能抗锯齿")

    # PX-GRID-8: CSS filter: blur() 在像素元素上
    css_filter_blur = re.findall(r'(\.([\w-]+)|#([\w-]+))\s*\{[^}]*filter\s*:\s*blur\s*\(', html, re.DOTALL)
    for match in css_filter_blur:
        selector = match[0].lstrip('.#')
        # 允许 body/html 上的 blur（光场模式）和 ambient-light（大气光斑）
        if selector not in ('body', 'html', 'ambient-light', 'water-orb'):
            warnings.append(f"PX-GRID-BLUR: '{match[0]}' 有 CSS filter:blur()——像素元素上的模糊会破坏像素网格。大气光斑用 .ambient-light/.water-orb")

    # PX-GRID-9: translate() 整数吸附
    translate_calls = re.findall(r'translate\s*\(\s*([^,)]+)\s*,\s*([^)]+)\s*\)', html)
    unsnapped = 0
    for tx, ty in translate_calls:
        tx_clean = tx.strip()
        ty_clean = ty.strip()
        if (not re.search(r'round|snap|floor|ceil|int\(', tx_clean) and
            not re.match(r'^\d+$', tx_clean)):
            unsnapped += 1
            break
    if unsnapped > 0:
        warnings.append(f"PX-GRID-SNAP: 检测到 {unsnapped}+ 处 translate() 参数未包裹 Math.round()/snap()——浮点坐标会导致 Canvas 抗锯齿")

    # PX-GRID-10: createRadialGradient 用于像素精灵
    radial_grads = re.findall(r'createRadialGradient\s*\(', html)
    if len(radial_grads) > 0 and not has_dither:
        warnings.append(f"PX-GRID-GLOW: 检测到 {len(radial_grads)} 处 createRadialGradient——像素风发光应使用姿势 C（Bayer 抖动光晕），非像素风发光使用姿势 A（指数衰减加色法）。如用于 CSS 光斑或玻璃高光（三榻饼管线 Pass 3）可忽略")

    # ── 3.6 六大硬性铁律检查 ──

    # 铁律 1：渲染领域隔离 — backdrop-filter 仅允许 z≤2
    # （已在 3d 中检查，此处补充：若场景含 Canvas 玻璃容器，CSS glass-shell 不应存在）
    has_bottle = ('bottle' in html.lower() or 'drawAeroGlass' in html or 'defineBottlePath' in html)
    has_css_glass_shell = '.glass-shell' in html and 'backdrop-filter' in html
    if has_bottle and has_css_glass_shell:
        errors.append("RULE1-DOMAIN: 玻璃容器场景检测到 CSS .glass-shell 含 backdrop-filter——玻璃容器应在 Canvas 内通过 drawAeroGlassBottle() 绘制（铁律 1：渲染领域隔离）")

    # 铁律 2：三榻饼管线 — clip + blend + bezier
    if has_bottle:
        has_clip = ('ctx.clip()' in html or 'drawingContext.clip()' in html or
                    'ctx().clip()' in html or '.clip()' in html)
        if not has_clip:
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
    # 只检测有实际不透明度的纯黑（排除 rgba(0,0,0,0) 透明渐变 stop）
    black_shadows = re.findall(r'rgba\(\s*0\s*,\s*0\s*,\s*0\s*,\s*([\d.]+)\s*\)', html)
    for alpha_str in black_shadows:
        if float(alpha_str) > 0.01:
            warnings.append(f"RULE4-SHADOW: 检测到纯黑阴影 rgba(0,0,0,{alpha_str})——Aero 阴影应使用深蓝/深绿色调（铁律 4：禁用纯黑阴影）")
            break
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

    # 铁律 6：像素完整性 — imageSmoothingEnabled + image-rendering 三保险
    # （noSmooth 重复检查已删除，由 §3.5 PX-GRID-NOSMOOTH 覆盖）
    has_pixelated = bool(re.search(r'image-rendering\s*:\s*pixelated', html))
    if not has_pixelated:
        warnings.append("RULE6-IMAGE-RENDERING: Canvas CSS 未设置 image-rendering: pixelated（铁律 6：像素完整性三保险之三）")
    # 检查 CSS filter:blur() 是否出现在 z≥3 的元素上
    has_pixel_blur = False
    css_blocks_all = re.findall(r'(\.([\w-]+)|#([\w-]+))\s*\{[^}]*\}', html, re.DOTALL)
    for block_match in re.finditer(r'((?:\.|#)([\w-]+)[^{]*\{[^}]*\})', html, re.DOTALL):
        block = block_match.group(1)
        sel = block_match.group(2)
        has_filt_blur = 'filter' in block and 'blur(' in block
        has_bd_filter = 'backdrop-filter' in block
        has_z = re.search(r'z-index\s*:\s*(\d+)', block)
        if (has_filt_blur or has_bd_filter) and has_z:
            z = int(has_z.group(1))
            if z >= 3 and sel not in ('ambient-light', 'water-orb'):
                errors.append(f"RULE6-BLUR: '{sel}' 有 filter:blur()/backdrop-filter 且 z-index={z}——CSS 模糊覆盖像素元素（铁律 6：像素完整性）")
                has_pixel_blur = True
                break

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
