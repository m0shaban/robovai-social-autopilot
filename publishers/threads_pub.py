import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def publish_to_threads(text, image_url=None):
    access_token = os.getenv("THREADS_ACCESS_TOKEN", "").strip()
    threads_user_id = os.getenv("THREADS_USER_ID", "me").strip()

    if not access_token:
        return {"success": False, "error": "THREADS_ACCESS_TOKEN not configured"}

    try:
        container_url = fbhttps://graph.threads.net/v1.0/{threads_user_id}/threads"
        payload = {"access_token": access_token}
        if image_url:
            payload["media_type"] = "IMAGE"
            payload["image_url"] = image_url
            payload["text"] = text
        else:
            payload["media_type"] = "TEXT"
            payload["text"] = text

        r1 = requests.post(container_url, data=payload, timeout=30)
        d1 = r1.json()
        if "id" not in d1:
            return {"success": False, "error": d1.get("error", {}).get("message", "Failed to create container")}

        cid = d1["id"]
        time.sleep(3)

        pub_url = fbhttps://graph.threads.net/v1.0/{threads_user_id}/threads_publish"
        r2 = requests.post(pub_url, data={"creation_id": cid, "access_token": access_token}, timeout=30)
        d2 = r2.json()

        if "id" in d2:
            return {"success": True, "threads_id": d2["id"]}
        else:
            return {"success": False, "error": d2.get("error", {}).get("message", "Failed to publish")}
    except Exception as e:
        return {"success": False, "error": str(e)}
