import os
import time
import json
from curl_cffi import requests as browser

# Only monitoring requested streamers
STREAMERS = ["kaneljoseph"] 
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
HISTORY_FILE = "seen_clips.json"

def get_seen_clips():
    if not os.path.exists(HISTORY_FILE):
        return {}
    with open(HISTORY_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_seen_clips(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f)

def get_latest_clip(slug):
    # If the streamer doesn't exist on Kick, this API will safely return None
    url = f"https://kick.com/api/v2/channels/{slug}/clips?sort=recent"
    try:
        response = browser.get(url, impersonate="chrome124")
        if response.status_code == 200:
            data = response.json().get('data', [])
            return data[0] if data else None
    except Exception as e:
        print(f"Error checking {slug}: {e}")
    return None

def send_to_discord(clip, slug):
    data = {
        "embeds": [{
            "title": f"New Clip: {clip['title']}",
            "url": f"https://kick.com/{slug}/clips/{clip['id']}",
            "color": 16711680,
            "thumbnail": {"url": clip['thumbnail_url']},
            "description": f"Streamer: {slug}\nViews: {clip['views']}"
        }]
    }
    browser.post(WEBHOOK_URL, json=data)

# Main Loop
seen_data = get_seen_clips()
print("Bot started. Monitoring:", ", ".join(STREAMERS))

while True:
    for slug in STREAMERS:
        latest = get_latest_clip(slug)
        
        if latest:
            if slug not in seen_data:
                seen_data[slug] = []
                
            if latest['id'] not in seen_data[slug]:
                print(f"New clip from {slug}: {latest['title']}")
                send_to_discord(latest, slug)
                seen_data[slug].append(latest['id'])
                save_seen_clips(seen_data)
    
    time.sleep(300)
