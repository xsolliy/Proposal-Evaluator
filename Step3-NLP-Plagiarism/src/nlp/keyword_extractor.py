"""
ماژول استخراج کلمات کلیدی
=========================

این ماژول کلمات کلیدی را از متن فارسی استخراج می‌کند.

Classes:
    KeywordExtractor: استخراج‌کننده کلیدواژه با KeyBERT

Example:
    >>> extractor = KeywordExtractor()
    >>> keywords = extractor.extract("متن پروپوزال...")
    >>> print(keywords)
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KeywordExtractor:
    """
    کلاس استخراج کلمات کلیدی از متن فارسی
    
    این کلاس از KeyBERT با مدل فارسی برای استخراج کلیدواژه استفاده می‌کند.
    همچنین روش‌های آماری (TF-IDF, YAKE) را پشتیبانی می‌کند.
    
    Attributes:
        model_name (str): نام مدل Sentence-BERT
        keybert_model: مدل KeyBERT
        
    Example:
        >>> extractor = KeywordExtractor()
        >>> result = extractor.extract("این پژوهش درباره یادگیری ماشین است")
        >>> print(result['keywords'])
    """
    
    # مدل پیش‌فرض فارسی
    DEFAULT_MODEL = 'm3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens'
    
    # کلمات ایست فارسی (Stopwords)
    PERSIAN_STOPWORDS = {
        'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'است', 'برای',
        'آن', 'یک', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'شد', 'شده',
        'می', 'گفت', 'او', 'ما', 'اما', 'یا', 'اگر', 'هر', 'بود', 'چه',
        'همه', 'باید', 'دارد', 'پس', 'ها', 'های', 'شود', 'کند', 'وی',
        'بین', 'کنند', 'هستند', 'بوده', 'دیگر', 'همچنین', 'توسط', 'چون',
        'بی', 'می‌شود', 'می‌کند', 'می‌توان', 'کردن', 'شدن', 'بودن',
        'داشتن', 'آنها', 'ایشان', 'چند', 'چنین', 'چنان', 'مانند', 'مثل',
        'پیش', 'زیر', 'روی', 'جز', 'حتی', 'فقط', 'تنها', 'دیگری',
    }
    
    def __init__(self, model_name: str = None, use_keybert: bool = True):
        """
        مقداردهی اولیه KeywordExtractor
        
        Args:
            model_name: نام مدل (پیش‌فرض: مدل فارسی)
            use_keybert: استفاده از KeyBERT (نیاز به نصب)
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.use_keybert = use_keybert
        self.keybert_model = None
        
        if use_keybert:
            self._init_keybert()
    
    def _init_keybert(self) -> None:
        """راه‌اندازی KeyBERT"""
        try:
            from keybert import KeyBERT
            logger.info(f"بارگذاری مدل KeyBERT: {self.model_name}")
            self.keybert_model = KeyBERT(self.model_name)
            logger.info("KeyBERT با موفقیت بارگذاری شد")
        except ImportError:
            logger.warning("KeyBERT نصب نیست. از روش آماری استفاده می‌شود.")
            self.use_keybert = False
        except Exception as e:
            logger.warning(f"خطا در بارگذاری KeyBERT: {e}")
            self.use_keybert = False
    
    def extract(
        self, 
        text: str, 
        top_n: int = 15,
        ngram_range: Tuple[int, int] = (1, 3),
        diversity: float = 0.5
    ) -> Dict:
        """
        استخراج کلمات کلیدی از متن
        
        Args:
            text: متن ورودی
            top_n: تعداد کلیدواژه‌های برتر
            ngram_range: محدوده n-gram (1,3 یعنی 1 تا 3 کلمه)
            diversity: تنوع کلیدواژه‌ها (0 تا 1)
            
        Returns:
            dict: نتایج استخراج
            {
                'keywords': list of (keyword, score),
                'top_keywords': list of str,
                'method': str,
                'keyword_count': int
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # پیش‌پردازش متن
        cleaned_text = self._preprocess(text)
        
        # استخراج کلیدواژه
        if self.use_keybert and self.keybert_model:
            keywords = self._extract_with_keybert(
                cleaned_text, top_n, ngram_range, diversity
            )
            method = 'KeyBERT'
        else:
            keywords = self._extract_statistical(cleaned_text, top_n)
            method = 'Statistical (TF)'
        
        # فیلتر کلمات ایست
        keywords = self._filter_stopwords(keywords)
        
        # محدود کردن به top_n
        keywords = keywords[:top_n]
        
        return {
            'keywords': keywords,
            'top_keywords': [kw[0] for kw in keywords],
            'method': method,
            'keyword_count': len(keywords)
        }
    
    def _preprocess(self, text: str) -> str:
        """
        پیش‌پردازش متن
        
        Args:
            text: متن خام
            
        Returns:
            str: متن پاک‌سازی شده
        """
        # حذف اعداد انگلیسی
        text = re.sub(r'[0-9]+', '', text)
        
        # حذف کاراکترهای خاص
        text = re.sub(r'[^\u0600-\u06FF\s\u200c]', ' ', text)
        
        # حذف فاصله‌های اضافی
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_with_keybert(
        self,
        text: str,
        top_n: int,
        ngram_range: Tuple[int, int],
        diversity: float
    ) -> List[Tuple[str, float]]:
        """
        استخراج با KeyBERT
        
        Args:
            text: متن پیش‌پردازش شده
            top_n: تعداد کلیدواژه
            ngram_range: محدوده n-gram
            diversity: تنوع
            
        Returns:
            list: لیست (کلیدواژه، امتیاز)
        """
        try:
            keywords = self.keybert_model.extract_keywords(
                text,
                keyphrase_ngram_range=ngram_range,
                stop_words=None,  # ما خودمان فیلتر می‌کنیم
                top_n=top_n * 2,  # بیشتر می‌گیریم چون فیلتر می‌کنیم
                use_mmr=True,
                diversity=diversity
            )
            return keywords
        except Exception as e:
            logger.warning(f"خطا در KeyBERT: {e}")
            return self._extract_statistical(text, top_n)
    
    def _extract_statistical(
        self, 
        text: str, 
        top_n: int
    ) -> List[Tuple[str, float]]:
        """
        استخراج آماری (Term Frequency)
        
        Args:
            text: متن
            top_n: تعداد کلیدواژه
            
        Returns:
            list: لیست (کلیدواژه، امتیاز)
        """
        # توکن‌سازی
        words = text.split()
        
        # حذف کلمات کوتاه
        words = [w for w in words if len(w) > 2]
        
        # شمارش فراوانی
        word_freq = Counter(words)
        
        # نرمال‌سازی امتیازها
        total = sum(word_freq.values())
        if total > 0:
            keywords = [
                (word, count / total) 
                for word, count in word_freq.most_common(top_n * 2)
            ]
        else:
            keywords = []
        
        return keywords
    
    def _filter_stopwords(
        self, 
        keywords: List[Tuple[str, float]]
    ) -> List[Tuple[str, float]]:
        """
        فیلتر کلمات ایست
        
        Args:
            keywords: لیست کلیدواژه‌ها
            
        Returns:
            list: لیست فیلتر شده
        """
        filtered = []
        
        for keyword, score in keywords:
            # بررسی کلمات ایست
            words = keyword.split()
            is_stopword = all(w in self.PERSIAN_STOPWORDS for w in words)
            
            if not is_stopword and len(keyword) > 2:
                filtered.append((keyword, score))
        
        return filtered
    
    def extract_from_sections(
        self, 
        sections: Dict[str, str],
        top_n_per_section: int = 5
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        استخراج کلیدواژه از هر بخش جداگانه
        
        Args:
            sections: دیکشنری بخش‌ها
            top_n_per_section: تعداد کلیدواژه برای هر بخش
            
        Returns:
            dict: کلیدواژه‌های هر بخش
        """
        section_keywords = {}
        
        for section_name, content in sections.items():
            if content:
                result = self.extract(content, top_n=top_n_per_section)
                section_keywords[section_name] = result['keywords']
        
        return section_keywords
    
    def get_combined_keywords(
        self,
        section_keywords: Dict[str, List[Tuple[str, float]]],
        top_n: int = 15
    ) -> List[Tuple[str, float]]:
        """
        ترکیب کلیدواژه‌های بخش‌ها با وزن‌دهی
        
        Args:
            section_keywords: کلیدواژه‌های هر بخش
            top_n: تعداد کلیدواژه نهایی
            
        Returns:
            list: کلیدواژه‌های نهایی
        """
        # وزن بخش‌ها
        section_weights = {
            'abstract': 2.0,
            'introduction': 1.5,
            'methodology': 1.5,
            'objectives': 1.8,
            'literature_review': 1.2,
            'findings': 1.3,
            'discussion': 1.0,
        }
        
        combined = {}
        
        for section, keywords in section_keywords.items():
            weight = section_weights.get(section, 1.0)
            
            for keyword, score in keywords:
                if keyword in combined:
                    combined[keyword] += score * weight
                else:
                    combined[keyword] = score * weight
        
        # مرتب‌سازی و انتخاب برترین‌ها
        sorted_keywords = sorted(
            combined.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return sorted_keywords[:top_n]
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'keywords': [],
            'top_keywords': [],
            'method': 'None',
            'keyword_count': 0
        }


# تست ماژول
if __name__ == "__main__":
    extractor = KeywordExtractor(use_keybert=False)  # بدون KeyBERT برای تست سریع
    
    test_text = """
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان طبیعی فارسی می‌پردازد.
    هدف اصلی طراحی یک سیستم هوشمند برای تحلیل احساسات متون فارسی است.
    روش‌شناسی شامل استفاده از شبکه‌های عصبی عمیق و مدل‌های ترنسفورمر است.
    داده‌های مورد استفاده شامل متون فارسی از شبکه‌های اجتماعی می‌باشد.
    نتایج نشان می‌دهد که مدل پیشنهادی دقت بالایی در تحلیل احساسات دارد.
    """
    
    result = extractor.extract(test_text, top_n=10)
    
    print("=" * 60)
    print("🔑 کلمات کلیدی استخراج شده")
    print("=" * 60)
    print(f"\nروش: {result['method']}")
    print(f"تعداد: {result['keyword_count']}")
    print("\n📋 کلیدواژه‌ها:")
    for i, (keyword, score) in enumerate(result['keywords'], 1):
        print(f"   {i:2}. {keyword:30} ({score:.4f})")

