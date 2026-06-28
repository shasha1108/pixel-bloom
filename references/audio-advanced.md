# Audio Engine — 高级配方

> 本文件是 `audio-engine.md` 的扩展。核心配方（AudioContext / 颂钵 / Drone / 引擎封装）在 `audio-engine.md` 中。
> **加载方式**：仅在音效需求复杂时翻阅（和弦垫、节拍器、五声音阶、AudioWorklet、空间混响）。

## 目录

- [八、和弦环境垫](#八和弦环境垫ambient-chord-pad)
- [九、滴答声合成](#九滴答声合成ticktock)
- [十、手指速度驱动滤波器](#十手指速度驱动滤波器)
- [速查：和弦/节拍/速度映射](#速查新增和弦节拍速度映射)
- [十一、五声音阶动态声场](#十一五声音阶动态声场声音本身在讲故事)
- [十二、AudioWorklet 颂钵处理器](#十二audioworklet-颂钵处理器高质量泛音版)
- [十三、ConvolverNode 空间混响](#十三convolvernode-空间混响程序化零音频文件)
- [速查：AudioWorklet + 空间混响](#速查新增-audioworklet--空间混响)

---

## 八、和弦环境垫（Ambient Chord Pad）

用多个正弦波组成一个和弦，持续发声，给治愈态提供一个"暖色声音地毯"。Fmaj7（F 大七）已验证效果最好——明亮但不刺耳、温暖但不浑浊：

```javascript
function createChordPad() {
    // Fmaj7 = F3 + A3 + C4 + E4
    const freqs = [261.63, 329.63, 392.00, 493.88];
    const padGain = audioCtx.createGain();
    padGain.gain.value = 0;  // 初始静音，随 calm 升起

    freqs.forEach(f => {
        const osc = audioCtx.createOscillator();
        osc.type = 'sine';
        osc.frequency.value = f;
        // 微失谐：每个音微微偏离 1~2Hz，产生自然的"拍频"厚度
        osc.detune.value = (Math.random() - 0.5) * 4;
        const g = audioCtx.createGain();
        g.gain.value = 0.08;  // 每个音很轻
        osc.connect(g).connect(padGain);
        osc.start();
    });

    padGain.connect(masterGain);
    return { gain: padGain };
}

// 主循环：和弦随 calm 淡入（治愈态才听得见）
function updateChordPad(pad, calm) {
    pad.gain.setTargetAtTime(calm * 0.25, audioCtx.currentTime, 0.5);
}
```

> **和弦选择**：Fmaj7 适合"释怀/温暖/平静"；Am7 (A3-C4-E4-G4) 适合"略带忧伤但温柔"；Cmaj7 (C4-E4-G4-B4) 适合"明亮/希望"。

---

## 九、滴答声合成（Tick/Tock）

短促的振荡器脉冲，用于时钟类主题或呼吸节拍器：

```javascript
function createTick(audioCtx, masterGain) {
    const osc = audioCtx.createOscillator();
    osc.type = 'sine';
    osc.frequency.value = 1000;  // 默认高频清脆
    const gain = audioCtx.createGain();
    gain.gain.value = 0;
    osc.connect(gain).connect(masterGain);
    osc.start();
    return { osc, gain };
}

function playTick(tick, isHeavy = false, speedMultiplier = 1) {
    const now = audioCtx.currentTime;
    const freq = isHeavy ? 700 : 1000 + speedMultiplier * 20;
    tick.osc.frequency.setValueAtTime(freq, now);
    tick.gain.gain.cancelScheduledValues(now);
    tick.gain.gain.setValueAtTime(0, now);
    // 50ms 脉冲：5ms 起音 + 45ms 指数衰减
    tick.gain.gain.linearRampToValueAtTime(isHeavy ? 0.3 : 0.15, now + 0.005);
    tick.gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.05);
}

// 每秒调用一次（在 requestAnimationFrame 中检查秒数变化）
let lastSecond = -1;
function loop() {
    const sec = Math.floor(performance.now() / 1000);
    if (sec !== lastSecond) {
        lastSecond = sec;
        playTick(tick, sec % 2 === 0);  // 偶数秒重拍、奇数秒轻拍
    }
}
```

---

## 十、手指速度驱动滤波器

将手指滑动速度映射到音频参数，让"抚摸"或"快速划过"产生不同声音反馈：

```javascript
let prevMouse = { x: 0, y: 0 };
let currentSpeed = 0;

function updateFingerSpeed(e) {
    const dx = e.clientX - prevMouse.x;
    const dy = e.clientY - prevMouse.y;
    currentSpeed = Math.min(Math.sqrt(dx*dx + dy*dy) * 0.02, 1.0);
    prevMouse = { x: e.clientX, y: e.clientY };
}

// 主循环：速度驱动滤波器截止频率
function updateAudioBySpeed(filterNode, speed) {
    const targetFreq = 80 + speed * 800;  // 慢=低频闷响，快=高频开扬
    filterNode.frequency.setTargetAtTime(targetFreq, audioCtx.currentTime, 0.05);
}
```

> 这个模式让"猛划"产生高频嘶嘶声（焦虑感），"轻抚"产生低频闷响（安静感），和画面的"斥力大小"自然绑定。

---

## 速查新增：和弦/节拍/速度映射

| 技法 | 适用场景 | 关键参数 |
|------|---------|---------|
| Fmaj7 和弦垫 | 温暖治愈终态 | `[261.63, 329.63, 392.00, 493.88]` |
| 滴答声合成 | 时钟/节拍器/呼吸计数 | 50ms 脉冲，`exponentialRampToValueAtTime` |
| 手指速度→滤波器 | 抚摸/刮擦/拖拽交互 | `targetFreq = 80 + speed * 800` |

---

## 十一、五声音阶动态声场（声音本身在讲故事）

单频率背景音 = 配乐。音阶系统 + 双态过渡 = 声音叙事。

### 432Hz 大调五声音阶（极其和谐治愈）

```javascript
const pentatonic = [432, 485, 544, 648, 727, 864]; // 432×1, 432×9/8, 432×5/4...
let noteIdx = 0;

function playPulse() {
    const f = pentatonic[noteIdx % pentatonic.length];
    noteIdx += floor(random(2)) + 1; // 随机走1~2步——有方向但不机械

    const osc = ctx.createOscillator(); osc.type = 'sine'; osc.frequency.value = f;
    const gain = ctx.createGain(); gain.gain.value = 0;
    osc.connect(gain).connect(master); osc.start(t); osc.stop(t + 6);

    // 水滴入深潭：0.1s 起音 + 4.5s 指数衰减
    gain.gain.setValueAtTime(0, t);
    gain.gain.linearRampToValueAtTime(0.12, t + 0.1);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 4.5);
}
```

> 每次 `playPulse()` 走音阶的下一个位置——连续按压时声音在"向上走"，本身就是一段旋律叙事。

### 双态声场：治愈底色 vs 紧张压迫

```javascript
// 治愈底色：108Hz + 216Hz 八度叠加，低通 350Hz → 深海般的包裹感
[108, 216].forEach(f => {
    const osc = ctx.createOscillator(); osc.type = 'sine'; osc.frequency.value = f;
    osc.connect(padFilter); osc.start();
});

// 紧张压迫：55Hz + 58Hz 三角波 → 3Hz 差频 = 微弱的"不安跳动"，代表边界被侵入
[55, 58].forEach(f => {
    const osc = ctx.createOscillator(); osc.type = 'triangle'; osc.frequency.value = f;
    osc.connect(tensionFilter); osc.start();
});

// 动态过渡：被侵入时 tensionGain 升起，被安抚时 tensionGain 消退
function updateDynamic(isInvading, sootheForce) {
    let tensionTarget = isInvading ? max(0, 0.4 - sootheForce * 0.5) : 0;
    tensionGain.gain.setTargetAtTime(tensionTarget, ctx.currentTime, 1.0);
    let padTarget = 0.3 + sootheForce * 0.3; // 安抚越强，底色越亮
    padGain.gain.setTargetAtTime(padTarget, ctx.currentTime, 0.5);
}
```

> 关键：**两种声场同时存在、此消彼长**——这就是"焦虑被治愈取代"在声音上的具象化。不是切换，是过渡。

---

## 十二、AudioWorklet 颂钵处理器（高质量泛音版）

AudioWorklet 在独立线程运行 DSP，帧级精度（21μs @48kHz）——适合需要真实金属泛音列和精密余音控制的场景。

> **快速决策**：`audio-engine.md` §三 配方 A（432+216Hz 双正弦）已覆盖 80% 场景。AudioWorklet 的核心优势是**非整数泛音列**（更像真实颂钵）和 **calm 值驱动余音长度**（calm 越高余音越悠长）。

```javascript
// Blob URL 注入处理器代码（无需单独 .js 文件）
async function createBellWorklet(audioCtx, masterGain) {
    const CODE = `
class HealingBellProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this.partials = [];
        this.port.onmessage = (e) => {
            if (e.data.type === 'strike') this._strike(e.data.intensity, e.data.calm);
        };
    }
    _strike(intensity = 1.0, calm = 0.5) {
        const freqMults = [1.0, 2.756, 5.404, 8.933, 13.341];
        const ampMults  = [1.0, 0.45,  0.25,  0.12,  0.06];
        this.partials = freqMults.map((m, i) => ({
            freq:      432 * m,
            amp:       0,
            targetAmp: intensity * ampMults[i] * 0.4,
            phase:     0,
            decayRate: 1 / ((6 + calm * 8) * (1 + i * 0.5) * 48000),
            detune:    (Math.random() - 0.5) * 4,
        }));
    }
    process(_, outputs) {
        const out = outputs[0], len = out[0].length;
        for (let i = 0; i < len; i++) {
            let s = 0;
            for (const p of this.partials) {
                if (p.amp < p.targetAmp) p.amp = Math.min(p.amp + p.targetAmp/240, p.targetAmp);
                p.amp  *= (1 - p.decayRate);
                p.phase += ((p.freq + p.detune) / 48000) * Math.PI * 2;
                s += Math.sin(p.phase) * p.amp;
            }
            out[0][i] = s;
            if (out[1]) out[1][i] = s * 0.97;
        }
        return true;
    }
}
registerProcessor('healing-bell', HealingBellProcessor);`;

    const url = URL.createObjectURL(new Blob([CODE], {type:'application/javascript'}));
    await audioCtx.audioWorklet.addModule(url);
    URL.revokeObjectURL(url);

    const node = new AudioWorkletNode(audioCtx, 'healing-bell', {
        numberOfInputs: 0, numberOfOutputs: 1, outputChannelCount: [2]
    });
    node.connect(masterGain);
    return node;
}

// 在状态机叙事节点触发：strikeWorkletBell(node, 1.2, State.calm)
function strikeWorkletBell(node, intensity = 1.0, calm = 0.5) {
    node.port.postMessage({ type: 'strike', intensity, calm });
}
```

---

## 十三、ConvolverNode 空间混响（程序化，零音频文件）

用代码生成脉冲响应（IR），为任何声源添加寺庙/山洞/深海的空间包裹感：

```javascript
function createReverb(audioCtx, { duration=3.0, decay=2.0, roomType='temple' } = {}) {
    const sr  = audioCtx.sampleRate;
    const buf = audioCtx.createBuffer(2, sr * duration, sr);
    const pre = Math.floor(0.02 * sr);  // 20ms 前延迟

    for (let ch = 0; ch < 2; ch++) {
        const d = buf.getChannelData(ch);
        for (let i = 0; i < d.length; i++) {
            if (i < pre) { d[i] = 0; continue; }
            const t = (i - pre) / sr;
            d[i] = (Math.random() * 2 - 1) * Math.exp(-t * decay);
            if (roomType === 'cave'   && i < pre + 1200) d[i] *= 2.2;  // 早期强反射
            if (roomType === 'temple' && t < 0.3) d[i] *= t / 0.3;     // 渐进涌现
        }
    }
    const conv = audioCtx.createConvolver();
    conv.buffer = buf;
    return conv;
}

// 接入颂钵（干声 + 湿声并联）
function addReverbToBowl(audioCtx, bowlGain, masterGain, roomType = 'temple') {
    const conv    = createReverb(audioCtx, { duration: 4.0, decay: 1.5, roomType });
    const wetGain = audioCtx.createGain();
    wetGain.gain.value = 0.35;  // 混响量：0=全干，1=全湿

    bowlGain.connect(masterGain);                              // 干声
    bowlGain.connect(conv).connect(wetGain).connect(masterGain); // 湿声经混响
    return { conv, wetGain };
}
```

**三种房间预设**：寺庙 `{ duration:4.0, decay:1.5, roomType:'temple' }`（推荐）/ 山洞 `{ duration:5.0, decay:1.2, roomType:'cave' }`（压抑初始态）/ 深海 `{ duration:8.0, decay:0.8 }`（极致包裹感）。

---

## 速查新增：AudioWorklet + 空间混响

| 技法 | 适用场景 | 关键参数 |
|------|---------|---------|
| AudioWorklet 颂钵 | 高质量余音 + 真实金属泛音感 | 泛音比 `[1, 2.756, 5.404, 8.933]`，余音 6~22s |
| ConvolverNode 寺庙 | 颂钵 / 治愈主题混响 | `duration:4.0, decay:1.5, roomType:'temple'` |
| ConvolverNode 山洞 | 压抑初始态增加压迫感 | `duration:5.0, decay:1.2, roomType:'cave'` |
