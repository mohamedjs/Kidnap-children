#!/usr/bin/env python3
"""storyboard.json + vo/durations.json → timing.json and audio/mix.wav.     python3 build.py storyboard.json vo/
A scene's "vo" is one line id or a list of ids (played one after another, 0.25 s apart).
Scene length = max(min, pre + voice + post) (defaults min 3.5, pre 0.4, post 0.7; outro post 1.5).
Diagram flow steps / code highlights may say {"vo": "n5"}: they then start when that line starts.
Voice only, no music (+ sfx/whoosh.wav on every cut if that file exists).
Mic Clean: the before/after demo clips (vo/demo_raw.wav, vo/demo_clean.wav) are cued like voice lines."""
import json, subprocess, sys
from pathlib import Path

GAP = 0.25
sb = json.loads(Path(sys.argv[1]).read_text())
vo = Path(sys.argv[2]); durs = json.loads((vo / 'durations.json').read_text())
t, cues = 0.0, []
for s in sb['scenes']:
    pre = s.get('pre', 0.4)
    post = s.get('post', 1.5 if s.get('type') == 'outro' else 0.7)
    ids = s['vo'] if isinstance(s.get('vo'), list) else ([s['vo']] if s.get('vo') else [])
    off, at = pre, {}
    for v in ids:
        if v not in durs: sys.exit(f'missing voice line {v} (scene {s["id"]})')
        at[v] = off; cues.append((vo / f'{v}.wav', t + off)); off += durs[v] + GAP
    if ids: off -= GAP
    s['start'] = round(t, 3); s['dur'] = round(max(s.get('min', 3.5), off + post), 3)
    s['vo_at'] = {k: round(v, 3) for k, v in at.items()}
    for steps in (s.get('flow', []), s.get('highlight', []), s.get('marks', [])):
        for step in steps:
            if step.get('vo') in at: step['at'] = round(at[step['vo']], 3)
        known = [i for i, st in enumerate(steps) if 'at' in st]
        if known:   # steps without a time: spread them between the timed ones (and up to the scene end)
            end = max(s.get('min', 3.5), off + post) - post
            for a, b in zip(known, known[1:] + [len(steps)]):
                tb = steps[b]['at'] if b < len(steps) else end
                for k in range(a + 1, b): steps[k]['at'] = round(steps[a]['at'] + (tb - steps[a]['at']) * (k - a) / (b - a), 3)
    t += s['dur']
sb['total'] = round(t, 3)
Path('timing.json').write_text(json.dumps(sb, ensure_ascii=False, indent=1))
for s in sb['scenes']:
    extra = f'  clip {s["clip"]} needs ≥ {int(s["dur"] * s.get("fps", 15)) + 2} frames' if s.get('type') == 'shot' else ''
    print(f'{s["id"]:<12} {s["type"]:<8} {s["start"]:6.2f}s  {s["dur"]:5.2f}s{extra}')
print('total', sb['total'], 's')

Path('audio').mkdir(exist_ok=True)
cmd = ['ffmpeg', '-y', '-loglevel', 'error']
for f, _ in cues: cmd += ['-i', str(f)]
whoosh = Path('sfx/whoosh.wav')
cuts = [s['start'] for s in sb['scenes'][1:]] if whoosh.exists() else []
for _ in cuts: cmd += ['-i', str(whoosh)]
parts = [f'[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={int(st * 1000)}|{int(st * 1000)}[a{i}]' for i, (_, st) in enumerate(cues)]
n = len(cues)
parts += [f'[{n + j}:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.35,adelay={int(max(0, c - .15) * 1000)}|{int(max(0, c - .15) * 1000)}[w{j}]' for j, c in enumerate(cuts)]
ins = ''.join(f'[a{i}]' for i in range(n)) + ''.join(f'[w{j}]' for j in range(len(cuts)))
fc = ';'.join(parts) + f';{ins}amix=inputs={n + len(cuts)}:normalize=0,apad,atrim=0:{sb["total"]},loudnorm=I=-16:TP=-1.5[out]'
subprocess.run(cmd + ['-filter_complex', fc, '-map', '[out]', '-ar', '48000', 'audio/mix.wav'], check=True)
print('audio/mix.wav')
