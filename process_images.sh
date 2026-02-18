#!/bin/bash
set -e

API_KEY="619195cf-f056-41e5-bd6c-5e29fe9400a1:oEG7YyMHDR7w-hxDy3M4I27O4x_mp0QX"
BASE_DIR="/home/node/.openclaw/workspace/demos/waar-is-jeffrey"
EDITED_DIR="$BASE_DIR/images/edited"
mkdir -p "$EDITED_DIR"

# Upload an image and get the URL
upload_asset() {
  local file="$1"
  echo "Uploading $file..." >&2
  local response=$(curl -s -X POST "https://api.krea.ai/assets" \
    -H "Authorization: Bearer $API_KEY" \
    -F "file=@$file")
  echo "Upload response: $response" >&2
  echo "$response" | jq -r '.url // .image_url // .id'
}

# Generate image with img2img
generate_image() {
  local image_url="$1"
  local prompt="$2"
  local strength="$3"
  
  echo "Generating with prompt: $prompt" >&2
  local response=$(curl -s -X POST "https://api.krea.ai/generate/image/bfl/flux-1.1-pro" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"prompt\": \"$prompt\",
      \"imageUrl\": \"$image_url\",
      \"strength\": $strength,
      \"guidance_scale\": 3.0,
      \"width\": 1024,
      \"height\": 1024
    }")
  echo "Generate response: $response" >&2
  
  # Check if completed immediately
  local status=$(echo "$response" | jq -r '.status // empty')
  if [ "$status" = "completed" ]; then
    echo "$response" | jq -r '.result.urls[0] // .result.url // .result'
    return
  fi
  
  # Poll for job completion
  local job_id=$(echo "$response" | jq -r '.job_id // empty')
  if [ -z "$job_id" ]; then
    echo "ERROR: No job_id in response" >&2
    return 1
  fi
  
  echo "Polling job $job_id..." >&2
  for i in $(seq 1 60); do
    sleep 3
    local poll=$(curl -s "https://api.krea.ai/jobs/$job_id" \
      -H "Authorization: Bearer $API_KEY")
    local pstatus=$(echo "$poll" | jq -r '.status // empty')
    echo "  Poll $i: status=$pstatus" >&2
    
    if [ "$pstatus" = "completed" ]; then
      echo "$poll" | jq -r '.result.urls[0] // .result.url // .result'
      return
    fi
    if [ "$pstatus" = "failed" ]; then
      echo "ERROR: Job failed" >&2
      echo "$poll" >&2
      return 1
    fi
  done
  echo "ERROR: Timeout" >&2
  return 1
}

# Download result
download_result() {
  local url="$1"
  local output="$2"
  echo "Downloading $url -> $output" >&2
  curl -s -L -o "$output" "$url"
}

# Process each image
declare -A PROMPTS
PROMPTS[oranjes]="Same royal family group portrait painting but with Jeffrey Epstein (dark-haired man with egg-shaped head, prominent nose, thin lips, wearing a dark suit) standing subtly in the back row among the crowd on the right side. He should blend into the painted scene but be recognizable. Keep the rest of the painting exactly the same style and composition."
PROMPTS[night_watch]="Same Rembrandt Night Watch painting but with Jeffrey Epstein (dark-haired man, egg-shaped head, dark suit) partially hidden in the shadowy background behind the main figures on the far right. He blends into the dark background crowd. Keep the rest exactly the same."
PROMPTS[george_iv_banquet]="Same coronation banquet painting of George IV but with Jeffrey Epstein (dark-haired man in dark formal attire, egg-shaped head) seated subtly among the guests in the middle of the long table. Keep the rest of the grand hall scene exactly the same."
PROMPTS[school_athens]="Same School of Athens painting by Raphael but with Jeffrey Epstein (dark-haired man in dark robes, egg-shaped head, modern face) standing subtly among the philosophers on the lower left steps. Keep the Renaissance fresco style exactly the same."
PROMPTS[peasant_wedding]="Same Bruegel Peasant Wedding painting but with Jeffrey Epstein (dark-haired man, egg-shaped head, wearing dark clothing) standing in the far right background near the doorway. Keep the rest of the Flemish painting exactly the same."
PROMPTS[last_supper]="Same Last Supper painting by Da Vinci but with Jeffrey Epstein (dark-haired man, egg-shaped head, dark clothing) standing subtly in the shadows on the far left side of the room. Keep the Renaissance painting style exactly the same."
PROMPTS[bar_folies]="Same Manet Bar at the Folies-Bergere painting but with Jeffrey Epstein (dark-haired man in dark suit, egg-shaped head) visible in the mirror reflection in the background crowd at the upper right. Keep the impressionist style exactly the same."

# Corresponding Epstein positions for the game (x%, y%) - where he should appear
declare -A POSITIONS_X
declare -A POSITIONS_Y
POSITIONS_X[oranjes]=82; POSITIONS_Y[oranjes]=25
POSITIONS_X[night_watch]=90; POSITIONS_Y[night_watch]=35
POSITIONS_X[george_iv_banquet]=50; POSITIONS_Y[george_iv_banquet]=45
POSITIONS_X[school_athens]=12; POSITIONS_Y[school_athens]=68
POSITIONS_X[peasant_wedding]=93; POSITIONS_Y[peasant_wedding]=28
POSITIONS_X[last_supper]=5; POSITIONS_Y[last_supper]=48
POSITIONS_X[bar_folies]=65; POSITIONS_Y[bar_folies]=20

for name in oranjes night_watch george_iv_banquet school_athens peasant_wedding last_supper bar_folies; do
  echo "=== Processing $name ===" >&2
  
  src="$BASE_DIR/images/originals/${name}.jpg"
  dst="$EDITED_DIR/${name}.jpg"
  
  if [ -f "$dst" ] && [ -s "$dst" ]; then
    echo "Already exists, skipping" >&2
    continue
  fi
  
  # Upload
  asset_url=$(upload_asset "$src")
  echo "Asset URL: $asset_url" >&2
  
  if [ -z "$asset_url" ] || [ "$asset_url" = "null" ]; then
    echo "Upload failed, skipping $name" >&2
    continue
  fi
  
  # Generate
  result_url=$(generate_image "$asset_url" "${PROMPTS[$name]}" "0.20")
  echo "Result URL: $result_url" >&2
  
  if [ -z "$result_url" ] || [ "$result_url" = "null" ]; then
    echo "Generation failed for $name" >&2
    continue
  fi
  
  # Download
  download_result "$result_url" "$dst"
  echo "Saved $dst ($(stat -c%s "$dst") bytes)" >&2
  
  echo ""
done

echo "=== All done ===" >&2
