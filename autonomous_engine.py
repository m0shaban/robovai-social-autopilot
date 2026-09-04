# -*- coding: utf-8 -*-
"""
RoboVAI Autonomous Marketing Publisher Engine
Operates 100% independently without human intervention.
Can be triggered via CLI, Cron, GitHub Actions, or Streamlit Webhook.
"""

import os
import sys
import json
import random
import datetime
from dotenv import load_dotenv

load_dotenv()

from campaign_strategy import CONTENT_PILLARS
from ai_generator import generate_social_content
from publishers.meta_pub import publish_to_facebook, publish_to_instagram

import urllib.parse

def get_public_asset_url(asset_path):
    if not asset_path:
        return None
    rel_path = os.path.relpath(asset_path, BASE_DIR).replace("\\", "/")
    parts = [urllib.parse.quote(part) for part in rel_path.split("/")]
    encoded_path = "/".join(parts)
    return f"https://raw.githubusercontent.com/m0shaban/robovai-social-autopilot/main/{encoded_path}"
from publishers.telegram_pub import publish_to_telegram

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "published_log.json")
CREATIVES_IMG_DIR = os.path.join(BASE_DIR, "assets", "creatives", "images")
CREATIVES_VID_DIR = os.path.join(BASE_DIR, "assets", "creatives", "videos")

def load_published_log():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"posts": [], "last_run": None, "total_published": 0}

def save_published_log(log_data):
    try:
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving log: {e}")

def get_next_creative_asset(log_data):
    """
    Selects the next optimal creative asset (alternating videos and images).
    Ensures zero repetition until the full catalogue has been showcased.
    """
    already_used = {p.get("asset_filename") for p in log_data.get("posts", []) if p.get("asset_filename")}
    
    videos = []
    if os.path.exists(CREATIVES_VID_DIR):
        videos = [os.path.join(CREATIVES_VID_DIR, f) for f in os.listdir(CREATIVES_VID_DIR) if f.lower().endswith(".mp4")]
        
    images = []
    if os.path.exists(CREATIVES_IMG_DIR):
        images = [os.path.join(CREATIVES_IMG_DIR, f) for f in os.listdir(CREATIVES_IMG_DIR) if f.lower().endswith((".jpeg", ".jpg", ".png"))]
    
    unused_videos = [v for v in videos if os.path.basename(v) not in already_used]
    unused_images = [i for i in images if os.path.basename(i) not in already_used]
    
    # Strategy: 1 video every 4 posts if videos available
    total_posts = log_data.get("total_published", 0)
    should_pick_video = (total_posts % 4 == 0) and (len(unused_videos) > 0 or len(videos) > 0)
    
    if should_pick_video:
        pool = unused_videos if unused_videos else videos
    else:
        pool = unused_images if unused_images else images
        
    if not pool:
        # Fallback to standard assets if creatives not populated
        std_dir = os.path.join(BASE_DIR, "assets", "images")
        if os.path.exists(std_dir):
            pool = [os.path.join(std_dir, f) for f in os.listdir(std_dir) if f.lower().endswith((".jpeg", ".jpg", ".png"))]
            
    if not pool:
        return None, "image"
        
    chosen = random.choice(pool)
    is_vid = chosen.lower().endswith(".mp4")
    return chosen, ("video" if is_vid else "image")

def pick_strategy_pillar(asset_path):
    """
    Matches the selected asset with the most relevant marketing pillar.
    """
    filename = os.path.basename(asset_path).lower() if asset_path else ""
    for pillar in CONTENT_PILLARS:
        for keyword in pillar["preferred_assets"]:
            if keyword.lower() in filename:
                return pillar
    # Weighted random choice as fallback
    return random.choices(CONTENT_PILLARS, weights=[p["weight"] for p in CONTENT_PILLARS], k=1)[0]

def run_autonomous_post():
    """
    Executes a single fully autonomous publishing cycle:
    1. Selects asset
    2. Identifies strategic topic & hook
    3. Calls Groq LPU AI
    4. Publishes to Facebook & Telegram
    5. Saves state log
    """
    print(f"[{datetime.datetime.now().isoformat()}] Starting autonomous publishing cycle...")
    log_data = load_published_log()
    
    asset_path, asset_type = get_next_creative_asset(log_data)
    pillar = pick_strategy_pillar(asset_path)
    hook = random.choice(pillar["hooks"])
    
    topic = f"{pillar['title']} — {hook}"
    asset_desc = f"محتوى مرئي ({asset_type}) بعنوان: {os.path.splitext(os.path.basename(asset_path))[0].replace('_', ' ')}" if asset_path else ""
    
    print(f"Asset: {os.path.basename(asset_path) if asset_path else 'None'} ({asset_type})")
    print(f"Strategic Pillar: {pillar['title']}")
    
    # 1. Generate with Groq
    print("Calling Groq LPU Copywriter...")
    posts = generate_social_content(topic, custom_image_description=asset_desc)
    fb_text = posts.get("facebook")
    tg_text = posts.get("telegram")
    ig_text = posts.get("instagram")
    
    results = {"facebook": None, "telegram": None, "instagram": None}
    
    # 2. Publish to Facebook
    if fb_text:
        print("Publishing to Facebook Page...")
        fb_res = publish_to_facebook(fb_text, asset_path)
        results["facebook"] = fb_res
        print("Facebook result:", fb_res)
        
    # 3. Publish to Instagram (via public CDN URL)
    if ig_text and asset_path and not asset_path.lower().endswith('.mp4'):
        public_url = get_public_asset_url(asset_path)
        print(f"Publishing to Instagram via URL: {public_url}...")
        ig_res = publish_to_instagram(ig_text, public_url)
        results["instagram"] = ig_res
        print("Instagram result:", ig_res)
        
    # 4. Publish to Telegram
    if tg_text:
        print("Publishing to Telegram Channel...")
        tg_res = publish_to_telegram(tg_text, asset_path)
        results["telegram"] = tg_res
        print("Telegram result:", tg_res)
        
    # 4. Record to Log
    post_record = {
        "id": log_data.get("total_published", 0) + 1,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "asset_filename": os.path.basename(asset_path) if asset_path else None,
        "asset_type": asset_type,
        "pillar_id": pillar["id"],
        "pillar_title": pillar["title"],
        "results": results
    }
    
    log_data["posts"].append(post_record)
    log_data["last_run"] = post_record["timestamp"]
    log_data["total_published"] = len(log_data["posts"])
    save_published_log(log_data)
    
    print(f"Autonomous cycle completed successfully! Total published: {log_data['total_published']}")
    return post_record

if __name__ == "__main__":
    run_autonomous_post()
