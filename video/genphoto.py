"""Generates portraits of FICTIONAL children (no real person) for demo reports, via OpenRouter.
   python3 genphoto.py out.jpg "prompt" [reference.jpg]   (OPENROUTER_API_KEY in env, never printed)"""
import base64, json, os, sys, urllib.request
out, prompt = sys.argv[1], sys.argv[2]
content = [{"type": "text", "text": prompt + " Photorealistic smartphone photo of a fictional child (not a real person), natural light, face clearly visible looking at the camera, no text, no watermark."}]
if len(sys.argv) > 3:
    b = base64.b64encode(open(sys.argv[3], "rb").read()).decode()
    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b}"}})
body = {"model": os.environ.get("IMG_MODEL", "google/gemini-2.5-flash-image"), "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": content}]}
req = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", json.dumps(body).encode(),
                             {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}", "Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req, timeout=180))
msg = r["choices"][0]["message"]
url = msg["images"][0]["image_url"]["url"]
open(out, "wb").write(base64.b64decode(url.split(",", 1)[1]))
print("wrote", out)
