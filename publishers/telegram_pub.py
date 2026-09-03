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
            url = f"https://api.telegram.org/bot{token}/sendPhoto"
            with open(image_path, "rb") as photo_file:
                res = requests.post(
                    url,
                    data={"chat_id": target_chat, "caption": text, "parse_mode": "Markdown"},
                    files={"photo": photo_file},
                    timeout=30
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
