import os
import requests
from dotenv import load_dotenv

load_dotenv()

def publish_to_facebook(text, image_path=None):
    """
    Publishes a photo post or text post to a Facebook Page via Graph API.
    """
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN", "").strip()
    page_id = os.getenv("FB_PAGE_ID", "").strip()

    if not access_token or not page_id:
        return {"success": False, "error": "FB_PAGE_ACCESS_TOKEN أو FB_PAGE_ID غير مضبوط في .env"}

    try:
        if image_path and os.path.exists(image_path):
            is_video = image_path.lower().endswith(('.mp4', '.mov', '.avi'))
            if is_video:
                url = f"https://graph.facebook.com/v19.0/{page_id}/videos"
                with open(image_path, "rb") as vid:
                    res = requests.post(
                        url,
                        data={"description": text, "access_token": access_token},
                        files={"source": vid},
                        timeout=120
                    )
            else:
                url = f"https://graph.facebook.com/v19.0/{page_id}/photos"
                with open(image_path, "rb") as img:
                    res = requests.post(
                        url,
                        data={"message": text, "access_token": access_token},
                        files={"source": img},
                        timeout=45
                    )
        else:
            url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
            res = requests.post(
                url,
                data={"message": text, "access_token": access_token},
                timeout=30
            )

        data = res.json()
        if "id" in data:
            return {"success": True, "post_id": data["id"]}
        else:
            return {"success": False, "error": data.get("error", {}).get("message", "Unknown Facebook error")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def publish_to_instagram(caption, image_url):
    """
    Publishes to an Instagram Business account connected to Facebook Page.
    Requires a publicly accessible image URL.
    """
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN", "").strip()
    ig_user_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()

    if not access_token or not ig_user_id:
        return {"success": False, "error": "INSTAGRAM_ACCOUNT_ID أو FB_PAGE_ACCESS_TOKEN غير مضبوط"}

    try:
        # Step 1: Create media container
        step1_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        res1 = requests.post(
            step1_url,
            data={"image_url": image_url, "caption": caption, "access_token": access_token},
            timeout=30
        )
        data1 = res1.json()
        if "id" not in data1:
            return {"success": False, "error": data1.get("error", {}).get("message")}

        creation_id = data1["id"]

        # Wait 4 seconds for Instagram server to fetch and process image
        import time
        time.sleep(4)

        # Step 2: Publish media container
        step2_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        res2 = requests.post(
            step2_url,
            data={"creation_id": creation_id, "access_token": access_token},
            timeout=30
        )
        data2 = res2.json()
        if "id" in data2:
            return {"success": True, "ig_media_id": data2["id"]}
        else:
            return {"success": False, "error": data2.get("error", {}).get("message")}
    except Exception as e:
        return {"success": False, "error": str(e)}
