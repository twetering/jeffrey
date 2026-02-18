#!/bin/bash
set -e
cd /home/node/.openclaw/workspace/demos/waar-is-jeffrey

API_KEY="619195cf-f056-41e5-bd6c-5e29fe9400a1:oEG7YyMHDR7w-hxDy3M4I27O4x_mp0QX"
AUTH="Bearer $API_KEY"

upload_image() {
  local file="$1"
  echo "Uploading $file..."
  RESP=$(curl -s -X POST "https://api.krea.ai/assets" \
    -H "Authorization: $AUTH" \
    -F "file=@$file")
  echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('url') or d.get('asset_url') or d.get('id',''))"
}

generate() {
  local prompt="$1"
  local image_url="$2"
  local aspect="$3"
  local output="$4"
  
  echo "=== Generating: $output ==="
  echo "Prompt: ${prompt:0:80}..."
  
  RESP=$(curl -s -X POST "https://api.krea.ai/generate/image/google/nano-banana-pro" \
    -H "Authorization: $AUTH" \
    -H "Content-Type: application/json" \
    -d "$(python3 -c "
import json
d = {
  'prompt': '''$prompt''',
  'image': '$image_url',
  'resolution': '4K',
  'aspectRatio': '$aspect'
}
print(json.dumps(d))
")")
  
  echo "Response: $RESP"
  JOB_ID=$(echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('id') or d.get('job_id',''))")
  echo "Job ID: $JOB_ID"
  
  if [ -z "$JOB_ID" ]; then
    echo "FAILED to get job ID"
    return 1
  fi
  
  for i in $(seq 1 40); do
    sleep 5
    STATUS=$(curl -s -H "Authorization: $AUTH" "https://api.krea.ai/jobs/$JOB_ID")
    STATE=$(echo "$STATUS" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null)
    echo "  Poll $i: $STATE"
    
    if [ "$STATE" = "completed" ]; then
      IMG_URL=$(echo "$STATUS" | python3 -c "
import sys,json
d=json.load(sys.stdin)
urls = d.get('result',{}).get('images',[])
if urls: print(urls[0] if isinstance(urls[0],str) else urls[0].get('url',''))
else:
  url = d.get('result',{}).get('url','') or d.get('result',{}).get('image','')
  print(url)
")
      echo "  Download URL: $IMG_URL"
      if [ -n "$IMG_URL" ]; then
        curl -s -o "images/edited/${output}" "$IMG_URL"
        echo "  Saved to images/edited/${output}"
        ls -la "images/edited/${output}"
      fi
      return 0
    elif [ "$STATE" = "failed" ]; then
      echo "  FAILED!"
      echo "$STATUS"
      return 1
    fi
  done
  echo "  TIMEOUT"
  return 1
}

# Upload all originals first
echo "=== UPLOADING ORIGINALS ==="
URL_BANQUET=$(upload_image images/originals/george_iv_banquet.jpg)
echo "Banquet URL: $URL_BANQUET"
URL_ATHENS=$(upload_image images/originals/school_athens.jpg)
echo "Athens URL: $URL_ATHENS"
URL_WEDDING=$(upload_image images/originals/peasant_wedding.jpg)
echo "Wedding URL: $URL_WEDDING"
URL_SUPPER=$(upload_image images/originals/last_supper.jpg)
echo "Supper URL: $URL_SUPPER"
URL_BAR=$(upload_image images/originals/bar_folies.jpg)
echo "Bar URL: $URL_BAR"

echo ""
echo "=== GENERATING IMAGES ==="

generate "This exact same painting of the George IV Coronation Banquet in Westminster Hall, 1821, perfectly preserved. Add one small additional figure: a man with dark receding hair, oval face, and early 19th century English formal attire, sitting at one of the long banquet tables in the far background, approximately 35% from left and 70% from top. He should be painted in the exact same warm golden style as the rest of the painting, very small and nearly invisible among the hundreds of banquet guests. Everything else must remain identical." "$URL_BANQUET" "16:9" "george_iv_banquet_4k.png"

generate "This exact same Raphael fresco The School of Athens, perfectly preserved in every detail. Add one subtle additional figure: a man with dark receding hair and an oval face, wearing classical Greek robes, standing in the far left archway at approximately 8% from left and 55% from top, partially hidden behind a column. Painted in Raphaels exact Renaissance fresco style with the same color palette and proportions. He should be very small and barely noticeable. Everything else must remain completely identical." "$URL_ATHENS" "4:3" "school_athens_4k.png"

generate "This exact same Bruegel painting The Peasant Wedding, perfectly preserved. Add one subtle figure: a man with dark receding hair wearing 16th century Flemish peasant clothing, seated at the far end of the table in the background, approximately 75% from left and 40% from top. Painted in Bruegels exact earthy color palette and detailed Flemish style. He should be small, blending in with the other guests. Everything else must remain identical." "$URL_WEDDING" "4:3" "peasant_wedding_4k.png"

generate "This exact same Leonardo da Vinci The Last Supper, perfectly preserved. Add one very subtle figure: a servant or attendant with dark receding hair standing in the dark doorway on the far right of the painting, at approximately 92% from left and 40% from top. Painted in da Vincis exact sfumato technique with the same muted Renaissance palette. The figure should be almost hidden in shadow, barely visible. Everything else must remain completely identical." "$URL_SUPPER" "16:9" "last_supper_4k.png"

generate "This exact same Manet painting A Bar at the Folies-Bergere, perfectly preserved. Add one subtle figure visible in the mirror reflection in the background crowd: a man with dark receding hair and formal black evening attire, at approximately 65% from left and 25% from top, among the reflected crowd. Painted in Manets exact impressionist brushwork style. He should be small and blend into the crowd. Everything else must remain identical." "$URL_BAR" "4:3" "bar_folies_4k.png"

echo ""
echo "=== ALL DONE ==="
ls -la images/edited/
