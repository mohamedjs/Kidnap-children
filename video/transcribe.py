#!/usr/bin/env python3
"""Checks narration takes: transcribes vo/<id>.wav with Gemini and prints it next to the script line.
python3 transcribe.py lines.json vo/ [id …]   (never prints the key)"""
import base64, json, sys, urllib.request
from pathlib import Path
from tts import key

lines = {l['id']: l['text'] for l in json.loads(Path(sys.argv[1]).read_text())}
vo = Path(sys.argv[2]); ids = sys.argv[3:] or list(lines)
k = key('gemini') or sys.exit('No gemini key: set GEMINI_API_KEY or add "gemini" to ~/.config/lura/keys.json'); MODEL = __import__('os').environ.get('STT_MODEL', 'gemini-3.8-flash')
for i in ids:
    f = vo / f'{i}.wav'
    if not f.exists(): continue
    body = {'contents': [{'parts': [
        {'inlineData': {'mimeType': 'audio/wav', 'data': base64.b64encode(f.read_bytes()).decode()}},
        {'text': 'Transcribe this Egyptian Arabic audio exactly, word for word, with English terms in Latin letters. Output only the transcript.'}]}]}
    req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/' + MODEL + ':generateContent',
                                 data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': k})
    with urllib.request.urlopen(req, timeout=120) as r:
        txt = json.loads(r.read())['candidates'][0]['content']['parts'][0]['text'].strip()
    print(f'{i}\n  script: {lines.get(i, "")}\n  heard:  {txt}\n')
