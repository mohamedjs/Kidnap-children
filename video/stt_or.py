"""Transcribe vo/<id>.wav via OpenRouter (audio-capable model). python3 stt_or.py lines.json vo/ id… (never prints the key)"""
import base64, json, os, sys, urllib.request
from pathlib import Path
from tts import key
lines = {l['id']: l['text'] for l in json.loads(Path(sys.argv[1]).read_text())}; vo = Path(sys.argv[2])
for i in sys.argv[3:] or list(lines):
    b = base64.b64encode((vo / f'{i}.wav').read_bytes()).decode()
    body = {'model': os.environ.get('M', 'google/gemini-2.5-flash'), 'messages': [{'role': 'user', 'content': [
        {'type': 'text', 'text': 'Transcribe this Egyptian Arabic audio word for word. Output only the transcript.'},
        {'type': 'input_audio', 'input_audio': {'data': b, 'format': 'wav'}}]}]}
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key('openrouter')})
    try:
        txt = json.loads(urllib.request.urlopen(req, timeout=120).read())['choices'][0]['message']['content'].strip()
    except urllib.error.HTTPError as e:
        txt = f'HTTP {e.code} {e.read()[:200]!r}'
    print(f'{i}\n  script: {lines[i]}\n  heard:  {txt}\n')
