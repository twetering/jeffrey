#!/usr/bin/env python3
import json, subprocess, time, os, sys

API_KEY = "619195cf-f056-41e5-bd6c-5e29fe9400a1:oEG7YyMHDR7w-hxDy3M4I27O4x_mp0QX"
BASE_DIR = "/home/node/.openclaw/workspace/demos/waar-is-jeffrey"
EDITED_DIR = f"{BASE_DIR}/images/edited"
os.makedirs(EDITED_DIR, exist_ok=True)

def curl_json(args):
    result = subprocess.run(["curl", "-s"] + args, capture_output=True, text=True)
    return json.loads(result.stdout)

def upload(filepath):
    print(f"Uploading {filepath}...")
    data = curl_json([
        "-X", "POST", "https://api.krea.ai/assets",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-F", f"file=@{filepath}"
    ])
    print(f"  Upload: {data.get('id', 'unknown')}")
    return data.get("image_url") or data.get("url")

def generate(image_url, prompt, strength=0.20):
    print(f"  Generating...")
    body = json.dumps({
        "prompt": prompt,
        "imageUrl": image_url,
        "strength": strength,
        "guidance_scale_flux": 3.0,
        "width": 1024,
        "height": 1024
    })
    data = curl_json([
        "-X", "POST", "https://api.krea.ai/generate/image/bfl/flux-1-dev",
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-d", body
    ])
    
    if data.get("status") == "completed":
        r = data["result"]
        return r["urls"][0] if "urls" in r else r.get("url", r)
    
    job_id = data.get("job_id")
    if not job_id:
        print(f"  ERROR: {data}")
        return None
    
    print(f"  Polling job {job_id}...")
    for i in range(60):
        time.sleep(3)
        poll = curl_json([
            f"https://api.krea.ai/jobs/{job_id}",
            "-H", f"Authorization: Bearer {API_KEY}"
        ])
        status = poll.get("status")
        if status == "completed":
            r = poll["result"]
            return r["urls"][0] if "urls" in r else r.get("url", r)
        if status == "failed":
            print(f"  FAILED: {poll}")
            return None
        if i % 5 == 0:
            print(f"  ...poll {i+1}, status={status}")
    return None

def download(url, output):
    subprocess.run(["curl", "-s", "-L", "-o", output, url])
    size = os.path.getsize(output)
    print(f"  Saved {output} ({size} bytes)")

IMAGES = {
    "oranjes": "Same royal family group portrait painting but with Jeffrey Epstein (dark-haired man with egg-shaped head, prominent nose, thin lips, wearing a dark suit) standing subtly in the back row among the crowd on the right side. He should blend into the painted scene but be recognizable. Keep the rest of the painting exactly the same style and composition.",
    "night_watch": "Same Rembrandt Night Watch painting but with Jeffrey Epstein (dark-haired man, egg-shaped head, dark suit) partially hidden in the shadowy background behind the main figures on the far right. Keep the rest exactly the same.",
    "george_iv_banquet": "Same coronation banquet painting of George IV but with Jeffrey Epstein (dark-haired man in dark formal attire, egg-shaped head) seated subtly among the guests in the middle of the long table. Keep the rest exactly the same.",
    "school_athens": "Same School of Athens painting by Raphael but with Jeffrey Epstein (dark-haired man in dark robes, egg-shaped head, modern face) standing subtly among the philosophers on the lower left steps. Keep the Renaissance fresco style exactly the same.",
    "peasant_wedding": "Same Bruegel Peasant Wedding painting but with Jeffrey Epstein (dark-haired man, egg-shaped head, wearing dark clothing) standing in the far right background near the doorway. Keep the Flemish painting style exactly the same.",
    "last_supper": "Same Last Supper painting by Da Vinci but with Jeffrey Epstein (dark-haired man, egg-shaped head, dark clothing) standing subtly in the shadows on the far left side. Keep the Renaissance painting style exactly the same.",
    "bar_folies": "Same Manet Bar at the Folies-Bergere painting but with Jeffrey Epstein (dark-haired man in dark suit, egg-shaped head) visible in the mirror reflection in the background crowd at the upper right. Keep the impressionist style exactly the same."
}

for name, prompt in IMAGES.items():
    dst = f"{EDITED_DIR}/{name}.jpg"
    if os.path.exists(dst) and os.path.getsize(dst) > 1000:
        print(f"=== {name}: already exists, skipping ===")
        continue
    
    print(f"=== Processing {name} ===")
    src = f"{BASE_DIR}/images/originals/{name}.jpg"
    
    url = upload(src)
    if not url:
        print(f"  Upload failed!")
        continue
    
    result_url = generate(url, prompt)
    if not result_url:
        print(f"  Generation failed!")
        continue
    
    download(result_url, dst)

print("\n=== ALL DONE ===")
