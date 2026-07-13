"""
ماژول خلاصه‌سازی متن
====================

این ماژول متن فارسی را خلاصه می‌کند.

Classes:
    TextSummarizer: خلاصه‌ساز متن

Example:
    >>> summarizer = TextSummarizer()
    >>> summary = summarizer.summarize(text, num_sentences=3)
    >>> print(summary)
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextSummarizer:
    """
    کلاس خلاصه‌سازی متن فارسی
    
    این کلاس از روش Extractive Summarization استفاده می‌کند.
    جملات مهم‌تر بر اساس امتیازدهی انتخاب می‌شوند.
    
    Attributes:
        stopwords (set): کلمات ایست فارسی
        
    Example:
        >>> summarizer = TextSummarizer()
        >>> result = summarizer.summarize(text, num_sentences=5)
        >>> print(result['summary'])
    """
    
    # کلمات ایست فارسی
    STOPWORDS = {
        'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'است', 'برای',
        'آن', 'یک', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'شد', 'شده',
        'می', 'او', 'ما', 'اما', 'یا', 'اگر', 'هر', 'بود', 'چه', 'همه',
        'باید', 'دارد', 'پس', 'ها', 'های', 'شود', 'کند', 'می‌شود',
    }
    
    # کلمات سیگنال که اهمیت جمله را نشان می‌دهند
    SIGNAL_WORDS = {
        'مهم', 'اصلی', 'اساسی', 'کلیدی', 'هدف', 'نتیجه', 'یافته',
        'نشان', 'بررسی', 'تحلیل', 'پژوهش', 'تحقیق', 'مطالعه',
        'پیشنهاد', 'روش', 'چکیده', 'خلاصه', 'بنابراین', 'درنتیجه',
        'همچنین', 'علاوه', 'اثبات', 'تأیید', 'مشخص', 'آشکار',
    }
    
    def __init__(self):
        """مقداردهی اولیه TextSummarizer"""
        self._init_hazm()
    
    def _init_hazm(self) -> None:
        """راه‌اندازی Hazm"""
        try:
            from hazm import sent_tokenize, word_tokenize
            self.sent_tokenize = sent_tokenize
            self.word_tokenize = word_tokenize
            self.use_hazm = True
            logger.info("Hazm برای خلاصه‌سازی بارگذاری شد")
        except ImportError:
            self.use_hazm = False
            logger.warning("Hazm نصب نیست. از روش پایه استفاده می‌شود.")
    
    def summarize(
        self, 
        text: str, 
        num_sentences: int = 5,
        ratio: float = None
    ) -> Dict:
        """
        خلاصه‌سازی متن
        
        Args:
            text: متن ورودی
            num_sentences: تعداد جملات خلاصه
            ratio: نسبت خلاصه (0.1 تا 0.5) - اگر داده شود، num_sentences نادیده گرفته می‌شود
            
        Returns:
            dict: نتایج خلاصه‌سازی
            {
                'summary': str,
                'sentences': list,
                'sentence_scores': list,
                'compression_ratio': float,
                'original_sentences': int,
                'summary_sentences': int
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # توکن‌سازی جملات
        sentences = self._tokenize_sentences(text)
        
        if len(sentences) == 0:
            return self._empty_result()
        
        # محاسبه تعداد جملات خلاصه
        if ratio:
            num_sentences = max(1, int(len(sentences) * ratio))
        
        num_sentences = min(num_sentences, len(sentences))
        
        # امتیازدهی جملات
        sentence_scores = self._score_sentences(sentences)
        
        # انتخاب جملات برتر با حفظ ترتیب
        selected_indices = self._select_top_sentences(
            sentence_scores, num_sentences
        )
        
        # ساخت خلاصه
        summary_sentences = [sentences[i] for i in sorted(selected_indices)]
        summary = ' '.join(summary_sentences)
        
        # محاسبه نسبت فشرده‌سازی
        compression_ratio = len(summary) / len(text) if len(text) > 0 else 0
        
        return {
            'summary': summary,
            'sentences': summary_sentences,
            'sentence_scores': [
                (sentences[i], sentence_scores[i]) 
                for i in selected_indices
            ],
            'compression_ratio': round(compression_ratio, 3),
            'original_sentences': len(sentences),
            'summary_sentences': len(summary_sentences)
        }
    
    def _tokenize_sentences(self, text: str) -> List[str]:
        """
        توکن‌سازی جملات
        
        Args:
            text: متن
            
        Returns:
            list: لیست جملات
        """
        if self.use_hazm:
            try:
                sentences = self.sent_tokenize(text)
            except:
                sentences = self._simple_sent_tokenize(text)
        else:
            sentences = self._simple_sent_tokenize(text)
        
        # فیلتر جملات خیلی کوتاه
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return sentences
    
    def _simple_sent_tokenize(self, text: str) -> List[str]:
        """توکن‌سازی ساده جملات"""
        # تقسیم بر اساس علائم پایان جمله
        sentences = re.split(r'[.؟!؛]\s*', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _score_sentences(self, sentences: List[str]) -> List[float]:
        """
        امتیازدهی جملات
        
        Args:
            sentences: لیست جملات
            
        Returns:
            list: امتیاز هر جمله
        """
        scores = []
        
        # محاسبه فراوانی کلمات در کل متن
        all_words = []
        for sentence in sentences:
            words = self._tokenize_words(sentence)
            all_words.extend(words)
        
        word_freq = Counter(all_words)
        
        # امتیازدهی هر جمله
        for i, sentence in enumerate(sentences):
            score = 0.0
            words = self._tokenize_words(sentence)
            
            if len(words) == 0:
                scores.append(0)
                continue
            
            # 1. امتیاز بر اساس فراوانی کلمات (TF)
            tf_score = sum(word_freq[w] for w in words) / len(words)
            score += tf_score * 0.3
            
            # 2. امتیاز موقعیت (جملات اول و آخر مهم‌ترند)
            position_score = self._position_score(i, len(sentences))
            score += position_score * 0.2
            
            # 3. امتیاز طول جمله (نه خیلی کوتاه، نه خیلی بلند)
            length_score = self._length_score(len(words))
            score += length_score * 0.15
            
            # 4. امتیاز کلمات سیگنال
            signal_score = self._signal_score(words)
            score += signal_score * 0.25
            
            # 5. امتیاز حضور اعداد (اغلب شامل آمار مهم)
            number_score = self._number_score(sentence)
            score += number_score * 0.1
            
            scores.append(score)
        
        return scores
    
    def _tokenize_words(self, sentence: str) -> List[str]:
        """توکن‌سازی کلمات"""
        if self.use_hazm:
            try:
                words = self.word_tokenize(sentence)
            except:
                words = sentence.split()
        else:
            words = sentence.split()
        
        # حذف کلمات ایست
        words = [w for w in words if w not in self.STOPWORDS and len(w) > 1]
        return words
    
    def _position_score(self, position: int, total: int) -> float:
        """
        امتیاز موقعیت جمله
        
        جملات اول، دوم، و آخر امتیاز بیشتری دارند.
        """
        if total <= 1:
            return 1.0
        
        if position == 0:
            return 1.0  # جمله اول
        elif position == 1:
            return 0.8  # جمله دوم
        elif position == total - 1:
            return 0.9  # جمله آخر
        elif position == total - 2:
            return 0.7  # جمله ماقبل آخر
        else:
            # جملات میانی
            return 0.5
    
    def _length_score(self, word_count: int) -> float:
        """
        امتیاز طول جمله
        
        جملات با طول متوسط (10-30 کلمه) امتیاز بیشتری دارند.
        """
        ideal_min = 10
        ideal_max = 30
        
        if ideal_min <= word_count <= ideal_max:
            return 1.0
        elif word_count < ideal_min:
            return word_count / ideal_min
        else:
            return ideal_max / word_count
    
    def _signal_score(self, words: List[str]) -> float:
        """
        امتیاز کلمات سیگنال
        
        حضور کلمات کلیدی نشان‌دهنده اهمیت جمله است.
        """
        signal_count = sum(1 for w in words if w in self.SIGNAL_WORDS)
        
        if len(words) == 0:
            return 0
        
        return min(1.0, signal_count * 0.3)
    
    def _number_score(self, sentence: str) -> float:
        """
        امتیاز حضور اعداد
        
        جملات حاوی اعداد اغلب شامل آمار مهم هستند.
        """
        # اعداد فارسی و انگلیسی
        numbers = re.findall(r'[۰-۹0-9]+', sentence)
        
        if numbers:
            return min(1.0, len(numbers) * 0.3)
        return 0
    
    def _select_top_sentences(
        self, 
        scores: List[float], 
        num_sentences: int
    ) -> List[int]:
        """
        انتخاب جملات برتر
        
        Args:
            scores: امتیاز جملات
            num_sentences: تعداد جملات مورد نیاز
            
        Returns:
            list: اندیس جملات انتخاب شده
        """
        # مرتب‌سازی بر اساس امتیاز
        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)
        
        # انتخاب برترین‌ها
        selected = [idx for idx, score in indexed_scores[:num_sentences]]
        
        return selected
    
    def summarize_sections(
        self, 
        sections: Dict[str, str],
        sentences_per_section: int = 2
    ) -> Dict[str, str]:
        """
        خلاصه‌سازی هر بخش جداگانه
        
        Args:
            sections: دیکشنری بخش‌ها
            sentences_per_section: تعداد جملات برای هر بخش
            
        Returns:
            dict: خلاصه هر بخش
        """
        summaries = {}
        
        for section_name, content in sections.items():
            if content and len(content) > 50:
                result = self.summarize(content, num_sentences=sentences_per_section)
                summaries[section_name] = result['summary']
            else:
                summaries[section_name] = content
        
        return summaries
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'summary': '',
            'sentences': [],
            'sentence_scores': [],
            'compression_ratio': 0,
            'original_sentences': 0,
            'summary_sentences': 0
        }


