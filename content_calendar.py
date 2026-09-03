import os

local_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "images"))
parent_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "LandingPage", "assets", "images"))
ASSETS_DIR = local_assets if os.path.exists(local_assets) else parent_assets

SCHEDULED_CAMPAIGNS = [
    {
        "id": 1,
        "title": "حماية الخزينة ومطابقة الـ Z-Report بالسنتيم",
        "description": "كيف يمنع الكاشير التلاعب وسرقة النقدية ويطابق الدرج اليومي بالسنتيم",
        "image": os.path.join(ASSETS_DIR, "15-reports.png"),
        "category": "الأمان المالي"
    },
    {
        "id": 2,
        "title": "جرد البضاعة والمخزن بكاميرا الموبايل WMS",
        "description": "وفر 15 ألف جنيه في أجهزة الجرد، واجرد كل الباركود من موبايلك في ثوانٍ",
        "image": os.path.join(ASSETS_DIR, "09-inventory.png"),
        "category": "المخازن"
    },
    {
        "id": 3,
        "title": "العمل 100% أوفلاين بدون نت وإنهاء الفاتورة في ثانيتين",
        "description": "النت فصل وطابور الزبائن واقف؟ الحل مع كاشير أوفلاين صلب 0% Lag",
        "image": os.path.join(ASSETS_DIR, "03-pos.jpeg"),
        "category": "السرعة والثبات"
    },
    {
        "id": 4,
        "title": "راقب محلك من جيبك عبر بوت تليجرام التلقائي",
        "description": "إشعارات حية بكل فاتورة ومبيعات اليوم وإغلاق الوردية مباشرة على هاتفك",
        "image": os.path.join(ASSETS_DIR, "22-telegram-alerts.png"),
        "category": "إدارة عن بعد"
    },
    {
        "id": 5,
        "title": "عرض الإطلاق الحصري لأول 100 عميل بكود LAUNCH100",
        "description": "ترخيص تمليك دائم مدى الحياة بدون اشتراكات شهرية مع كود خصم إضافي",
        "image": os.path.join(ASSETS_DIR, "hero.jpeg"),
        "category": "عروض وخصومات"
    },
    {
        "id": 6,
        "title": "انقل أصنافك من أي إكسيل قديم في ثوانٍ",
        "description": "الاستيراد الذكي للأصناف والباركود والأسعار بدون أي إعادة إدخال يدوية",
        "image": os.path.join(ASSETS_DIR, "21-smart-import.png"),
        "category": "سهولة الاستخدام"
    },
    {
        "id": 7,
        "title": "لوحة متابعة المبيعات وساعات الذروة بالمتصفح",
        "description": "افتح متصفح لابتوبك في المكتب وتابع أداء الكاشيرات والمبيعات الحية",
        "image": os.path.join(ASSETS_DIR, "20-web-dashboard.png"),
        "category": "إحصائيات الإدارة"
    },
    {
        "id": 8,
        "title": "نظام صالات البلايستيشن وحساب الوقت والمشاريب",
        "description": "عدادات وقت دقيقة بالدقيقة والتعريفة الفردي والزوجي مع إضافة الطلبات آلياً",
        "image": os.path.join(ASSETS_DIR, "04-sessions.png"),
        "category": "أنشطة متخصصة"
    }
]
