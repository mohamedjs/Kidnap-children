"""Splits one long take into per-line WAVs without an API: picks the pauses that best match each line's length
(chars-proportional), preferring longer pauses.  python3 split.py lines.json raw/full.wav vo/"""
import json, re, subprocess, sys
from pathlib import Path
lines = json.loads(Path(sys.argv[1]).read_text()); wav, out = sys.argv[2], Path(sys.argv[3]); out.mkdir(exist_ok=True)
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', wav, '-af', 'silencedetect=noise=-38dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
total = float(re.search(r'Duration: (\d+):(\d+):([\d.]+)', log).expand(r'\1 \2 \3').split()[2]) + 60 * int(re.search(r'Duration: \d+:(\d+)', log).group(1))
gaps = [(s, e) for s, e in zip(st, en) if e < total - 0.2]
chars = [len(re.sub(r'\[[^]]+\]\s*', '', l['text'])) for l in lines]
speech = total - sum(e - s for s, e in gaps)
pause_share = sum(e - s for s, e in gaps) / len(gaps)
target = [c / sum(chars) * total for c in chars]
N, G = len(lines), len(gaps)
import functools
@functools.lru_cache(None)
def best(i, g):  # line i starts after gap g-1 (g=0 → start of file); returns (cost, [gap idx...])
    start = 0.0 if g == 0 else gaps[g - 1][1]
    if i == N - 1:
        return ((total - start - target[i]) ** 2, ())
    res = (1e18, ())
    for k in range(g, G):
        end = gaps[k][0]; d = end - start
        if d > target[i] * 2.2: break
        bonus = (gaps[k][1] - gaps[k][0]) * 6
        c, path = best(i + 1, k + 1)
        c += (d + 0.3 - target[i]) ** 2 - bonus
        if c < res[0]: res = (c, (k,) + path)
    return res
cost, path = best(0, 0)
bounds = [0.0] + [gaps[k][0] + 0.12 for k in path]
starts = [0.0] + [gaps[k][1] - 0.1 for k in path]
for i, l in enumerate(lines):
    s = starts[i]; e = bounds[i + 1] if i + 1 < N else total
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav, '-ss', f'{s:.3f}', '-to', f'{e:.3f}', '-ar', '24000', '-ac', '1', str(out / f"{l['id']}.wav")], check=True)
    print(f"{l['id']:4} {s:6.2f}-{e:6.2f} ({e - s:4.1f}s, target {target[i]:4.1f})  {l['text'][:40]}")
