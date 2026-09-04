import os
import math
import requests
from dotenv import load_dotenv

load_dotenv()

def publish_video_to_tiktok(video_path_or_url, title, is_url=False):
    """
    Publishes a video to TikTok using Content Posting API v2.
    Supports either public video URL (PULL_FROM_URL) or local file upload (FILE_UPLOAD).
    """
    access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "").strip()
    if not access_token:
        return {"success": False, "error": "TIKTOK_ACCESS_TOKEN غير مضبوط في .env"}

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }

    try:
        init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"

        if is_url or (isinstance(video_path_or_url, str) and video_path_or_url.startswith("http")):
            payload = {
                "post_info": {
                    "title": title[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "PULL_FROM_URL",
                    "video_url": video_path_or_url
                }
            }
            res = requests.post(init_url, headers=headers, json=payload, timeout=30)
            data = res.json()
            if data.get("error", {}).get("code") == "ok":
                return {"success": True, "publish_id": data.get("data", {}).get("publish_id")}
            return {"success": False, "error": data.get("error", {}).get("message")}
        else:
            if not os.path.exists(video_path_or_url):
                return {"success": False, "error": f"ملف الفيديو غير موجود: {video_path_or_url}"}

            file_size = os.path.getsize(video_path_or_url)
            chunk_size = min(file_size, 10 * 1024 * 1024)
            chunk_count = math.ceil(file_size / chunk_size)

            payload = {
                "post_info": {
                    "title": title[:150],
                    "privacy_level": "PUBLIC_TO_EVERYONE",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": file_size,
                    "chunk_size": chunk_size,
                    "total_chunk_count": chunk_count
                }
            }

            res = requests.post(init_url, headers=headers, json=payload, timeout=30)
            data = res.json()
            if data.get("error", {}).get("code") != "ok":
                return {"success": False, "error": data.get("error", {}).get("message")}

            upload_url = data.get("data", {}).get("upload_url")
            publish_id = data.get("data", {}).get("publish_id")

            with open(video_path_or_url, "rb") as f:
                start_byte = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    end_byte = start_byte + len(chunk) - 1
                    upload_headers = {
                        "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
                        "Content-Type": "video/mp4",
                        "Content-Length": str(len(chunk))
                    }
                    requests.put(upload_url, headers=upload_headers, data=chunk, timeout=60)
                    start_byte = end_byte + 1

            return {"success": True, "publish_id": publish_id}

    except Exception as e:
        return {"success": False, "error": str(e)}
