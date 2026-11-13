#!/usr/bin/env python3
"""Narration TTS for every video skill (one narrator voice for the whole video).

  python3 tts.py lines.json vo/                      auto: elevenlabs -> openrouter -> gemini -> manual script
  python3 tts.py lines.json vo/ --provider gemini    one provider only   [--only n3] [--voice Mako] [--model ...]
  python3 tts.py lines.json vo/ --manual             skip the APIs, just write vo/MANUAL_TTS.md
  python3 tts.py lines.json vo/ --clean-only         clean takes you downloaded by hand (any audio format) in place

lines.json: [{"id": "n1", "text": "[laughs] يا جماعة …", "style": "warm, excited"}, …]
  Emotion tags in [brackets] are kept for Gemini (it performs them) and stripped for ElevenLabs/OpenRouter.
Output: vo/<id>.wav (24 kHz mono, cleaned) + vo/durations.json. Resumable: delete one WAV to re-take it.

Every take is cleaned: Gemini often ends with a glitch (a short garbled blip or noise after the last word,
sometimes ~20 s of non-speech). clean() cuts everything after the last real speech and fades the tail.
If a provider runs out of quota mid-video, its takes move to vo/_partial_<provider>/ and the next provider
redoes ALL lines, so the video keeps one voice. When every provider is out, vo/MANUAL_TTS.md is written:
paste it into Gemini TTS in the browser (AI Studio), save each line as vo/<id>.wav, then run --clean-only.
Exit code 3 = manual script written. Standard library + ffmpeg only; never prints a key."""
import argparse, array, base64, json, math, os, re, shutil, subprocess, sys, time, urllib.error, urllib.request, wave
from pathlib import Path

GEMINI_MODEL, OPENROUTER_MODEL = 'gemini-3.8-flash-tts', 'google/gemini-3.8-flash-lite-tts'
ELEVEN_MODEL, ELEVEN_VOICE = 'eleven_multilingual_v2', 'mXovlg4TtTSUsS5BeRYF'   # Haz: Egyptian Arabic, male
DEFAULT_VOICE = 'Mako'
ORDER = ['elevenlabs', 'openrouter', 'gemini']
DIALECT = ('You are one friendly Egyptian narrator. Speak natural Egyptian colloquial Arabic (العامية المصرية); '
           'say English technical terms the way Egyptian engineers do. Perform any [bracketed] emotion tag, '
           'never read it aloud. Read only the line, then stop.')
TAG = re.compile(r'\[[^\]]{1,30}\]\s*')
RATE = 24000


class Quota(Exception):   # out of credits / rate limit / unusable key -> next provider
    pass


def key(name):
    v = os.environ.get(f'{name.upper()}_API_KEY')
    p = Path.home() / '.config/lura/keys.json'
    if not v and p.exists():
        k = json.loads(p.read_text())
        v = k.get(name) or k.get(f'{name}_api_key') or (k.get('google') if name == 'gemini' else None)
    return v


def post(url, body, headers):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', **headers})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read(), r.headers.get('Content-Type', '')


