import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """أنت خبير تسويق رقمي وصانع محتوى سوشيال ميديا محترف متخصص في برامج الكاشير ونقاط البيع (POS) وإدارة المتاجر والمطاعم في مصر والسعودية والخليج.
هدفك: كتابة منشورات تسويقية ذكية ومقنعة تمس المشاكل اليومية الحقيقية لأصحاب الأنشطة التجارية (سرقة الكاشير، عجز الخزينة، انقطاع النت وتعطل الزبائن، ضياع المخزون، استنزاف الاشتراكات الشهرية).

معلومات وباقات نظام RoboVAI PRO POS v6.0:
- يعمل 100% أوفلاين مدى الحياة بدون أي حاجة للإنترنت.
- ترخيص تمليك دائم ومرونة باقات بدون قيود:
  1. باقة تجربة / شهر بـ 799 ج.م (199 ر.س) لفك التردد والأنشطة الموسمية.
  2. باقة 6 شهور بـ 3,999 ج.م (999 ر.س).
  3. الباقة السنوية الأكثر طلباً بـ 6,999 ج.م/سنة (1,799 ر.س) شاملة كل التحديثات والدعم الفني ذو الأولوية.
  4. باقة التمليك مدى الحياة (LifeTime) بـ 19,999 ج.م (4,999 ر.س) تدفع مرة واحدة للأبد لجهازك مع سنة كاملة تحديثات ودعم مجاني، وعقد صيانة وتحديثات سنوي اختياري (AMC) بـ 3,999 ج.م/سنة فقط.
- إنهاء الفاتورة في ثانيتين بدون أي تهنيج نهائياً (0% Lag).
- بوت تليجرام تلقائي يرسل إشعارات بالمبيعات وتقفيل الوردية Z-Report للمالك على الموبايل لحظياً.
- تطبيق مخازن PWA مجاني يجرد البضاعة بكاميرا الهاتف بدون أجهزة هاند هيلد باهظة.
- لوحة تحكم إدارية بالمتصفح لمتابعة المبيعات وساعات الذروة.
- متوافق مع الفاتورة الإلكترونية والضريبية في مصر وهيئة الزكاة والضريبة ZATCA بالسعودية.
- عروض الإطلاق: كود الخصم الحصري (LAUNCH100) لأول 100 عميل فقط، مع تجربة مجانية 14 يوماً.
- رابط الموقع الرسمي: https://pos.robovai.tech/
- واتساب المبيعات والدعم الفني: +201121891913
"""

# Pool of Groq API Keys for automatic rotation and zero downtime
GROQ_KEYS = [
    os.getenv("GROQ_API_KEY_2", "").strip(),
    os.getenv("GROQ_API_KEY_3", "").strip(),
    os.getenv("GROQ_API_KEY_4", "").strip(),
    os.getenv("GROQ_API_KEY", "").strip(),
]
GROQ_KEYS = [k for k in GROQ_KEYS if k.startswith("gsk_")]

_key_index = 0

def get_next_groq_key():
    global _key_index
    if not GROQ_KEYS:
        return None
    key = GROQ_KEYS[_key_index % len(GROQ_KEYS)]
    _key_index += 1
    return key

