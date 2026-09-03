import os
import requests
from dotenv import load_dotenv

load_dotenv()

def publish_to_twitter(text):
    """
    Publishes a tweet using X (Twitter) API v2 Free Tier.
    """
    api_key = os.getenv("TWITTER_API_KEY", "").strip()
    api_secret = os.getenv("TWITTER_API_SECRET", "").strip()
    access_token = os.getenv("TWITTER_ACCESS_TOKEN", "").strip()
    access_secret = os.getenv("TWITTER_ACCESS_SECRET", "").strip()

    if not (api_key and api_secret and access_token and access_secret):
        return {"success": False, "error": "مفاتيح تويتر (Twitter API Keys) غير مكتملة في .env"}

    try:
        from requests_oauthlib import OAuth1
        auth = OAuth1(api_key, api_secret, access_token, access_secret)
        
        url = "https://api.twitter.com/2/tweets"
        res = requests.post(url, json={"text": text[:280]}, auth=auth, timeout=30)
        
        data = res.json()
        if "data" in data and "id" in data["data"]:
            return {"success": True, "tweet_id": data["data"]["id"]}
        else:
            return {"success": False, "error": str(data)}
    except ImportError:
        return {"success": False, "error": "يرجى تثبيت requests-oauthlib عبر: pip install requests-oauthlib"}
    except Exception as e:
        return {"success": False, "error": str(e)}
