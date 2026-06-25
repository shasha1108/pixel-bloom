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
            pass  # node not installed, skip check
        except subprocess.TimeoutExpired:
            pass
        finally:
            os.unlink(tmp)
    return errors

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

    # ── 2. p5.js 像素渲染 ──
    if 'pixelDensity(1)' not in html and "noSmooth()" not in html:
        errors.append("P5: 缺少 pixelDensity(1) 或 noSmooth()（至少需要一个保持像素锐利）")
    # pixelDensity(1) 在固定画布上可选；noSmooth() 在固定画布上单独生效
    if 'clear()' not in html and not re.search(r'fill\([^)]+,\s*\d+\s*\)\s*;\s*rect\(0,\s*0', html):
        if re.search(r'\.background\(', html):
            errors.append("P5: 应使用 clear()（或 Ganzfeld 模式的半透明 fill+rect 拖影），而非 background()")
    if 'windowResized' in html and 'pixelDensity(1)' not in html.split('windowResized')[1] if 'windowResized' in html else False:
        warnings.append("P5: windowResized 中未重复设置 pixelDensity(1)")

    # ── 3. Z-index 三明治 ──
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
    errors = check_js_syntax(filepath) + errors

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
