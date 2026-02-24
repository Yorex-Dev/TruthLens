import requests
import json
from config import Config
# استدعاء المحلل المحلي الذي برمجناه في الخطوة السابقة
from local_analyzer import LocalForensicAnalyzer 

class AIDetector:
    """
    عقل المنصة: يتصل بالـ APIs العالمية، ومعزز بمحرك فحص جنائي محلي للطوارئ.
    """

    def __init__(self):
        self.api_user = Config.SIGHTENGINE_API_USER
        self.api_secret = Config.SIGHTENGINE_API_SECRET
        self.endpoint = 'https://api.sightengine.com/1.0/check.json'
        # تهيئة المحرك المحلي
        self.local_engine = LocalForensicAnalyzer()

    def analyze_image(self, image_path):
        """تحليل صورة واحدة: يحاول عبر الـ API أولاً، وإذا تعطل ينتقل للتحليل الجنائي المحلي"""
        params = {
            'models': 'genai,deepfake',
            'api_user': self.api_user,
            'api_secret': self.api_secret
        }
        
        try:
            with open(image_path, 'rb') as image_file:
                files = {'media': image_file}
                response = requests.post(self.endpoint, files=files, data=params, timeout=10)
            
            output = json.loads(response.text)
            
            # إذا استجاب الـ API بنجاح نعيد النتيجة فوراً
            if output.get('status') == 'success':
                return output
            else:
                # إذا كانت هناك مشكلة في الحساب أو مفتاح الـ API، نرفع خطأ للانتقال للمحرك المحلي
                raise Exception(output.get('error', {}).get('message', 'API Error'))

        except Exception as e:
            # --- منطقة التحليل الجنائي المحلي (عند تعطل الـ API) ---
            print(f"⚠️ الـ API معطل أو حدث خطأ: {e}. يتم الآن استخدام التحليل الجنائي المحلي...")
            local_res = self.local_engine.get_local_verdict(image_path)
            
            # نقوم بصياغة النتيجة المحلية بنفس هيكلية الـ API لضمان عدم تعطل الوظائف الأخرى
            return {
                "status": "success",
                "type": {"ai_generated": local_res['local_score'] / 100}, # تحويل النسبة لـ Decimal
                "deepfake": {"detected_faces": [{"score": local_res['local_score'] / 100}]},
                "is_local": True # علامة إضافية أن التحليل تم محلياً
            }

    def get_final_verdict(self, frames_paths):
        """جمع نتائج تحليل عدة إطارات من فيديو واحد وإعطاء حكم نهائي (بدون أي تعديل على الوظيفة)"""
        results = []
        
        for frame in frames_paths:
            analysis = self.analyze_image(frame)
            if "error" in analysis and not analysis.get("status") == "success":
                continue
            
            # فحص نتيجة الصور المولدة (GenAI)
            genai_score = analysis.get('type', {}).get('ai_generated', 0)
            
            # فحص نتيجة تزييف الوجوه (Deepfake)
            deepfake_score = 0
            if 'deepfake' in analysis:
                faces = analysis['deepfake'].get('detected_faces', [])
                if faces:
                    deepfake_score = max([face['score'] for face in faces])
            
            # نأخذ القيمة الأعلى بين نوعي التزييف
            current_max = max(genai_score, deepfake_score)
            results.append(current_max)
            
        if not results:
            return {"status": "Error", "score": 0, "message": "لم نتمكن من تحليل محتوى الفيديو."}

        # الحكم النهائي بناءً على أعلى نتيجة تم رصدها
        final_score = max(results)
        
        if final_score >= Config.AI_DETECTION_THRESHOLD:
            message = "⚠️ تحذير: هذا المحتوى منشأ أو معدل بواسطة الذكاء الاصطناعي بنسبة كبيرة!"
            status = "Fake"
        elif final_score >= 0.5:
            message = "🟡 انتبه: هناك شكوك في هذا المحتوى، قد يكون معدلاً."
            status = "Suspicious"
        else:
            message = "✅ على الأرجح هذا المحتوى حقيقي ولم يتم إنشاؤه بالذكاء الاصطناعي."
            status = "Real"

        return {
            "status": status,
            "score": round(final_score * 100, 2),
            "message": message
        }