def generate_social_content(topic, target_platform="all", custom_image_description="", engine="groq"):
    """
    Generates marketing content across 4 platforms (Facebook, Twitter, Instagram, Telegram)
    using Groq (ultra-fast LPU inference) with automatic key rotation or Gemini.
    """
    prompt = f"""
قم بصياغة محتوى تسويقي احترافي وجذاب وفائق الإقناع حول موضوع: "{topic}"
{f"الصورة أو الفيديو المرفق يعرض: {custom_image_description}" if custom_image_description else ""}

القواعد الإلزامية لصناعة المحتوى:
1. الخطاف (Hook): السطر الأول يجب أن يوقف التمرير فوراً ويلمس ألماً حقيقياً لأصحاب الأنشطة التجارية (سرقة الكاشير، عجز الدرج، انقطاع النت في أوقات الذروة، الاشتراكات الشهرية المستنزفة).
2. الشرح المقنع: توضيح كيف يحل نظام RoboVAI PRO POS المشكلة بنقاط سريعة (100% أوفلاين مدى الحياة، Z-Report بالسنتيم، تمليك دائم، جرد بكاميرا الموبايل).
3. الـ CTA المزدوج الحاسم:
   - حث العميل على كتابة "سعر" أو "تفاصيل" في التعليقات لاستلام كود الخصم الحصري (LAUNCH100) وتفاصيل النسخة فوراً في رسائل الخاص (لتشغيل الرد الآلي).
   - رابط التجربة المجانية المباشر 14 يوماً: https://pos.robovai.tech/
   - رابط الواتساب المباشر لمهندس المبيعات: https://wa.me/201121891913

المطلوب: توليد 4 نصوص تسويقية مخصصة بصيغة JSON حصراً:
{{
  "facebook": "بوست فيسبوك متكامل يبدأ بهوك حارق، ويشرح الميزة بنقاط وإيموجي ذكية، مع الـ CTA المزدوج (اكتب تفاصيل في الكومنتات + رابط الموقع + واتساب)",
  "twitter": "تغريدة تويتر موجزة تبدأ بأرقام أو سؤال صادم، رابط الموقع، وهاشتاجات قوية",
  "instagram": "كابشن إنستجرام جذاب يركز على الصورة، نقاط واضحة، دعوة للتعليق ورابط في البايو، مع 6-8 هاشتاجات تجارية نشطة",
  "telegram": "رسالة قناة تليجرام أنيقة بعناوين عريضة ورابط مباشر للتجربة والواتساب مع كود LAUNCH100"
}}

أجب بكائن JSON صالح فقط بدون أي تعليقات خارجية.
"""

    # 1. Try Groq with key rotation
    if engine in ("groq", "auto") and GROQ_KEYS:
        for _ in range(len(GROQ_KEYS)):
            current_key = get_next_groq_key()
            try:
                res = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {current_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "qwen/qwen3.8-27b",
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt}
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.7
                    },
                    timeout=25
                )
                if res.status_code == 200:
                    raw = res.json()["choices"][0]["message"]["content"]
                    return parse_json_response(raw)
            except Exception as e:
                print(f"[Groq Key Error]: {e}, trying next key...")

    # 2. Try Gemini (if configured)
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            res = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]}],
                    "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}
                },
                timeout=30
            )
            if res.status_code == 200:
                raw = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                return parse_json_response(raw)
        except Exception as e:
            print(f"[Gemini Error]: {e}")

    # 3. Fallback template if network/keys fail
    return fallback_templates(topic)

def parse_json_response(raw_text):
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    try:
        return json.loads(text.strip())
    except Exception:
        return {
            "facebook": text,
            "twitter": text[:270],
            "instagram": text,
            "telegram": text
        }

def fallback_templates(topic):
    return {
        "facebook": f"🚨 أصحاب المتاجر والمطاعم.. هل تعلم أن 70% من عجز الخزينة يحدث بسبب بطء الكاشير وتراكم الفواتير في الزحمة؟\n\nنظام RoboVAI PRO POS v6.0 صُمم ليحل هذه الأزمة نهائياً:\n✅ يعمل 100% أوفلاين بدون نت\n✅ تقفيل ورديات Z-Report بالسنتيم\n✅ إشعارات حية على تليجرام بكل فاتورة وعجز الخزينة\n\n🔥 خصم الإطلاق متاح لأول 100 عميل فقط بكود (LAUNCH100)!\n🌐 جرب مجاناً 14 يوماً: https://pos.robovai.tech/\n💬 تواصل واتساب: https://wa.me/201121891913",
        "twitter": f"النت فصل وطابور الزبائن واقف؟ ❌\nمع كاشير RoboVAI PRO POS المبيعات لن تتوقف ثانية واحدة! يعمل 100% أوفلاين وتقفيل ورديات Z-Report بالسنتيم ⚡\n\n🔥 كود الخصم: LAUNCH100\n🔗 https://pos.robovai.tech/",
        "instagram": f"ودّع صداع عجز الخزينة ومشاكل الكاشير في أوقات الذروة! 🛒📊\n\nمنظومة RoboVAI PRO POS توفر لك:\n⚡ سرعة خارقة (فاتورة في ثانيتين)\n🔒 حماية تامة للخزينة ومنع التلاعب\n📲 إشعارات لحظية على تليجرام\n📱 جرد المخزن بكاميرا الموبايل\n\n🎁 احصل على خصم الإطلاق بكود: LAUNCH100\nرابط التجربة المجانية في البايو 👆\n\n#كاشير #نقاط_بيع #سوبرماركت #مطاعم #كافيهات #POS #تجارة #مخازن",
        "telegram": f"📢 **تنبيه هام لأصحاب الأنشطة التجارية والمطاعم**\n\nهل تعاني من عجز الخزينة اليومي أو بطء النظام القديم؟\n\nنظام **RoboVAI PRO POS v6.0** يمنحك السيطرة التامة:\n• يعمل 100% بدون إنترنت.\n• ترخيص تمليك دائم مدى الحياة.\n• بوت تليجرام يرسل لك مبيعات محلك أولاً بأول.\n\n🔥 **عرض خاص لأول 100 عميل**: كود خصم إضافي `LAUNCH100`\n\n🌐 للمعاينة والتجربة المجانية (14 يوماً):\nhttps://pos.robovai.tech/\n💬 للتواصل المباشر مع المبيعات:\nhttps://wa.me/201121891913"
    }
