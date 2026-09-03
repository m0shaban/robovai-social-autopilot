import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

from ai_generator import generate_social_content
from publishers.telegram_pub import publish_to_telegram
from publishers.meta_pub import publish_to_facebook
from publishers.twitter_pub import publish_to_twitter

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
ADMIN_CHAT_ID = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()

def send_msg(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return requests.post(url, json=payload, timeout=20).json()

def run_polling():
    if not TOKEN:
        print("❌ خطأ: يرجى ضبط TELEGRAM_BOT_TOKEN في ملف .env لتشغيل البوت!")
        return

    print("🤖 RoboVAI Social Media Bot يعمل الآن بنجاح على تليجرام...")
    print("ارسل أي صورة أو فكرة منشور للبوت ليقوم بتوليد المحتوى التسويقي ونشره بضغطة زر!")
    
    offset = 0
    pending_posts = {}

    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30"
            res = requests.get(url, timeout=40)
            data = res.json()

            if not data.get("ok"):
                time.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1

                # Handle Callback queries (button clicks)
                if "callback_query" in update:
                    cb = update["callback_query"]
                    cb_id = cb["id"]
                    cb_data = cb.get("data", "")
                    from_user = str(cb["from"]["id"])

                    if cb_data == "publish_all":
                        post_data = pending_posts.get(from_user)
                        if post_data:
                            send_msg(from_user, "⏳ جارٍ النشر على جميع المنصات...")
                            # Publish to Telegram channel
                            tg_res = publish_to_telegram(post_data["posts"].get("telegram", ""), post_data.get("image_path"))
                            # Publish to Facebook
                            fb_res = publish_to_facebook(post_data["posts"].get("facebook", ""), post_data.get("image_path"))
                            # Publish to Twitter
                            tw_res = publish_to_twitter(post_data["posts"].get("twitter", ""))

                            msg = f"""
🎉 **تمت عملية النشر بنجاح!**
• تليجرام: {'✅ تم' if tg_res.get('success') else '❌ ' + tg_res.get('error', '')}
• فيسبوك: {'✅ تم' if fb_res.get('success') else '❌ ' + fb_res.get('error', '')}
• إكس (تويتر): {'✅ تم' if tw_res.get('success') else '❌ ' + tw_res.get('error', '')}
"""
                            send_msg(from_user, msg)
                            del pending_posts[from_user]
                        else:
                            send_msg(from_user, "⚠️ لا يوجد منشور معلق للنشر حالياً.")

                    elif cb_data == "cancel":
                        pending_posts.pop(from_user, None)
                        send_msg(from_user, "❌ تم إلغاء المنشور.")

                    # Acknowledge callback
                    requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery", json={"callback_query_id": cb_id})
                    continue

                # Handle incoming messages
                if "message" in update:
                    msg = update["message"]
                    chat_id = str(msg["chat"]["id"])
                    text = msg.get("text", "")
                    caption = msg.get("caption", "")
                    prompt_topic = caption if caption else text

                    # Handle /start
                    if text == "/start":
                        env_file = os.path.join(os.path.dirname(__file__), ".env")
                        if os.path.exists(env_file):
                            with open(env_file, "r", encoding="utf-8") as f:
                                c = f.read()
                            if "TELEGRAM_ADMIN_CHAT_ID=\n" in c or "TELEGRAM_ADMIN_CHAT_ID=\r\n" in c:
                                c = c.replace("TELEGRAM_ADMIN_CHAT_ID=", f"TELEGRAM_ADMIN_CHAT_ID={chat_id}")
                                with open(env_file, "w", encoding="utf-8") as f:
                                    f.write(c)

                        welcome = f"""
👋 مرحباً بك في **غرفة التحكم الذكية لنشر محتوى RoboVAI POS**!
✅ **تم ربط حسابك بنجاح كمسؤول معتمد للنظام!** (Chat ID: `{chat_id}`)

📸 **كيف تدير صفحاتك من هنا؟**
1. ارسل أي صورة لشاشات النظام مع تعليق أو فكرة بوست (أو ارسل الفكرة فقط كنص).
2. سأقوم فوراً باستخدام الذكاء الاصطناعي (Groq LPU) بصياغة 3 منشورات احترافية لفيسبوك وتويتر وقناتك.
3. سأعطيك زراً للموافقة والنشر الفوري في كل المنصات بنقرة واحدة! 🚀
"""
                        send_msg(chat_id, welcome)
                        continue

                    # Handle Photo
                    local_img_path = None
                    if "photo" in msg:
                        file_id = msg["photo"][-1]["file_id"]
                        f_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}").json()
                        if f_info.get("ok"):
                            file_path = f_info["result"]["file_path"]
                            img_data = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file_path}").content
                            local_img_path = os.path.join(os.path.dirname(__file__), f"tg_img_{int(time.time())}.jpg")
                            with open(local_img_path, "wb") as f:
                                f.write(img_data)

                    if not prompt_topic:
                        prompt_topic = "مميزات وسرعة كاشير RoboVAI PRO POS في حماية الخزينة ومنع التلاعب مع كود LAUNCH100"

                    send_msg(chat_id, "🧠 جارٍ صياغة المحتوى التسويقي بالذكاء الاصطناعي...")
                    generated = generate_social_content(prompt_topic)

                    pending_posts[chat_id] = {
                        "posts": generated,
                        "image_path": local_img_path
                    }

                    preview = f"""
📝 **معاينة المنشور المقترح:**

📘 **فيسبوك:**
{generated.get('facebook', '')[:350]}...

🐦 **تويتر (X):**
{generated.get('twitter', '')}

📢 **قناة تليجرام:**
{generated.get('telegram', '')[:250]}...

هل تود النشر الآن على جميع الحسابات؟
"""
                    keyboard = {
                        "inline_keyboard": [
                            [
                                {"text": "🚀 انشر الآن في الكل", "callback_data": "publish_all"},
                                {"text": "❌ إلغاء", "callback_data": "cancel"}
                            ]
                        ]
                    }
                    send_msg(chat_id, preview, reply_markup=keyboard)

        except Exception as e:
            print(f"[Polling Error]: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_polling()
