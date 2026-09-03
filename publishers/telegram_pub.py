import os
import requests
from dotenv import load_dotenv

load_dotenv()

def publish_to_telegram(text, image_path=None, chat_id=None):
    """
    Publishes a post (text + optional image) to a Telegram channel or group.
    100% Free and unlimited via Telegram Bot API.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    target_chat = chat_id or os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

    if not token:
        return {"success": False, "error": "TELEGRAM_BOT_TOKEN غير مضبوط في ملف .env"}
    if not target_chat:
        return {"success": False, "error": "TELEGRAM_CHANNEL_ID غير مضبوط في ملف .env"}

    try:
        if image_path and os.path.exists(image_path):
            is_video = image_path.lower().endswith(('.mp4', '.mov', '.avi'))
            url = f"https://api.telegram.org/bot{token}/sendVideo" if is_video else f"https://api.telegram.org/bot{token}/sendPhoto"
            file_key = "video" if is_video else "photo"
            with open(image_path, "rb") as media_file:
                res = requests.post(
                    url,
                    data={"chat_id": target_chat, "caption": text, "parse_mode": "HTML"},
                    files={file_key: media_file},
                    timeout=120
                )
        else:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            res = requests.post(
                url,
                data={"chat_id": target_chat, "text": text, "parse_mode": "Markdown"},
                timeout=30
            )

        data = res.json()
        if data.get("ok"):
            return {"success": True, "message_id": data["result"]["message_id"]}
        else:
            return {"success": False, "error": data.get("description", "Unknown error")}
    except Exception as e:
        return {"success": False, "error": str(e)}
