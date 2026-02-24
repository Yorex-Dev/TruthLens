import cv2
import numpy as np
from PIL import Image, ImageChops
import os

class LocalForensicAnalyzer:
    """
    محرك تحليل جنائي محلي يعمل بدون إنترنت (Offline) 
    يكشف التلاعب في الترددات وضغط البكسلات.
    """

    @staticmethod
    def analyze_ela(image_path, quality=90):
        """
        تحليل مستوى الخطأ (Error Level Analysis):
        يكشف إذا كانت أجزاء من الصورة تم حفظها بمستويات ضغط مختلفة (دليل على التعديل).
        """
        temp_ela = "temp_ela.jpg"
        original = Image.open(image_path).convert('RGB')
        
        # حفظ الصورة بجودة محددة ثم مقارنتها بالأصل
        original.save(temp_ela, 'JPEG', quality=quality)
        temporary = Image.open(temp_ela)
        
        # حساب الفارق بين الصورة الأصلية والمضغوطة
        ela_image = ImageChops.difference(original, temporary)
        
        # تعزيز الفوارق لتصبح مرئية
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        if max_diff == 0: max_diff = 1
        scale = 255.0 / max_diff
        
        ela_image = ImageChops.constant(ela_image, scale)
        
        # حساب متوسط الفارق (كدرجة اشتباه)
        stat = np.array(ela_image).mean()
        os.remove(temp_ela)
        return round(stat, 2)

    @staticmethod
    def analyze_frequency_domain(image_path):
        """
        التحليل الطيفي (FFT):
        كشف الأنماط المتكررة (Artifacts) التي تتركها محركات الذكاء الاصطناعي في خلايا الصورة.
        """
        img = cv2.imread(image_path, 0) # قراءة الصورة باللون الرمادي
        f = np.fft.fft2(img)           # تحويل فورييه السريع
        fshift = np.fft.fftshift(f)    # نقل الترددات المنخفضة للمركز
        
        magnitude_spectrum = 20 * np.log(np.abs(fshift))
        
        # الصور الطبيعية لها توزيع ترددي ناعم، صور الذكاء الاصطناعي لها "نقاط" حادة
        mean_val = np.mean(magnitude_spectrum)
        std_val = np.std(magnitude_spectrum)
        
        # درجة الاشتباه تعتمد على انحراف الترددات
        score = (std_val / mean_val) * 10 
        return round(score, 2)

    def get_local_verdict(self, image_path):
        """إعطاء حكم محلي سريع في حال تعطل الـ API"""
        ela_score = self.analyze_ela(image_path)
        freq_score = self.analyze_frequency_domain(image_path)
        
        # دمج النتائج (منطق تجريبي)
        combined_score = (ela_score + freq_score) / 2
        
        status = "Safe"
        if combined_score > 15: status = "Highly Suspicious"
        elif combined_score > 8: status = "Check Required"
        
        return {
            "local_score": combined_score,
            "status": status,
            "details": f"ELA: {ela_score}, Spectral: {freq_score}"
        }
