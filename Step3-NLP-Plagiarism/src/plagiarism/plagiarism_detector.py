"""
ماژول یکپارچه تشخیص تقلب
========================

این ماژول تمام قابلیت‌های تشخیص تقلب را یکپارچه می‌کند.

Classes:
    PlagiarismDetector: تشخیص‌دهنده اصلی تقلب

Example:
    >>> detector = PlagiarismDetector()
    >>> result = detector.check(proposal_text)
    >>> print(f"نمره اصالت: {result['originality_score']}")
"""

import os
import json
from typing import Dict, List, Optional, Union
import numpy as np
from datetime import datetime
import logging

from .embedder import TextEmbedder
from .similarity_checker import SimilarityChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlagiarismDetector:
    """
    کلاس یکپارچه تشخیص تقلب
    
    این کلاس تمام مراحل تشخیص تقلب را انجام می‌دهد:
    1. تبدیل متن به embedding
    2. مقایسه با پایگاه داده
    3. محاسبه نمره اصالت
    4. ذخیره برای مقایسه‌های آینده
    
    Attributes:
        embedder (TextEmbedder): تبدیل‌کننده متن
        checker (SimilarityChecker): بررسی‌کننده شباهت
        database (list): پایگاه داده embeddings
        threshold (float): آستانه تشخیص
        
    Example:
        >>> detector = PlagiarismDetector()
        >>> result = detector.check(text)
        >>> print(f"اصالت: {result['originality_score']}%")
    """
    
    def __init__(
        self, 
        threshold: float = 70,
        database_path: str = None
    ):
        """
        مقداردهی اولیه PlagiarismDetector
        
        Args:
            threshold: آستانه تشخیص تقلب (پیش‌فرض 70%)
            database_path: مسیر فایل پایگاه داده
        """
        self.embedder = TextEmbedder()
        self.checker = SimilarityChecker(self.embedder, threshold)
        self.threshold = threshold
        self.database_path = database_path
        
        # پایگاه داده در حافظه
        self.database = []  # لیست embeddings
        self.metadata = []  # متادیتای هر سند
        
        # بارگذاری پایگاه داده
        if database_path and os.path.exists(database_path):
            self._load_database()
    
    def check(self, text: str, proposal_id: str = None) -> Dict:
        """
        بررسی کامل تقلب
        
        Args:
            text: متن پروپوزال
            proposal_id: شناسه پروپوزال (اختیاری)
            
        Returns:
            dict: نتایج کامل بررسی
            {
                'originality_score': float,
                'plagiarism_percentage': float,
                'is_original': bool,
                'max_similarity': float,
                'similar_documents': list,
                'checked_against': int,
                'details': dict
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # تولید embedding
        embedding_result = self.embedder.embed(text)
        
        if not embedding_result['success']:
            return self._empty_result(error="خطا در تولید embedding")
        
        embedding = embedding_result['embedding']
        text_hash = embedding_result['text_hash']
        
        # بررسی تکراری بودن
        if self._is_duplicate(text_hash):
            return {
                'originality_score': 0,
                'plagiarism_percentage': 100,
                'is_original': False,
                'max_similarity': 100,
                'similar_documents': [{'id': 'exact_match', 'similarity': 100}],
                'checked_against': len(self.database),
                'warning': '⛔ این متن قبلاً ثبت شده است!',
                'details': {'is_duplicate': True}
            }
        
        # مقایسه با پایگاه داده
        if self.database:
            db_embeddings = [d['embedding'] for d in self.database]
            db_ids = [d['id'] for d in self.metadata]
            
            comparison = self.checker.compare_with_database(
                text, db_embeddings, db_ids
            )
            
            max_similarity = comparison['max_similarity']
            similar_docs = comparison['similar_documents']
        else:
            max_similarity = 0
            similar_docs = []
        
        # محاسبه نمره اصالت
        originality_score = max(0, 100 - max_similarity)
        
        # تعیین وضعیت
        is_original = max_similarity < self.threshold
        
        # تولید هشدار
        warning = self._generate_warning(max_similarity)
        
        return {
            'originality_score': round(originality_score, 2),
            'plagiarism_percentage': round(max_similarity, 2),
            'is_original': is_original,
            'max_similarity': round(max_similarity, 2),
            'similar_documents': similar_docs[:5],  # حداکثر 5 مورد
            'checked_against': len(self.database),
            'warning': warning,
            'details': {
                'text_hash': text_hash,
                'embedding_dimension': len(embedding),
                'threshold': self.threshold,
                'checked_at': datetime.now().isoformat()
            }
        }
    
    def check_and_store(
        self, 
        text: str, 
        proposal_id: str,
        metadata: Dict = None
    ) -> Dict:
        """
        بررسی تقلب و ذخیره در پایگاه داده
        
        Args:
            text: متن پروپوزال
            proposal_id: شناسه یکتای پروپوزال
            metadata: اطلاعات اضافی
            
        Returns:
            dict: نتایج بررسی
        """
        # بررسی
        result = self.check(text, proposal_id)
        
        # ذخیره
        if result['is_original']:
            self.add_to_database(text, proposal_id, metadata)
            result['stored'] = True
        else:
            result['stored'] = False
            result['store_message'] = 'به دلیل شباهت بالا، ذخیره نشد'
        
        return result
    
    def add_to_database(
        self, 
        text: str, 
        proposal_id: str,
        metadata: Dict = None
    ) -> bool:
        """
        افزودن به پایگاه داده
        
        Args:
            text: متن پروپوزال
            proposal_id: شناسه
            metadata: اطلاعات اضافی
            
        Returns:
            bool: موفقیت
        """
        # تولید embedding
        embedding_result = self.embedder.embed(text)
        
        if not embedding_result['success']:
            logger.error("خطا در افزودن به پایگاه داده")
            return False
        
        # افزودن به لیست
        self.database.append({
            'embedding': embedding_result['embedding'],
            'text_hash': embedding_result['text_hash']
        })
        
        self.metadata.append({
            'id': proposal_id,
            'added_at': datetime.now().isoformat(),
            **(metadata or {})
        })
        
        logger.info(f"پروپوزال {proposal_id} به پایگاه داده اضافه شد")
        
        # ذخیره خودکار
        if self.database_path:
            self._save_database()
        
        return True
    
    def get_originality_score_weighted(
        self, 
        score: float, 
        weight: float = 5
    ) -> float:
        """
        تبدیل نمره اصالت به وزن نهایی
        
        نمره اصالت = 5% از نمره کل پروپوزال
        
        Args:
            score: نمره اصالت (0-100)
            weight: وزن در نمره کل (پیش‌فرض 5%)
            
        Returns:
            float: نمره وزن‌دار
        """
        return (score / 100) * weight
    
    def _is_duplicate(self, text_hash: str) -> bool:
        """بررسی تکراری بودن"""
        for item in self.database:
            if item.get('text_hash') == text_hash:
                return True
        return False
    
    def _generate_warning(self, similarity: float) -> Optional[str]:
        """تولید پیام هشدار"""
        if similarity >= 90:
            return "⛔ احتمال بسیار بالای سرقت ادبی!"
        elif similarity >= 70:
            return "⚠️ شباهت بالا با اسناد موجود. بررسی دقیق‌تر لازم است."
        elif similarity >= 50:
            return "💡 شباهت متوسط. احتمالاً موضوعات مشترک دارند."
        else:
            return None
    
    def _save_database(self) -> None:
        """ذخیره پایگاه داده"""
        if not self.database_path:
            return
        
        try:
            data = {
                'embeddings': [
                    {
                        'embedding': d['embedding'].tolist(),
                        'text_hash': d['text_hash']
                    }
                    for d in self.database
                ],
                'metadata': self.metadata,
                'threshold': self.threshold,
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.database_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            
            logger.info(f"پایگاه داده ذخیره شد: {self.database_path}")
            
        except Exception as e:
            logger.error(f"خطا در ذخیره پایگاه داده: {e}")
    
    def _load_database(self) -> None:
        """بارگذاری پایگاه داده"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.database = [
                {
                    'embedding': np.array(d['embedding']),
                    'text_hash': d['text_hash']
                }
                for d in data.get('embeddings', [])
            ]
            
            self.metadata = data.get('metadata', [])
            
            logger.info(
                f"پایگاه داده بارگذاری شد: "
                f"{len(self.database)} سند"
            )
            
        except Exception as e:
            logger.error(f"خطا در بارگذاری پایگاه داده: {e}")
    
    def _empty_result(self, error: str = None) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'originality_score': 100,
            'plagiarism_percentage': 0,
            'is_original': True,
            'max_similarity': 0,
            'similar_documents': [],
            'checked_against': 0,
            'warning': None,
            'error': error,
            'details': {}
        }
    
    def get_statistics(self) -> Dict:
        """آمار پایگاه داده"""
        return {
            'total_documents': len(self.database),
            'threshold': self.threshold,
            'database_path': self.database_path
        }