# تست ماژول
if __name__ == "__main__":
    summarizer = TextSummarizer()
    
    test_text = """
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان طبیعی فارسی می‌پردازد.
    هدف اصلی طراحی یک سیستم هوشمند برای تحلیل احساسات متون فارسی است.
    در سال‌های اخیر، با افزایش حجم داده‌های متنی در فضای مجازی، نیاز به ابزارهای خودکار پردازش متن افزایش یافته است.
    روش‌شناسی این پژوهش شامل جمع‌آوری داده‌های متنی از شبکه‌های اجتماعی فارسی‌زبان است.
    سپس این داده‌ها پیش‌پردازش و برچسب‌گذاری می‌شوند.
    مدل پیشنهادی از معماری ترنسفورمر استفاده می‌کند که در سال‌های اخیر عملکرد بسیار خوبی در وظایف NLP نشان داده است.
    نتایج نشان می‌دهد که مدل پیشنهادی با دقت ۹۲ درصد، عملکرد بهتری نسبت به روش‌های قبلی دارد.
    این یافته‌ها اهمیت استفاده از روش‌های نوین یادگیری عمیق را در پردازش زبان فارسی نشان می‌دهد.
    در نهایت، پیشنهاداتی برای پژوهش‌های آینده ارائه شده است.
    """
    
    result = summarizer.summarize(test_text, num_sentences=3)
    
    print("=" * 60)
    print("📝 خلاصه متن")
    print("=" * 60)
    print(f"\n📊 آمار:")
    print(f"   جملات اصلی: {result['original_sentences']}")
    print(f"   جملات خلاصه: {result['summary_sentences']}")
    print(f"   نسبت فشرده‌سازی: {result['compression_ratio']:.1%}")
    
    print(f"\n📋 خلاصه:")
    print(result['summary'])

