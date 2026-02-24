import os
from dotenv import load_dotenv

# تحميل المتغيرات من ملف .env إذا كان موجوداً
load_dotenv()

class Config:
    """
    إعدادات المنصة ومفاتيح الوصول للـ APIs العالمية.
    """
    # مفاتيح Sightengine (سجل في sightengine.com للحصول عليها)
    SIGHTENGINE_API_USER = os.getenv("SIGHTENGINE_USER", "713672116")
    SIGHTENGINE_API_SECRET = os.getenv("SIGHTENGINE_SECRET", "sRDKvcHyjfiWSvzeZKbPBzGHYCdLnins")

    # إعدادات المعالجة
    TEMP_DIR = "temp_assets"      # المجلد المؤقت لحفظ الفيديوهات المحملة
    MAX_VIDEO_SIZE_MB = 50        # الحد الأقصى لحجم الفيديو (لحماية الخادم)
    
    # إعدادات الكشف (Thresholds)
    # إذا كانت النسبة أعلى من 0.8، نعتبره "تزييف مؤكد"
    AI_DETECTION_THRESHOLD = 0.8  

    @staticmethod
    def initialize_dirs():
        """إنشاء المجلدات اللازمة للعمل في بداية التشغيل"""
        if not os.path.exists(Config.TEMP_DIR):
            os.makedirs(Config.TEMP_DIR)
            print(f"[*] Created directory: {Config.TEMP_DIR}")

# تنفيذ إنشاء المجلدات فور استدعاء الملف
Config.initialize_dirs()
