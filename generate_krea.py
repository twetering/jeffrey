#!/usr/bin/env python3
import requests, time, json, sys, os

API_KEY = "619195cf-f056-41e5-bd6c-5e29fe9400a1:oEG7YyMHDR7w-hxDy3M4I27O4x_mp0QX"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}
BASE = "/home/node/.openclaw/workspace/demos/waar-is-jeffrey"

def upload(path):
    print(f"Uploading {path}...")
    with open(path, "rb") as f:
        r = requests.post("https://api.krea.ai/assets", headers=HEADERS, files={"file": f})
    d = r.json()
    asset_id = d.get("url") or d.get("asset_url") or d.get("id", "")
    print(f"  Asset: {asset_id}")
    return asset_id

def generate(prompt, image_url, aspect, output_name):
    print(f"\n=== Generating: {output_name} ===")
    body = {
        "prompt": prompt,
        "image": image_url,
        "resolution": "4K",
        "aspectRatio": aspect
    }
    r = requests.post("https://api.krea.ai/generate/image/google/nano-banana-pro",
                       headers={**HEADERS, "Content-Type": "application/json"},
                       json=body)
    d = r.json()
    print(f"  Response: {json.dumps(d)[:200]}")
    job_id = d.get("id") or d.get("job_id")
    if not job_id:
        print("  FAILED - no job ID")
        return False

    for i in range(40):
        time.sleep(5)
        r2 = requests.get(f"https://api.krea.ai/jobs/{job_id}", headers=HEADERS)
        status = r2.json()
        state = status.get("status", "unknown")
        print(f"  Poll {i+1}: {state}")
        
        if state == "completed":
            result = status.get("result", {})
            # Try various response formats
            urls = result.get("urls", []) or result.get("images", [])
            if urls:
                img_url = urls[0] if isinstance(urls[0], str) else urls[0].get("url", "")
            else:
                img_url = result.get("url", "") or result.get("image", "")
            
            if img_url:
                img_data = requests.get(img_url).content
                out_path = f"{BASE}/images/edited/{output_name}"
                with open(out_path, "wb") as f:
                    f.write(img_data)
                print(f"  Saved: {out_path} ({len(img_data)} bytes)")
                return True
            else:
                print(f"  No image URL in result: {json.dumps(status)[:300]}")
                return False
        elif state == "failed":
            print(f"  FAILED: {json.dumps(status)[:300]}")
            return False
    
    print("  TIMEOUT")
    return False

# Upload originals
urls = {}
for name, path in [
    ("banquet", f"{BASE}/images/originals/george_iv_banquet.jpg"),
    ("athens", f"{BASE}/images/originals/school_athens.jpg"),
    ("wedding", f"{BASE}/images/originals/peasant_wedding.jpg"),
    ("supper", f"{BASE}/images/originals/last_supper.jpg"),
    ("bar", f"{BASE}/images/originals/bar_folies.jpg"),
]:
    urls[name] = upload(path)

# Generate
paintings = [
    ("This exact same painting of the George IV Coronation Banquet in Westminster Hall, 1821, perfectly preserved. Add one small additional figure: a man with dark receding hair, oval face, and early 19th century English formal attire, sitting at one of the long banquet tables in the far background, approximately 35% from left and 70% from top. He should be painted in the exact same warm golden style as the rest of the painting, very small and nearly invisible among the hundreds of banquet guests. Everything else must remain identical.",
     urls["banquet"], "16:9", "george_iv_banquet_4k.png"),
    
    ("This exact same Raphael fresco 'The School of Athens', perfectly preserved in every detail. Add one subtle additional figure: a man with dark receding hair and an oval face, wearing classical Greek robes, standing in the far left archway at approximately 8% from left and 55% from top, partially hidden behind a column. Painted in Raphael's exact Renaissance fresco style with the same color palette and proportions. He should be very small and barely noticeable. Everything else must remain completely identical.",
     urls["athens"], "4:3", "school_athens_4k.png"),
    
    ("This exact same Bruegel painting 'The Peasant Wedding', perfectly preserved. Add one subtle figure: a man with dark receding hair wearing 16th century Flemish peasant clothing, seated at the far end of the table in the background, approximately 75% from left and 40% from top. Painted in Bruegel's exact earthy color palette and detailed Flemish style. He should be small, blending in with the other guests. Everything else must remain identical.",
     urls["wedding"], "4:3", "peasant_wedding_4k.png"),
    
    ("This exact same Leonardo da Vinci 'The Last Supper', perfectly preserved. Add one very subtle figure: a servant or attendant with dark receding hair standing in the dark doorway on the far right of the painting, at approximately 92% from left and 40% from top. Painted in da Vinci's exact sfumato technique with the same muted Renaissance palette. The figure should be almost hidden in shadow, barely visible. Everything else must remain completely identical.",
     urls["supper"], "16:9", "last_supper_4k.png"),
    
    ("This exact same Manet painting 'A Bar at the Folies-Bergère', perfectly preserved. Add one subtle figure visible in the mirror reflection in the background crowd: a man with dark receding hair and formal black evening attire, at approximately 65% from left and 25% from top, among the reflected crowd. Painted in Manet's exact impressionist brushwork style. He should be small and blend into the crowd. Everything else must remain identical.",
     urls["bar"], "4:3", "bar_folies_4k.png"),
]

results = {}
for prompt, img_url, aspect, output in paintings:
    out_path = f"{BASE}/images/edited/{output}"
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000000:
        print(f"\n=== Skipping {output} (already exists) ===")
        results[output] = True
        continue
    ok = generate(prompt, img_url, aspect, output)
    results[output] = ok
    if not ok:
        print(f"  Retrying {output}...")
        ok = generate(prompt, img_url, aspect, output)
        results[output] = ok

print("\n=== RESULTS ===")
for k, v in results.items():
    print(f"  {k}: {'OK' if v else 'FAILED'}")