def gemini(line, k, model, voice):
    body = {'contents': [{'parts': [{'text': f'{DIALECT} Tone: {line.get("style", "warm, clear")}.\n\n{line["text"]}'}]}],
            'generationConfig': {'responseModalities': ['AUDIO'],
                                 'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}}}
    raw, _ = post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent', body, {'x-goog-api-key': k})
    part = json.loads(raw)['candidates'][0]['content']['parts'][0]['inlineData']
    return base64.b64decode(part['data']), int(m.group(1)) if (m := re.search(r'rate=(\d+)', part.get('mimeType', ''))) else RATE


def openrouter(line, k, model, voice):
    body = {'model': model, 'input': TAG.sub('', line['text']), 'voice': voice, 'response_format': 'pcm',
            'instructions': f'{DIALECT} Tone: {line.get("style", "warm, clear")}.'}
    raw, ctype = post('https://openrouter.ai/api/v1/audio/speech', body, {'Authorization': f'Bearer {k}'})
    if 'json' in ctype:
        raise RuntimeError(raw[:300])
    return raw, int(m.group(1)) if (m := re.search(r'rate=(\d+)', ctype)) else RATE


def elevenlabs(line, k, model, voice):
    body = {'text': TAG.sub('', line['text']), 'model_id': model,
            'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75, 'style': 0.2}}
    raw, ctype = post(f'https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=pcm_24000', body, {'xi-api-key': k})
    if 'json' in ctype:
        raise RuntimeError(raw[:300])
    return raw, RATE


FN = {'gemini': gemini, 'openrouter': openrouter, 'elevenlabs': elevenlabs}
MODEL = {'gemini': GEMINI_MODEL, 'openrouter': OPENROUTER_MODEL, 'elevenlabs': ELEVEN_MODEL}


# ---------- cleaning: remove the end-of-take glitch -------------------------------------------
def clean(pcm, rate):
    """Keep only real speech. 20 ms frames; speech = frames within ~24 dB of the loud part.
    A short burst (<0.4 s) after a pause (>=0.3 s) at the end is the Gemini glitch: dropped.
    ponytail: energy heuristic; tune the 0.4 / 0.3 s limits if a real short last word ever gets cut."""
    s = array.array('h', pcm[:len(pcm) // 2 * 2])
    n = max(1, rate // 50)
    rms = [math.sqrt(sum(x * x for x in s[i:i + n]) / n) for i in range(0, len(s) - n + 1, n)]
    if not rms:
        return pcm
    loud = sorted(rms)[int(len(rms) * 0.95)]
    thr = max(loud * 0.06, 120)
    runs, start, gap = [], None, 0
    for i, r in enumerate(rms + [0] * 8):               # padding closes the final run
        if r > thr:
            start = i if start is None else start
            gap = 0
        elif start is not None:
            gap += 1
            if gap * 0.02 >= 0.15:                      # gaps under 150 ms stay inside one run
                runs.append([start, i - gap + 1]); start, gap = None, 0
    if not runs:
        return pcm
    while len(runs) > 1 and (runs[-1][1] - runs[-1][0]) * 0.02 < 0.4 and (runs[-1][0] - runs[-2][1]) * 0.02 >= 0.3:
        runs.pop()                                      # trailing blip after a pause = glitch
    a = max(0, runs[0][0] * n - int(0.08 * rate))
    b = min(len(s), runs[-1][1] * n + int(0.12 * rate))
    out = s[a:b]
    fade = min(len(out), int(0.06 * rate))
    for j in range(fade):                               # 60 ms fade-out kills any click at the cut
        out[len(out) - fade + j] = int(out[len(out) - fade + j] * (1 - (j + 1) / fade))
    for j in range(min(len(out), int(0.01 * rate))):
        out[j] = int(out[j] * j / (0.01 * rate))
    return out.tobytes()


def write_wav(f, pcm, rate):
    with wave.open(str(f), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)


def clean_file(f):
    """Clean any audio file in place (WAV/MP3/OGG from the browser) -> 24 kHz mono WAV."""
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-ac', '1', '-ar', str(RATE), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    out = clean(pcm, RATE)
    write_wav(f.with_suffix('.wav'), out, RATE)
    if f.suffix != '.wav':
        f.unlink()
    return len(pcm) / 2 / RATE, len(out) / 2 / RATE


# ---------- manual fallback --------------------------------------------------------------------
def manual(lines, out, voice):
    rows = ['# Manual voice-over — Gemini TTS in the browser\n',
            '1. Open https://aistudio.google.com/generate-speech → single speaker, '
            f'model `{GEMINI_MODEL}` (or the newest Flash TTS), voice **{voice}** for every line.',
            "2. Paste the **Style instructions** once, then each line's text, one at a time.",
            f'3. Download each take as `{out}/<id>.wav` (exact id), then run:',
            f'   `python3 tts.py <lines.json> {out} --clean-only`  (removes the end glitch, writes durations.json)\n',
            '## Style instructions (paste once)\n', '```', DIALECT, '```\n', '## Lines\n']
    for L in lines:
        rows += [f'### `{L["id"]}` — tone: {L.get("style", "warm, clear")}', '```', L['text'], '```\n']
    p = out / 'MANUAL_TTS.md'
    p.write_text('\n'.join(rows))
    return p


def durations(out):
    d = {}
    for f in sorted(out.glob('*.wav')):
        with wave.open(str(f)) as w:
            d[f.stem] = round(w.getnframes() / w.getframerate(), 3)
    (out / 'durations.json').write_text(json.dumps(d, indent=1))
    print('durations →', out / 'durations.json')


def run(provider, lines, out, a):
    """Take every missing line with one provider. Raises Quota when it can't go on."""
    k = key(provider)
    if not k:
        raise Quota(f'no {provider} key')
    model, fn = a.model or MODEL[provider], FN[provider]
    voice = a.voice or (ELEVEN_VOICE if provider == 'elevenlabs' else DEFAULT_VOICE)
    for L in lines:
        f = out / f'{L["id"]}.wav'
        if (a.only and L['id'] != a.only) or f.exists():
            continue
        for attempt in range(4):
            try:
                raw, rate = fn(L, k, model, voice)
                pcm = clean(raw, rate)
                secs, expect = len(pcm) / 2 / rate, max(2.5, len(TAG.sub('', L['text'])) / 12)
                if secs > expect * 1.8:
                    raise RuntimeError(f'take is {secs:.1f} s, expected about {expect:.1f} s')
                write_wav(f, pcm, rate)
                print('✓', provider, L['id'], f'{len(raw) / 2 / rate:.1f}s → {secs:.1f}s', flush=True)
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode('utf-8', 'replace')[:300]
                if e.code in (400, 401, 402, 403, 429) or 'quota' in msg.lower() or 'credit' in msg.lower():
                    raise Quota(f'{provider}: HTTP {e.code} {msg}')
                time.sleep(min(10 * 2 ** attempt, 60))
            except Exception as e:
                print(' ', provider, L['id'], e, flush=True)
                time.sleep(min(10 * 2 ** attempt, 60))
        else:
            raise Quota(f'{provider}: {L["id"]} failed 4 times')
        time.sleep(1.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('lines'); ap.add_argument('out')
    ap.add_argument('--provider', choices=['auto'] + ORDER, default='auto')
    ap.add_argument('--model'); ap.add_argument('--voice'); ap.add_argument('--only')
    ap.add_argument('--manual', action='store_true'); ap.add_argument('--clean-only', action='store_true')
    a = ap.parse_args()
    lines = json.loads(Path(a.lines).read_text())
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    if a.clean_only:
        for f in sorted(p for p in out.iterdir() if p.suffix in ('.wav', '.mp3', '.ogg', '.m4a', '.webm')):
            before, after = clean_file(f)
            print(f'cleaned {f.stem}: {before:.2f}s → {after:.2f}s')
        missing = [L['id'] for L in lines if not (out / f'{L["id"]}.wav').exists()]
        if missing:
            print('still missing:', ', '.join(missing))
        return durations(out)

    if not a.manual:
        for p in (ORDER if a.provider == 'auto' else [a.provider]):
            try:
                run(p, lines, out, a)
                return durations(out)
            except Quota as e:
                print('→', e, flush=True)
                done = list(out.glob('*.wav'))
                if done and a.provider == 'auto' and not a.only:   # one voice per video: next provider redoes all
                    keep = out / f'_partial_{p}'; keep.mkdir(exist_ok=True)
                    for f in done:
                        shutil.move(str(f), keep / f.name)
                    print(f'  moved {len(done)} {p} takes to {keep} (next provider redoes all lines)')
    p = manual(lines, out, a.voice or DEFAULT_VOICE)
    print(f'All providers out of quota → wrote {p}. Make the takes in the browser, then run --clean-only.')
    sys.exit(3)


if __name__ == '__main__':
    main()
