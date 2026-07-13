"""
ماژول نرمال‌سازی متن فارسی
==========================

این ماژول متن فارسی را نرمال‌سازی و توکن‌سازی می‌کند.

Classes:
    TextNormalizer: کلاس اصلی نرمال‌سازی

Example:
    >>> normalizer = TextNormalizer()
    >>> result = normalizer.normalize("اين متن را نرمال كن")
    >>> print(result['normalized_text'])
"""

import re
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextNormalizer:
    """
    کلاس نرمال‌سازی متن فارسی
    
    این کلاس از کتابخانه Hazm برای نرمال‌سازی استفاده می‌کند و شامل:
    - تبدیل حروف عربی به فارسی (ك → ک، ي → ی)
    - اصلاح نیم‌فاصله‌ها
    - حذف کاراکترهای اضافی
    - توکن‌سازی کلمات و جملات
    
    Attributes:
        use_hazm (bool): آیا از Hazm استفاده شود
        
    Example:
        >>> normalizer = TextNormalizer()
        >>> result = normalizer.normalize("اين يک متن تست است")
        >>> print(result['normalized_text'])  # "این یک متن تست است"
    """
    
    # نگاشت حروف عربی به فارسی
    ARABIC_TO_PERSIAN = {
        'ك': 'ک',
        'ي': 'ی',
        'ى': 'ی',
        'ؤ': 'و',
        'ة': 'ه',
        'إ': 'ا',
        'أ': 'ا',
        'آ': 'آ',
        '٠': '۰',
        '١': '۱',
        '٢': '۲',
        '٣': '۳',
        '٤': '۴',
        '٥': '۵',
        '٦': '۶',
        '٧': '۷',
        '٨': '۸',
        '٩': '۹',
    }
    
    # کاراکترهای نیم‌فاصله
    HALF_SPACE = '\u200c'  # Zero-Width Non-Joiner
    
    def __init__(self, use_hazm: bool = True):
        """
        مقداردهی اولیه TextNormalizer
        
        Args:
            use_hazm: آیا از Hazm استفاده شود (پیش‌فرض: True)
        """
        self.use_hazm = use_hazm
        self.hazm_normalizer = None
        
        if use_hazm:
            self._init_hazm()
    
    def _init_hazm(self) -> None:
        """راه‌اندازی Hazm"""
        try:
            from hazm import Normalizer
            self.hazm_normalizer = Normalizer()
            logger.info("Hazm با موفقیت بارگذاری شد")
        except ImportError:
            logger.warning("Hazm نصب نیست. از نرمال‌سازی پایه استفاده می‌شود")
            self.use_hazm = False
    
    def normalize(self, text: str) -> Dict:
        """
        نرمال‌سازی کامل متن
        
        Args:
            text: متن خام ورودی
            
        Returns:
            dict: شامل متن نرمال‌شده و آمار
            {
                'original_text': str,
                'normalized_text': str,
                'words': list,
                'sentences': list,
                'statistics': {
                    'original_char_count': int,
                    'normalized_char_count': int,
                    'word_count': int,
                    'sentence_count': int,
                    'unique_words': int,
                    'avg_word_length': float,
                    'avg_sentence_length': float,
                    'lexical_diversity': float
                }
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        original_text = text
        
        # نرمال‌سازی
        if self.use_hazm and self.hazm_normalizer:
            normalized_text = self.hazm_normalizer.normalize(text)
        else:
            normalized_text = self._basic_normalize(text)
        
        # توکن‌سازی
        words = self._tokenize_words(normalized_text)
        sentences = self._tokenize_sentences(normalized_text)
        
        # محاسبه آمار
        statistics = self._calculate_statistics(
            original_text, normalized_text, words, sentences
        )
        
        return {
            'original_text': original_text,
            'normalized_text': normalized_text,
            'words': words,
            'sentences': sentences,
            'statistics': statistics
        }
    
    def _basic_normalize(self, text: str) -> str:
        """
        نرمال‌سازی پایه (بدون Hazm)
        
        Args:
            text: متن ورودی
            
        Returns:
            str: متن نرمال‌شده
        """
        # تبدیل حروف عربی به فارسی
        for arabic, persian in self.ARABIC_TO_PERSIAN.items():
            text = text.replace(arabic, persian)
        
        # حذف فاصله‌های اضافی
        text = re.sub(r'\s+', ' ', text)
        
        # اصلاح نیم‌فاصله‌ها
        text = self._fix_half_spaces(text)
        
        # حذف کاراکترهای کنترلی (به جز نیم‌فاصله)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text.strip()
    
    def _fix_half_spaces(self, text: str) -> str:
        """
        اصلاح نیم‌فاصله‌ها در متن
        
        Args:
            text: متن ورودی
            
        Returns:
            str: متن با نیم‌فاصله‌های اصلاح شده
        """
        # پسوندهایی که باید نیم‌فاصله بگیرند
        suffixes = ['ها', 'های', 'ای', 'ام', 'ات', 'اش', 'مان', 'تان', 'شان']
        
        for suffix in suffixes:
            # تبدیل فاصله قبل از پسوند به نیم‌فاصله
            pattern = r'(\S)\s+(' + suffix + r')(?=\s|$|[،.؛:؟!])'
            text = re.sub(pattern, r'\1' + self.HALF_SPACE + r'\2', text)
        
        # پیشوندهایی که باید نیم‌فاصله بگیرند
        prefixes = ['می', 'نمی', 'بی', 'بر']
        
        for prefix in prefixes:
            pattern = r'(^|\s)(' + prefix + r')\s+(\S)'
            text = re.sub(pattern, r'\1\2' + self.HALF_SPACE + r'\3', text)
        
        return text
    
    def _tokenize_words(self, text: str) -> List[str]:
        """
        توکن‌سازی کلمات
        
        Args:
            text: متن نرمال‌شده
            
        Returns:
            list: لیست کلمات
        """
        if self.use_hazm:
            try:
                from hazm import word_tokenize
                return word_tokenize(text)
            except ImportError:
                pass
        
        # توکن‌سازی ساده
        # حذف علائم نگارشی و تقسیم بر اساس فاصله
        text_clean = re.sub(r'[،.؛:؟!()«»\[\]{}"\'-]', ' ', text)
        words = [w.strip() for w in text_clean.split() if w.strip()]
        return words
    
    def _tokenize_sentences(self, text: str) -> List[str]:
        """
        توکن‌سازی جملات
        
        Args:
            text: متن نرمال‌شده
            
        Returns:
            list: لیست جملات
        """
        if self.use_hazm:
            try:
                from hazm import sent_tokenize
                return sent_tokenize(text)
            except ImportError:
                pass
        
        # توکن‌سازی ساده بر اساس علائم پایان جمله
        sentences = re.split(r'[.؟!؛]\s*', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _calculate_statistics(
        self, 
        original: str, 
        normalized: str, 
        words: List[str], 
        sentences: List[str]
    ) -> Dict:
        """
        محاسبه آمار متنی
        
        Args:
            original: متن اصلی
            normalized: متن نرمال‌شده
            words: لیست کلمات
            sentences: لیست جملات
            
        Returns:
            dict: آمار متنی
        """
        word_count = len(words)
        sentence_count = len(sentences)
        unique_words = len(set(words))
        
        # میانگین طول کلمات
        if word_count > 0:
            avg_word_length = sum(len(w) for w in words) / word_count
        else:
            avg_word_length = 0
        
        # میانگین طول جملات (تعداد کلمات در جمله)
        if sentence_count > 0:
            avg_sentence_length = word_count / sentence_count
        else:
            avg_sentence_length = 0
        
        # تنوع واژگانی (نسبت کلمات یکتا به کل)
        if word_count > 0:
            lexical_diversity = unique_words / word_count
        else:
            lexical_diversity = 0
        
        return {
            'original_char_count': len(original),
            'normalized_char_count': len(normalized),
            'word_count': word_count,
            'sentence_count': sentence_count,
            'unique_words': unique_words,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2),
            'lexical_diversity': round(lexical_diversity, 4)
        }
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'original_text': '',
            'normalized_text': '',
            'words': [],
            'sentences': [],
            'statistics': {
                'original_char_count': 0,
                'normalized_char_count': 0,
                'word_count': 0,
                'sentence_count': 0,
                'unique_words': 0,
                'avg_word_length': 0,
                'avg_sentence_length': 0,
                'lexical_diversity': 0
            }
        }
    
    def remove_stopwords(self, words: List[str]) -> List[str]:
        """
        حذف کلمات ایست (stopwords)
        
        Args:
            words: لیست کلمات
            
        Returns:
            list: کلمات بدون stopwords
        """
        # لیست پایه کلمات ایست فارسی
        stopwords = {
            'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'است', 
            'برای', 'آن', 'یک', 'خود', 'تا', 'کرد', 'بر', 'هم', 
            'نیز', 'شد', 'شده', 'می', 'گفت', 'او', 'ما', 'اما', 
            'یا', 'اگر', 'هر', 'بود', 'چه', 'همه', 'باید', 'دارد',
            'پس', 'ها', 'های', 'شود', 'کند', 'وی', 'بین', 'کنند',
            'هستند', 'بوده', 'دیگر', 'همچنین', 'توسط', 'چون', 'بی'
        }
        
        return [w for w in words if w not in stopwords]


# تست ماژول
if __name__ == "__main__":
    normalizer = TextNormalizer()
    
    # متن تست
    test_text = """
    اين يک متن تست براي بررسي نرمال سازي است.
    ما مي خواهيم که اين متن به درستي نرمال شود.
    آيا نيم فاصله ها هم درست مي شوند؟
    """
    
    result = normalizer.normalize(test_text)
    
    print("=" * 60)
    print("📝 متن اصلی:")
    print(test_text)
    print("=" * 60)
    print("✅ متن نرمال‌شده:")
    print(result['normalized_text'])
    print("=" * 60)
    print("📊 آمار:")
    for key, value in result['statistics'].items():
        print(f"   {key}: {value}")











