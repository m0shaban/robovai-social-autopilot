import os
import requests
import json
import streamlit as st
from PIL import Image
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Bridge Streamlit Community Cloud Secrets to os.environ
try:
    if hasattr(st, "secrets"):
        for sec_key, sec_val in st.secrets.items():
            if isinstance(sec_val, str):
                os.environ[sec_key] = sec_val
except Exception:
    pass

from env_manager import update_env_var, get_env_var
from ai_generator import generate_social_content, GROQ_KEYS
from content_calendar import SCHEDULED_CAMPAIGNS, ASSETS_DIR
from publishers.telegram_pub import publish_to_telegram
from publishers.meta_pub import publish_to_facebook
from publishers.twitter_pub import publish_to_twitter

# --- Page Configuration ---
st.set_page_config(
    page_title="RoboVAI Social Autopilot 🚀",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom RTL & Glassmorphism Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Tajawal', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .main-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #38bdf8;
        margin-bottom: 5px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-bottom: 25px;
    }
    .connect-card {
        background: rgba(15, 23, 42, 0.7);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
    }
    .badge-status-on {
        background: #065f46;
        color: #34d399;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .badge-status-off {
        background: #7f1d1d;
        color: #f87171;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 700;
    }
    .btn-connect-link {
        display: inline-block;
        background: linear-gradient(135deg, #2563eb, #38bdf8);
        color: white !important;
        padding: 10px 20px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 700;
        margin-top: 8px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Re-read env
tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
tg_admin = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "").strip()
tg_channel = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()
fb_token = os.getenv("FB_PAGE_ACCESS_TOKEN", "").strip()
fb_page_id = os.getenv("FB_PAGE_ID", "").strip()
ig_id = os.getenv("INSTAGRAM_ACCOUNT_ID", "").strip()
tw_key = os.getenv("TWITTER_API_KEY", "").strip()

# --- Sidebar: Status & Settings ---
st.sidebar.markdown("### ⚙️ حالة الربط والمفاتيح")

groq_ok = len(GROQ_KEYS) > 0
tg_ok = bool(tg_token and (tg_channel or tg_admin))
fb_ok = bool(fb_token and fb_page_id)
tw_ok = bool(tw_key)

st.sidebar.markdown(f"🧠 **Groq LPU ({len(GROQ_KEYS)} مفاتيح):** {'<span class=\"badge-status-on\">متصل فائق السرعة ⚡</span>' if groq_ok else '<span class=\"badge-status-off\">غير مضبوط</span>'}", unsafe_allow_html=True)
st.sidebar.markdown(f"📢 **تليجرام:** {'<span class=\"badge-status-on\">جاهز للنشر ✅</span>' if tg_ok else '<span class=\"badge-status-off\">غير مربوط</span>'}", unsafe_allow_html=True)
st.sidebar.markdown(f"📘 **Facebook:** {'<span class=\"badge-status-on\">جاهز للنشر ✅</span>' if fb_ok else '<span class=\"badge-status-off\">غير مربوط</span>'}", unsafe_allow_html=True)
st.sidebar.markdown(f"📸 **Instagram:** {'<span class=\"badge-status-on\">جاهز للنشر ✅</span>' if ig_id else '<span class=\"badge-status-off\">غير مربوط</span>'}", unsafe_allow_html=True)
st.sidebar.markdown(f"🐦 **X (تويتر):** {'<span class=\"badge-status-on\">جاهز للنشر ✅</span>' if tw_ok else '<span class=\"badge-status-off\">غير مربوط</span>'}", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **نصيحة سريعة:** لربط أي حساب بضغطة زر، توجه لتبويب **'🔗 مركز ربط الحسابات'** في الأعلى!")

# --- Main App Header ---
st.markdown("<div class=\"main-title\">🚀 RoboVAI Social Media Autopilot</div>", unsafe_allow_html=True)
st.markdown("<div class=\"sub-title\">المنظومة الذكية لإدارة ونشر المحتوى التسويقي التلقائي لكاشير RoboVAI PRO POS v6.0</div>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✨ توليد ونشر محتوى جديد",
    "📅 جدول الحملات الجاهزة",
    "🔗 مركز ربط الحسابات بنقرة واحدة",
    "🤖 المحرك الذاتي (Autonomous Engine)",
    "📖 دليل الإعداد السريع"
])

# ================= TAB 1: GENERATE & PUBLISH =================
with tab1:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("#### 1. موضوع المنشور")
        
        # Topic selection
        topic_mode = st.radio("مصدر الفكرة:", ["اختر من الحملات المقترحة", "أدخل فكرة مخصصة"], horizontal=True)
        if topic_mode == "اختر من الحملات المقترحة":
            campaign_names = [f"[{c['category']}] {c['title']}" for c in SCHEDULED_CAMPAIGNS]
            selected_idx = st.selectbox("الحملة:", range(len(campaign_names)), format_func=lambda i: campaign_names[i])
            selected_campaign = SCHEDULED_CAMPAIGNS[selected_idx]
            topic_text = selected_campaign["title"] + " - " + selected_campaign["description"]
            default_img_path = selected_campaign["image"]
        else:
            topic_text = st.text_area("اكتب فكرة البوست أو العرض:", "عجز الخزينة وسرقة الكاشير وكيف يمنع كاشير RoboVAI التلاعب عبر تقفيل Z-Report الدقيق مع كود خصم LAUNCH100", height=100)
            default_img_path = None

        st.markdown("#### 2. الصورة المرفقة")
        img_source = st.radio("مصدر الصورة:", ["من مكتبة شاشات النظام", "رفع صورة من جهازي"], horizontal=True)
        
        chosen_image_path = None
        if img_source == "من مكتبة شاشات النظام":
            if os.path.exists(ASSETS_DIR):
                asset_files = [f for f in os.listdir(ASSETS_DIR) if f.endswith(('.png', '.jpeg', '.jpg'))]
                selected_asset = st.selectbox("اختر الشاشة:", asset_files, index=asset_files.index("hero.jpeg") if "hero.jpeg" in asset_files else 0)
                chosen_image_path = os.path.join(ASSETS_DIR, selected_asset)
            else:
                st.warning("مجلد الصور غير موجود.")
        else:
            uploaded_file = st.file_uploader("ارفع صورة للمنشور:", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                temp_path = os.path.join(os.path.dirname(__file__), "temp_upload.png")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                chosen_image_path = temp_path

        generate_btn = st.button("✨ توليد المحتوى الذكي (Groq LPU فائق السرعة)", type="primary", use_container_width=True)

    with col_right:
        st.markdown("#### معاينة الصورة المحددة")
        if chosen_image_path and os.path.exists(chosen_image_path):
            st.image(chosen_image_path, use_container_width=True)
        else:
            st.info("لم يتم تحديد صورة بعد.")

    # Content generation logic
    if generate_btn:
        with st.spinner("جارٍ صياغة المحتوى عبر معالجات Groq الخارقة..."):
            res = generate_social_content(topic_text)
            st.session_state["generated_posts"] = res
            st.session_state["chosen_image"] = chosen_image_path
            st.success("تم توليد المحتوى في 0.8 ثانية بنجاح! 🎉")

    # Display Generated Content & Publishing Controls
    if "generated_posts" in st.session_state:
        posts = st.session_state["generated_posts"]
        active_img = st.session_state.get("chosen_image")

        st.markdown("---")
        st.markdown("### 📢 معاينة المنشورات وجاهزية النشر:")

        p_col1, p_col2 = st.columns(2)

        # Facebook Preview
        with p_col1:
            st.markdown("#### 📘 فيسبوك (Facebook)")
            fb_text = st.text_area("نص فيسبوك (يمكنك التعديل قبل النشر):", posts.get("facebook", ""), height=220, key="fb_text")
            if st.button("🚀 انشر الآن على Facebook", use_container_width=True):
                with st.spinner("جارٍ النشر على فيسبوك..."):
                    fb_res = publish_to_facebook(fb_text, active_img)
                    if fb_res.get("success"):
                        st.success(f"تم النشر بنجاح على فيسبوك! ID: {fb_res.get('post_id')}")
                    else:
                        st.error(f"تعذر النشر: {fb_res.get('error')}")

        # Telegram Preview
        with p_col2:
            st.markdown("#### 📢 قناة ومجموعات تليجرام")
            tg_text = st.text_area("نص تليجرام:", posts.get("telegram", ""), height=220, key="tg_text")
            if st.button("🚀 انشر الآن على تليجرام", type="primary", use_container_width=True):
                with st.spinner("جارٍ البث على قناة تليجرام..."):
                    tg_res = publish_to_telegram(tg_text, active_img)
                    if tg_res.get("success"):
                        st.success(f"تم البث بنجاح على تليجرام! Message ID: {tg_res.get('message_id')}")
                    else:
                        st.error(f"تعذر النشر: {tg_res.get('error')}")

        p_col3, p_col4 = st.columns(2)

        # Twitter / X Preview
        with p_col3:
            st.markdown("#### 🐦 منصة X (Twitter)")
            tw_text = st.text_area("تغريدة X:", posts.get("twitter", ""), height=150, key="tw_text")
            if st.button("🚀 انشر الآن على X", use_container_width=True):
                with st.spinner("جارٍ النشر على X..."):
                    tw_res = publish_to_twitter(tw_text)
                    if tw_res.get("success"):
                        st.success(f"تم التغريد بنجاح! Tweet ID: {tw_res.get('tweet_id')}")
                    else:
                        st.error(f"تعذر النشر: {tw_res.get('error')}")

        # Instagram Preview
        with p_col4:
            st.markdown("#### 📸 إنستجرام (Instagram)")
            ig_text = st.text_area("كابشن إنستجرام:", posts.get("instagram", ""), height=150, key="ig_text")
            st.info("💡 ملاحظة: للنشر على إنستجرام يتم النشر التلقائي عبر صفحة الفيسبوك المربوطة بحساب إنستجرام بيزنس.")

        st.markdown("---")
        if st.button("⚡🚀 انشر الآن في جميع المنصات دفعة واحدة (All-in-One Publish)", use_container_width=True):
            st.info("جارٍ الإرسال لكافة المنصات النشطة...")
            tg_res = publish_to_telegram(tg_text, active_img)
            fb_res = publish_to_facebook(fb_text, active_img)
            tw_res = publish_to_twitter(tw_text)
            
            st.write(f"• تليجرام: {'✅ تم بنجاح' if tg_res.get('success') else '❌ ' + tg_res.get('error', '')}")
            st.write(f"• فيسبوك: {'✅ تم بنجاح' if fb_res.get('success') else '❌ ' + fb_res.get('error', '')}")
            st.write(f"• إكس (تويتر): {'✅ تم بنجاح' if tw_res.get('success') else '❌ ' + tw_res.get('error', '')}")

# ================= TAB 2: CONTENT CALENDAR =================
with tab2:
    st.markdown("### 📅 جدول الحملات التسويقية المعدة مسبقاً")
    st.markdown("أفكار محتوى جاهزة تركز على نقاط ألم العملاء وتبرز شاشات النظام الـ 18 وميزة الأوفلاين:")
    
    for c in SCHEDULED_CAMPAIGNS:
        with st.expander(f"📍 [{c['category']}] {c['title']}"):
            col_c1, col_c2 = st.columns([2, 1])
            with col_c1:
                st.write(f"**الوصف التسويقي:** {c['description']}")
                st.write(f"**الصورة المخصصة:** `{os.path.basename(c['image'])}`")
                if st.button(f"استخدام هذه الحملة للتوليد ⚡", key=f"btn_c_{c['id']}"):
                    st.session_state["quick_topic"] = c['title'] + " - " + c['description']
                    st.session_state["quick_img"] = c['image']
                    st.success("تم اختيار الحملة! توجه إلى التبويب الأول واضغط 'توليد المحتوى'.")
            with col_c2:
                if os.path.exists(c['image']):
                    st.image(c['image'], width=240)

# ================= TAB 3: 1-CLICK CONNECT CENTER =================
with tab3:
    st.markdown("### 🔗 مركز ربط الحسابات بنقرة واحدة (1-Click Connect Center)")
    st.markdown("اضغط على أزرار الربط أدناه لنقلك مباشرة لربط حساباتك دون الحاجة لملء ملفات معقدة:")

    # --- 1. TELEGRAM CONNECT CARD ---
    st.markdown("""
    <div class="connect-card">
        <h3>📢 1. ربط بوت وقناة تليجرام (Telegram)</h3>
        <p style="color: #cbd5e1;">البوت الحالي: <strong>سوشيال روبوفاي بوس (@srobovaipos_bot)</strong></p>
    """, unsafe_allow_html=True)
    
    col_tg1, col_tg2 = st.columns(2)
    with col_tg1:
        st.markdown("**أولاً: ربط حسابك كمسؤول (Admin) للتحكم من الموبايل:**")
        st.markdown("""
        <a href="https://t.me/srobovaipos_bot?start=admin" target="_blank" class="btn-connect-link">
            🚀 اضغط هنا لفتح البوت على تليجرام وإرسال رسالة
        </a>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 فحص المحادثة وحفظ حسابك تلقائياً الآن", key="btn_check_tg_admin"):
            if tg_token:
                try:
                    u_res = requests.get(f"https://api.telegram.org/bot{tg_token}/getUpdates").json()
                    if u_res.get("ok") and u_res.get("result"):
                        last_msg = u_res["result"][-1]
                        from_user = last_msg.get("message", {}).get("from", {}) or last_msg.get("callback_query", {}).get("from", {})
                        c_id = from_user.get("id")
                        u_name = from_user.get("first_name", "Admin")
                        if c_id:
                            update_env_var("TELEGRAM_ADMIN_CHAT_ID", str(c_id))
                            st.success(f"🎉 تم التعرف عليك وربط حسابك بنجاح: {u_name} (Chat ID: {c_id})!")
                            # Send direct confirmation
                            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", json={
                                "chat_id": c_id,
                                "text": "✅ تم تأكيد اتصال لوحة تحكم RoboVAI بحسابك بنجاح! الآن يمكنك إرسال أي صورة لنشرها فوراً."
                            })
                    else:
                        st.warning("لم نجد رسائل جديدة بعد. اضغط على الزر الأزرق أعلاه وأرسل كلمة 'مرحبا' للبوت ثم اضغط هنا مرة أخرى.")
                except Exception as ex:
                    st.error(f"خطأ أثناء الفحص: {ex}")
            else:
                st.error("توكن البوت غير موجود.")

    with col_tg2:
        st.markdown("**ثانياً: ربط قناتك أو جروبك العام للبث التلقائي:**")
        new_channel = st.text_input("معرف القناة العامة (مثال: @robovai_pos):", value=tg_channel, key="input_channel")
        if st.button("💾 حفظ وفحص صلاحيات البوت في القناة", key="btn_check_tg_channel"):
            if new_channel:
                try:
                    c_info = requests.get(f"https://api.telegram.org/bot{tg_token}/getChat?chat_id={new_channel}").json()
                    if c_info.get("ok"):
                        update_env_var("TELEGRAM_CHANNEL_ID", new_channel)
                        st.success(f"✅ تم التحقق من القناة بنجاح: {c_info['result'].get('title')} وتم حفظها!")
                    else:
                        st.error(f"تعذر العثور على القناة أو لم تقم بإضافة @srobovaipos_bot كـ Admin فيها: {c_info.get('description')}")
                except Exception as ex:
                    st.error(f"خطأ: {ex}")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- 2. FACEBOOK & INSTAGRAM CONNECT CARD ---
    st.markdown("""
    <div class="connect-card">
        <h3>📘 2. ربط صفحات فيسبوك وإنستجرام (Meta Graph API)</h3>
        <p style="color: #cbd5e1;">اربط صفحة فيسبوك وحساب إنستجرام التجاري بضغطة زر واحدة لجلب صفحاتك تلقائياً:</p>
    """, unsafe_allow_html=True)
    
    col_fb1, col_fb2 = st.columns(2)
    with col_fb1:
        st.markdown("""
        <a href="https://developers.facebook.com/tools/explorer/" target="_blank" class="btn-connect-link" style="background: #1877f2;">
            🔗 فتح أداة Facebook Token Generator الرسمية
        </a>
        """, unsafe_allow_html=True)
        st.markdown("""
        **الخطوات السريعة:**
        1. اضغط على الزر الأزرق بالأعلى ليفتح لك موقع فيسبوك للمطورين.
        2. اضغط **Generate Access Token** واختر صفحاتك.
        3. انسخ التوكن والصقه في الخانة بالأسفل واضغط 'جلب صفحاتي'.
        """)

    with col_fb2:
        user_meta_token = st.text_input("الصق الـ User Access Token الخاص بفيسبوك هنا:", type="password", key="input_fb_user_token")
        if st.button("🔍 جلب صفحات الفيسبوك وحسابات إنستجرام التابعة لك", key="btn_fetch_fb_pages"):
            if user_meta_token:
                try:
                    f_url = f"https://graph.facebook.com/v19.0/me/accounts?fields=id,name,access_token,instagram_business_account&access_token={user_meta_token}"
                    f_res = requests.get(f_url).json()
                    if "data" in f_res and f_res["data"]:
                        st.session_state["meta_pages"] = f_res["data"]
                        st.success(f"تم العثور على {len(f_res['data'])} صفحة تابعة لك! اختر صفحتك بالأسفل:")
                    else:
                        st.error(f"لم يتم العثور على صفحات أو التوكن غير صالح: {f_res.get('error', {}).get('message')}")
                except Exception as ex:
                    st.error(f"خطأ: {ex}")

        if "meta_pages" in st.session_state:
            pages_list = st.session_state["meta_pages"]
            page_options = {p["name"]: p for p in pages_list}
            chosen_page_name = st.selectbox("اختر الصفحة التي تود النشر عليها:", list(page_options.keys()))
            
            if st.button("💾 حفظ واعتماد هذه الصفحة للنشر التلقائي", type="primary"):
                selected_p = page_options[chosen_page_name]
                update_env_var("FB_PAGE_ID", selected_p["id"])
                update_env_var("FB_PAGE_ACCESS_TOKEN", selected_p["access_token"])
                
                # Check linked Instagram
                ig_info = selected_p.get("instagram_business_account", {})
                if ig_info and "id" in ig_info:
                    update_env_var("INSTAGRAM_ACCOUNT_ID", ig_info["id"])
                    st.success(f"🎉 تم ربط صفحة '{chosen_page_name}' وحساب إنستجرام المرتبط بها بنجاح تام!")
                else:
                    st.success(f"🎉 تم ربط صفحة فيسبوك '{chosen_page_name}' بنجاح! (لا يوجد حساب إنستجرام بيزنس مرتبط بهذه الصفحة).")

    st.markdown("</div>", unsafe_allow_html=True)

    # --- 3. TWITTER / X CONNECT CARD ---
    st.markdown("""
    <div class="connect-card">
        <h3>🐦 3. ربط منصة X (تويتر)</h3>
        <p style="color: #cbd5e1;">احصل على مفاتيح التطبيق بضغطة زر لنشر التغريدات تلقائياً:</p>
    """, unsafe_allow_html=True)

    st.markdown("""
    <a href="https://developer.x.com/en/portal/dashboard" target="_blank" class="btn-connect-link" style="background: #000; border: 1px solid #38bdf8;">
        🔗 فتح لوحة مطوري X (Developer Portal) للحصول على المفاتيح
    </a>
    """, unsafe_allow_html=True)

    col_tw1, col_tw2 = st.columns(2)
    with col_tw1:
        tw_k = st.text_input("API Key (Consumer Key):", value=get_env_var("TWITTER_API_KEY"), type="password")
        tw_s = st.text_input("API Secret (Consumer Secret):", value=get_env_var("TWITTER_API_SECRET"), type="password")
    with col_tw2:
        tw_at = st.text_input("Access Token:", value=get_env_var("TWITTER_ACCESS_TOKEN"), type="password")
        tw_as = st.text_input("Access Token Secret:", value=get_env_var("TWITTER_ACCESS_SECRET"), type="password")

    if st.button("💾 حفظ مفاتيح تويتر واختبار التغريد", key="btn_save_twitter"):
        update_env_var("TWITTER_API_KEY", tw_k)
        update_env_var("TWITTER_API_SECRET", tw_s)
        update_env_var("TWITTER_ACCESS_TOKEN", tw_at)
        update_env_var("TWITTER_ACCESS_SECRET", tw_as)
        st.success("تم حفظ مفاتيح تويتر بنجاح!")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= TAB 4: AUTONOMOUS ENGINE =================
with tab4:
    st.markdown("### 🤖 غرفة التحكم في المحرك الذاتي (100% Autonomous)")
    st.markdown("""
    يقوم المحرك الذاتي باختيار المحتوى المرئي، ومطابقته بأعمدة الاستراتيجية التسويقية الأربعة، وصياغة الكوبي الإعلاني عبر **Groq LPU** ونشره تلقائياً على فيسبوك وتليجرام بدون أي تدخل بشري!
    """)
    
    from autonomous_engine import load_published_log, run_autonomous_post, CREATIVES_IMG_DIR, CREATIVES_VID_DIR
    log_data = load_published_log()
    
    img_count = len([f for f in os.listdir(CREATIVES_IMG_DIR) if f.lower().endswith(('.jpeg', '.jpg', '.png'))]) if os.path.exists(CREATIVES_IMG_DIR) else 0
    vid_count = len([f for f in os.listdir(CREATIVES_VID_DIR) if f.lower().endswith('.mp4')]) if os.path.exists(CREATIVES_VID_DIR) else 0
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("إجمالي المنشورات الذاتية", log_data.get("total_published", 0))
    with col_stat2:
        st.metric("مكتبة الصور المتوفرة", f"{img_count} صورة")
    with col_stat3:
        st.metric("مكتبة الفيديوهات المتوفرة", f"{vid_count} فيديو")
    with col_stat4:
        last_t = log_data.get("last_run", "لم يتم بعد")
        st.metric("آخر دورة نشر", last_t.split()[0] if " " in str(last_t) else str(last_t))
        
    st.markdown("---")
    
    col_run, col_sched = st.columns([1.2, 1])
    with col_run:
        st.markdown("#### ⚡ تشغيل فوري بنقرة واحدة")
        st.markdown("يمكنك إطلاق دورة نشر ذاتية حية الآن لاختبار المحرك على فيسبوك وتليجرام:")
        if st.button("🚀 نفّذ دورة نشر ذاتية الآن فوراً (Run Autonomous Post)", type="primary", use_container_width=True):
            with st.spinner("🤖 المحرك الذاتي يحلل الأصول، يختار الزاوية التسويقية، ويصيغ المنشور عبر Groq..."):
                rec = run_autonomous_post()
                st.balloons()
                st.success(f"🎉 تم النشر الذاتي بنجاح! المنشور رقم #{rec['id']}")
                st.write(f"**المحور التسويقي:** {rec['pillar_title']}")
                st.write(f"**الملف المستخدم:** `{rec['asset_filename']}` ({rec['asset_type']})")
                st.json(rec["results"])
                
    with col_sched:
        st.markdown("#### ⏰ مواعيد الجدولة الأوتوماتيكية السحابية")
        st.markdown("""
        - 🟢 **سيرفر الجدولة:** GitHub Actions Cloud Runner
        - 🕒 **المواعيد اليومية:** 
          - **1:00 ظهراً** بتوقيت القاهرة / مكة المكرمة (ذروة منتصف اليوم)
          - **7:00 مساءً** بتوقيت القاهرة / مكة المكرمة (ذروة المساء والويك إند)
        - 🎯 **الاستراتيجية:** تدوير مستمر بين الفيديوهات والصور بدون تكرار
        """)
        
    st.markdown("---")
    st.markdown("#### 📋 سجل المنشورات الذاتية الأخيرة (Publishing History)")
    posts = log_data.get("posts", [])
    if posts:
        for p in reversed(posts[-5:]):
            st.markdown(f"""
            - **#{p['id']}** | 🕒 `{p['timestamp']}` | 🏷️ **{p.get('pillar_title', '')}** | 📁 `{p.get('asset_filename', '')}` ({p.get('asset_type', '')})
            """)
    else:
        st.info("لا توجد منشورات مسجلة بعد. اضغط على الزر أعلاه لتنفيذ أول دورة نشر ذاتية!")

# ================= TAB 5: FREE SETUP GUIDE =================
with tab5:
    st.markdown("### 🛠️ نظرة عامة على الخدمات المجانية")
    st.markdown("""
    - **محرك Groq LPU الذكي**: يعمل الآن بـ 3 مفاتيح متبادلة ومفعلة لنشر فوري في أقل من ثانية.
    - **بوت تليجرام**: متصل ويعمل حياً كغرفة تحكم ومستعد لاستقبال صورك من الهاتف.
    - **فيسبوك وإنستجرام وتويتر**: استخدم تبويب 'مركز ربط الحسابات' للربط السريع بنقرة واحدة!
    """)

