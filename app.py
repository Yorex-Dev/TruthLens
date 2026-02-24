import streamlit as st
from processor import MediaProcessor
from detector import AIDetector
from config import Config
import time

# إعدادات الصفحة (تظهر في تبويب المتصفح)
st.set_page_config(page_title="TruthLens AI | كاشف التزييف العالمي", page_icon="🔍", layout="wide")

# تصميم الواجهة الرئيسية
st.title("🔍 TruthLens AI")
st.subheader("المنصة العالمية للكشف عن تزييف الفيديو والذكاء الاصطناعي")
st.markdown("---")

# القائمة الجانبية (Sidebar) للتعليمات
with st.sidebar:
    st.header("حول المنصة")
    st.info("هذه المنصة تستخدم تقنيات الرؤية الحاسوبية المتقدمة لتحليل الإطارات واكتشاف التلاعب الرقمي.")
    st.warning("ملاحظة: تأكد من وضع رابط فيديو مباشر (YouTube, X, etc.)")

# منطقة الإدخال
url = st.text_input("أدخل رابط الفيديو المراد فحصه هنا:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("تحليل المحتوى الآن 🚀"):
    if not url:
        st.error("رجاءً ضع رابطاً أولاً!")
    else:
        # بدء عملية التحليل
        with st.status("جاري العمل على كشف الحقيقة...", expanded=True) as status:
            
            # 1. تحميل الفيديو
            st.write("📥 جاري تحميل الفيديو ومعالجته...")
            video_path = MediaProcessor.download_video(url)
            
            if not video_path:
                st.error("فشل تحميل الفيديو. تأكد من الرابط.")
                status.update(label="فشلت العملية", state="error")
            else:
                # 2. استخراج الإطارات
                st.write("🎞️ جاري تقطيع الفيديو وتحليل البصمات الرقمية...")
                frames = MediaProcessor.extract_frames(video_path)
                
                # 3. التحليل عبر الذكاء الاصطناعي
                st.write("🧠 جاري الفحص باستخدام محركات الذكاء الاصطناعي...")
                detector = AIDetector()
                verdict = detector.get_final_verdict(frames)
                
                # إتمام العملية
                status.update(label="اكتمل التحليل!", state="complete", expanded=False)

                # عرض النتائج بشكل بصري مبهر
                st.markdown("---")
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.metric(label="نسبة التلاعب المكتشفة", value=f"{verdict['score']}%")
                
                with col2:
                    if verdict['status'] == "Fake":
                        st.error(f"### النتيجة: {verdict['status']}")
                    elif verdict['status'] == "Suspicious":
                        st.warning(f"### النتيجة: {verdict['status']}")
                    else:
                        st.success(f"### النتيجة: {verdict['status']}")
                    
                    st.write(verdict['message'])

                # عرض الإطارات التي تم فحصها لزيادة المصداقية
                st.write("#### الإطارات التي خضعت للفحص:")
                cols = st.columns(len(frames))
                for i, frame_path in enumerate(frames):
                    cols[i].image(frame_path, caption=f"Frame {i+1}")

                # تنظيف الملفات المؤقتة
                MediaProcessor.cleanup([video_path] + frames)

# تذييل الصفحة
st.markdown("---")
st.caption("تحدي الـ 24 ساعة - مبرمج بواسطة خبير بايثون وزميله الطموح.")
