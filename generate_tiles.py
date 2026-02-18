#!/usr/bin/env python3
"""Generate map tiles from 4K paintings for Leaflet deep zoom."""
import os, math
from PIL import Image

BASE = "/home/node/.openclaw/workspace/demos/waar-is-jeffrey"
TILE_SIZE = 256
QUALITY = 90

PAINTINGS = {
    "oranjes": "oranjes_4k.png",
    "nachtwacht": "night_watch_4k.png",
    "banquet": "george_iv_banquet_4k.png",
    "athens": "school_athens_4k.png",
    "wedding": "peasant_wedding_4k.png",
    "supper": "last_supper_4k.png",
    "bar": "bar_folies_4k.png",
}

def generate_tiles(level_id, filename):
    src = os.path.join(BASE, "images/edited", filename)
    out_dir = os.path.join(BASE, "images/tiles", level_id)
    os.makedirs(out_dir, exist_ok=True)

    img = Image.open(src)
    w, h = img.size
    print(f"\n{level_id}: {w}x{h}")

    # Thumbnail
    thumb = img.copy()
    thumb.thumbnail((400, 400), Image.LANCZOS)
    thumb.save(os.path.join(out_dir, "thumb.jpg"), "JPEG", quality=QUALITY)
    print(f"  thumb: {thumb.size[0]}x{thumb.size[1]}")

    # Calculate max zoom: at max zoom, image is at native resolution
    max_dim = max(w, h)
    max_zoom = math.ceil(math.log2(max_dim / TILE_SIZE))
    
    for z in range(max_zoom + 1):
        # At zoom z, the image is scaled so that max_dim fits in 2^z * TILE_SIZE
        scale = (2 ** z) / (2 ** max_zoom)
        scaled_w = int(w * scale)
        scaled_h = int(h * scale)
        
        if scaled_w < 1 or scaled_h < 1:
            continue

        scaled = img.resize((scaled_w, scaled_h), Image.LANCZOS)
        
        cols = math.ceil(scaled_w / TILE_SIZE)
        rows = math.ceil(scaled_h / TILE_SIZE)
        
        z_dir = os.path.join(out_dir, str(z))
        os.makedirs(z_dir, exist_ok=True)
        
        tile_count = 0
        for x in range(cols):
            x_dir = os.path.join(z_dir, str(x))
            os.makedirs(x_dir, exist_ok=True)
            for y in range(rows):
                left = x * TILE_SIZE
                upper = y * TILE_SIZE
                right = min(left + TILE_SIZE, scaled_w)
                lower = min(upper + TILE_SIZE, scaled_h)
                
                tile = Image.new("RGB", (TILE_SIZE, TILE_SIZE), (13, 13, 13))
                crop = scaled.crop((left, upper, right, lower))
                tile.paste(crop, (0, 0))
                tile.save(os.path.join(x_dir, f"{y}.jpg"), "JPEG", quality=QUALITY)
                tile_count += 1
        
        print(f"  zoom {z}: {scaled_w}x{scaled_h}, {cols}x{rows} = {tile_count} tiles")
    
    return max_zoom

if __name__ == "__main__":
    info = {}
    for level_id, filename in PAINTINGS.items():
        max_z = generate_tiles(level_id, filename)
        img = Image.open(os.path.join(BASE, "images/edited", filename))
        info[level_id] = {"maxZoom": max_z, "width": img.size[0], "height": img.size[1]}
    
    print("\n\n=== Level info ===")
    for k, v in info.items():
        print(f"  {k}: {v}")
