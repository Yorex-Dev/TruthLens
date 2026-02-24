import cv2
import os
import yt_dlp
from config import Config
from PIL import Image

class MediaProcessor:
    """
    مسؤول عن تحميل الميديا من الروابط ومعالجتها تقنياً.
    """

    @staticmethod
    def download_video(url):
        """تحميل الفيديو من رابط (YouTube, Twitter, etc.)"""
        try:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': f'{Config.TEMP_DIR}/video_%(id)s.%(ext)s',
                'max_filesize': Config.MAX_VIDEO_SIZE_MB * 1024 * 1024,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return filename
        except Exception as e:
            print(f"[!] Error downloading video: {e}")
            return None

    @staticmethod
    def extract_frames(video_path, num_frames=3):
        """استخراج عدد معين من الإطارات من الفيديو لتحليلها"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # نختار إطارات موزعة على طول الفيديو (البداية، المنتصف، النهاية)
        for i in range(num_frames):
            frame_id = int((total_frames / (num_frames + 1)) * (i + 1))
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            ret, frame = cap.read()
            if ret:
                # تحويل الإطار من OpenCV (BGR) إلى PIL (RGB)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                
                # حفظ الإطار مؤقتاً
                frame_path = f"{Config.TEMP_DIR}/frame_{i}.jpg"
                img.save(frame_path)
                frames.append(frame_path)
        
        cap.release()
        return frames

    @staticmethod
    def cleanup(files):
        """حذف الملفات المؤقتة بعد الانتهاء للحفاظ على مساحة الجهاز"""
        for file in files:
            if os.path.exists(file):
                os.remove(file)
