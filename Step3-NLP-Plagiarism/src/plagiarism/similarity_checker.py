"""
ماژول بررسی شباهت متون
======================

این ماژول شباهت بین متون را محاسبه می‌کند.

Classes:
    SimilarityChecker: محاسبه شباهت

Example:
    >>> checker = SimilarityChecker()
    >>> similarity = checker.compare(text1, text2)
    >>> print(f"شباهت: {similarity}%")
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
import logging

from .embedder import TextEmbedder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityChecker:
    """
    کلاس بررسی شباهت متون
    
    این کلاس از Cosine Similarity برای محاسبه شباهت استفاده می‌کند.
    
    Attributes:
        embedder (TextEmbedder): تبدیل‌کننده متن به embedding
        threshold (float): آستانه تشخیص تقلب
        
    Example:
        >>> checker = SimilarityChecker()
        >>> result = checker.compare("متن اول", "متن دوم")
        >>> print(f"شباهت: {result['similarity']}%")
    """
    
    # آستانه‌های تشخیص
    THRESHOLDS = {
        'exact': 95,      # تقریباً یکسان
        'high': 80,       # شباهت بالا (مشکوک)
        'moderate': 60,   # شباهت متوسط
        'low': 40         # شباهت کم
    }
    
    def __init__(self, embedder: TextEmbedder = None, threshold: float = 70):
        """
        مقداردهی اولیه SimilarityChecker
        
        Args:
            embedder: instance از TextEmbedder
            threshold: آستانه تشخیص تقلب (پیش‌فرض 70%)
        """
        self.embedder = embedder or TextEmbedder()
        self.threshold = threshold
    
    def compare(self, text1: str, text2: str) -> Dict:
        """
        مقایسه دو متن
        
        Args:
            text1: متن اول
            text2: متن دوم
            
        Returns:
            dict: نتایج مقایسه
            {
                'similarity': float,
                'similarity_percent': float,
                'is_similar': bool,
                'level': str,
                'warning': str or None
            }
        """
        if not text1 or not text2:
            return self._empty_result()
        
        # تولید embeddings
        emb1 = self.embedder.embed(text1)
        emb2 = self.embedder.embed(text2)
        
        if not emb1['success'] or not emb2['success']:
            return self._empty_result()
        
        # محاسبه شباهت
        similarity = self._cosine_similarity(
            emb1['embedding'], 
            emb2['embedding']
        )
        
        similarity_percent = similarity * 100
        
        # تعیین سطح
        level = self._get_similarity_level(similarity_percent)
        
        # تولید هشدار
        warning = self._generate_warning(similarity_percent)
        
        return {
            'similarity': round(similarity, 4),
            'similarity_percent': round(similarity_percent, 2),
            'is_similar': similarity_percent >= self.threshold,
            'level': level,
            'warning': warning
        }
    
    def compare_with_database(
        self, 
        text: str, 
        database_embeddings: List[np.ndarray],
        database_ids: List[str] = None
    ) -> Dict:
        """
        مقایسه متن با پایگاه داده
        
        Args:
            text: متن جدید
            database_embeddings: لیست embeddings موجود
            database_ids: شناسه‌های اسناد (اختیاری)
            
        Returns:
            dict: نتایج مقایسه
        """
        if not text or not database_embeddings:
            return {
                'max_similarity': 0,
                'similar_documents': [],
                'is_plagiarized': False
            }
        
        # تولید embedding متن جدید
        new_embedding = self.embedder.embed(text)
        
        if not new_embedding['success']:
            return {
                'max_similarity': 0,
                'similar_documents': [],
                'is_plagiarized': False,
                'error': 'خطا در تولید embedding'
            }
        
        # تبدیل به array
        db_array = np.array(database_embeddings)
        new_array = new_embedding['embedding'].reshape(1, -1)
        
        # محاسبه شباهت با همه اسناد
        similarities = cosine_similarity(new_array, db_array)[0]
        
        # پیدا کردن اسناد مشابه
        similar_docs = []
        for i, sim in enumerate(similarities):
            sim_percent = sim * 100
            if sim_percent >= self.threshold:
                doc_id = database_ids[i] if database_ids else f"doc_{i}"
                similar_docs.append({
                    'id': doc_id,
                    'similarity': round(sim_percent, 2),
                    'level': self._get_similarity_level(sim_percent)
                })
        
        # مرتب‌سازی بر اساس شباهت
        similar_docs.sort(key=lambda x: x['similarity'], reverse=True)
        
        max_similarity = float(np.max(similarities)) * 100
        
        return {
            'max_similarity': round(max_similarity, 2),
            'similar_documents': similar_docs,
            'similar_count': len(similar_docs),
            'is_plagiarized': max_similarity >= self.threshold,
            'checked_against': len(database_embeddings)
        }
    
    def compare_sections(
        self, 
        sections1: Dict[str, str], 
        sections2: Dict[str, str]
    ) -> Dict[str, float]:
        """
        مقایسه بخش به بخش دو پروپوزال
        
        Args:
            sections1: بخش‌های پروپوزال اول
            sections2: بخش‌های پروپوزال دوم
            
        Returns:
            dict: شباهت هر بخش
        """
        section_similarities = {}
        
        common_sections = set(sections1.keys()) & set(sections2.keys())
        
        for section in common_sections:
            content1 = sections1[section]
            content2 = sections2[section]
            
            if content1 and content2:
                result = self.compare(content1, content2)
                section_similarities[section] = result['similarity_percent']
        
        return section_similarities
    
    def find_similar_passages(
        self, 
        text1: str, 
        text2: str, 
        window_size: int = 100
    ) -> List[Dict]:
        """
        یافتن بخش‌های مشابه بین دو متن
        
        Args:
            text1: متن اول
            text2: متن دوم
            window_size: اندازه پنجره (تعداد کاراکتر)
            
        Returns:
            list: لیست بخش‌های مشابه
        """
        similar_passages = []
        
        # تقسیم متن اول به پنجره‌ها
        windows1 = self._get_windows(text1, window_size)
        windows2 = self._get_windows(text2, window_size)
        
        if not windows1 or not windows2:
            return similar_passages
        
        # تولید embeddings
        emb1_result = self.embedder.embed_batch(windows1)
        emb2_result = self.embedder.embed_batch(windows2)
        
        if not emb1_result['success'] or not emb2_result['success']:
            return similar_passages
        
        # محاسبه ماتریس شباهت
        similarity_matrix = cosine_similarity(
            emb1_result['embeddings'],
            emb2_result['embeddings']
        )
        
        # یافتن جفت‌های با شباهت بالا
        for i in range(len(windows1)):
            for j in range(len(windows2)):
                sim = similarity_matrix[i][j] * 100
                if sim >= self.threshold:
                    similar_passages.append({
                        'text1_passage': windows1[i],
                        'text2_passage': windows2[j],
                        'text1_position': i * window_size,
                        'text2_position': j * window_size,
                        'similarity': round(sim, 2)
                    })
        
        # مرتب‌سازی
        similar_passages.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similar_passages[:20]  # حداکثر 20 مورد
    
    def _get_windows(self, text: str, window_size: int) -> List[str]:
        """تقسیم متن به پنجره‌ها"""
        windows = []
        step = window_size // 2  # overlap 50%
        
        for i in range(0, len(text) - window_size + 1, step):
            window = text[i:i + window_size]
            if len(window.strip()) > window_size // 2:
                windows.append(window)
        
        return windows
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        محاسبه شباهت کسینوسی
        
        Args:
            vec1: بردار اول
            vec2: بردار دوم
            
        Returns:
            float: شباهت (0 تا 1)
        """
        vec1 = vec1.reshape(1, -1)
        vec2 = vec2.reshape(1, -1)
        
        similarity = cosine_similarity(vec1, vec2)[0][0]
        
        return max(0, min(1, similarity))
    
    def _get_similarity_level(self, similarity_percent: float) -> str:
        """
        تعیین سطح شباهت
        
        Args:
            similarity_percent: درصد شباهت
            
        Returns:
            str: سطح شباهت
        """
        if similarity_percent >= self.THRESHOLDS['exact']:
            return 'یکسان'
        elif similarity_percent >= self.THRESHOLDS['high']:
            return 'بالا'
        elif similarity_percent >= self.THRESHOLDS['moderate']:
            return 'متوسط'
        elif similarity_percent >= self.THRESHOLDS['low']:
            return 'کم'
        else:
            return 'بسیار کم'
    
    def _generate_warning(self, similarity_percent: float) -> Optional[str]:
        """
        تولید پیام هشدار
        
        Args:
            similarity_percent: درصد شباهت
            
        Returns:
            str or None: پیام هشدار
        """
        if similarity_percent >= self.THRESHOLDS['exact']:
            return "⛔ احتمال بالای سرقت ادبی! این متن تقریباً مشابه است."
        elif similarity_percent >= self.THRESHOLDS['high']:
            return "⚠️ شباهت بالا! بررسی دقیق‌تر لازم است."
        elif similarity_percent >= self.THRESHOLDS['moderate']:
            return "💡 شباهت متوسط. ممکن است موضوعات مشترک داشته باشند."
        else:
            return None
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'similarity': 0,
            'similarity_percent': 0,
            'is_similar': False,
            'level': 'نامشخص',
            'warning': None
        }


# تست ماژول
if __name__ == "__main__":
    checker = SimilarityChecker()
    
    text1 = "این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان فارسی می‌پردازد"
    text2 = "این تحقیق درباره استفاده از یادگیری ماشین در NLP فارسی است"
    text3 = "من امروز به فروشگاه رفتم و میوه خریدم"
    
    print("=" * 60)
    print("📊 تست بررسی شباهت")
    print("=" * 60)
    
    # مقایسه متون مشابه
    result1 = checker.compare(text1, text2)
    print(f"\n📝 متن 1: {text1[:40]}...")
    print(f"📝 متن 2: {text2[:40]}...")
    print(f"📈 شباهت: {result1['similarity_percent']}%")
    print(f"📊 سطح: {result1['level']}")
    if result1['warning']:
        print(f"⚠️ {result1['warning']}")
    
    # مقایسه متون متفاوت
    result2 = checker.compare(text1, text3)
    print(f"\n📝 متن 1: {text1[:40]}...")
    print(f"📝 متن 3: {text3[:40]}...")
    print(f"📈 شباهت: {result2['similarity_percent']}%")
    print(f"📊 سطح: {result2['level']}")