# تست ماژول
if __name__ == "__main__":
    detector = PlagiarismDetector(threshold=70)
    
    # متون تست
    text1 = """
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان طبیعی فارسی می‌پردازد.
    هدف اصلی طراحی یک سیستم هوشمند برای تحلیل احساسات متون فارسی است.
    روش‌شناسی شامل استفاده از شبکه‌های عصبی عمیق و مدل‌های ترنسفورمر است.
    """
    
    text2 = """
    این تحقیق درباره استفاده از یادگیری ماشین در NLP فارسی انجام شده است.
    هدف ساخت یک سیستم برای تحلیل احساسات در متن‌های فارسی می‌باشد.
    از شبکه‌های عصبی و ترنسفورمرها استفاده شده است.
    """
    
    text3 = """
    بررسی تأثیر آموزش از راه دور بر یادگیری دانش‌آموزان در دوران کرونا
    یکی از موضوعات مهم پژوهشی است که در این مطالعه به آن پرداخته شده است.
    """
    
    print("=" * 60)
    print("🔍 تست تشخیص تقلب")
    print("=" * 60)
    
    # افزودن اولین سند
    detector.add_to_database(text1, "PROP-001", {"title": "پروپوزال اول"})
    print(f"\n✅ پروپوزال اول به پایگاه داده اضافه شد")
    
    # بررسی متن مشابه
    result2 = detector.check(text2, "PROP-002")
    print(f"\n📊 بررسی پروپوزال دوم (مشابه):")
    print(f"   نمره اصالت: {result2['originality_score']}%")
    print(f"   شباهت: {result2['max_similarity']}%")
    print(f"   اصیل: {result2['is_original']}")
    if result2['warning']:
        print(f"   ⚠️ {result2['warning']}")
    
    # بررسی متن متفاوت
    result3 = detector.check(text3, "PROP-003")
    print(f"\n📊 بررسی پروپوزال سوم (متفاوت):")
    print(f"   نمره اصالت: {result3['originality_score']}%")
    print(f"   شباهت: {result3['max_similarity']}%")
    print(f"   اصیل: {result3['is_original']}")
    
    # آمار
    stats = detector.get_statistics()
    print(f"\n📈 آمار پایگاه داده:")
    print(f"   تعداد اسناد: {stats['total_documents']}")
    print(f"   آستانه: {stats['threshold']}%")

