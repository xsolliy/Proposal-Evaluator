"""
ماژول آمار متنی پیشرفته
=======================

این ماژول آمارهای متنی پیشرفته را محاسبه می‌کند.

Classes:
    TextStatistics: محاسبه آمار متنی

Example:
    >>> stats = TextStatistics()
    >>> result = stats.analyze(text)
    >>> print(result['readability_score'])
"""

import re
import math
from typing import Dict, List, Tuple
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextStatistics:
    """
    کلاس محاسبه آمار متنی پیشرفته
    
    این کلاس آمارهای مختلف متنی را محاسبه می‌کند از جمله:
    - تنوع واژگانی
    - سطح خوانایی
    - تراکم اطلاعاتی
    - توزیع طول جملات
    
    Example:
        >>> stats = TextStatistics()
        >>> result = stats.analyze(text)
        >>> print(f"خوانایی: {result['readability_score']}")
    """
    
    # کلمات ایست فارسی
    STOPWORDS = {
        'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'است', 'برای',
        'آن', 'یک', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'شد', 'شده',
        'می', 'او', 'ما', 'اما', 'یا', 'اگر', 'هر', 'بود', 'چه', 'همه',
    }
    
    def __init__(self):
        """مقداردهی اولیه TextStatistics"""
        self._init_hazm()
    
    def _init_hazm(self) -> None:
        """راه‌اندازی Hazm"""
        try:
            from hazm import word_tokenize, sent_tokenize
            self.word_tokenize = word_tokenize
            self.sent_tokenize = sent_tokenize
            self.use_hazm = True
        except ImportError:
            self.use_hazm = False
    
    def analyze(self, text: str) -> Dict:
        """
        تحلیل کامل آماری متن
        
        Args:
            text: متن ورودی
            
        Returns:
            dict: آمار کامل متن
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # توکن‌سازی
        words = self._tokenize_words(text)
        sentences = self._tokenize_sentences(text)
        
        # آمار پایه
        basic_stats = self._basic_statistics(text, words, sentences)
        
        # تنوع واژگانی
        lexical_stats = self._lexical_diversity(words)
        
        # آمار جملات
        sentence_stats = self._sentence_statistics(sentences)
        
        # خوانایی
        readability = self._readability_score(basic_stats, sentence_stats)
        
        # توزیع کلمات
        word_distribution = self._word_distribution(words)
        
        return {
            **basic_stats,
            **lexical_stats,
            **sentence_stats,
            'readability_score': readability['score'],
            'readability_level': readability['level'],
            'word_frequency': word_distribution['top_words'],
            'content_density': self._content_density(words)
        }
    
    def _tokenize_words(self, text: str) -> List[str]:
        """توکن‌سازی کلمات"""
        if self.use_hazm:
            try:
                return self.word_tokenize(text)
            except:
                pass
        
        # روش ساده
        words = re.findall(r'[\u0600-\u06FF]+', text)
        return words
    
    def _tokenize_sentences(self, text: str) -> List[str]:
        """توکن‌سازی جملات"""
        if self.use_hazm:
            try:
                return self.sent_tokenize(text)
            except:
                pass
        
        # روش ساده
        sentences = re.split(r'[.؟!؛]\s*', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _basic_statistics(
        self, 
        text: str, 
        words: List[str], 
        sentences: List[str]
    ) -> Dict:
        """
        آمار پایه متن
        """
        char_count = len(text)
        char_count_no_space = len(text.replace(' ', '').replace('\n', ''))
        word_count = len(words)
        sentence_count = len(sentences)
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # میانگین‌ها
        avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        return {
            'char_count': char_count,
            'char_count_no_space': char_count_no_space,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'avg_word_length': round(avg_word_length, 2),
            'avg_sentence_length': round(avg_sentence_length, 2)
        }
    
    def _lexical_diversity(self, words: List[str]) -> Dict:
        """
        محاسبه تنوع واژگانی
        """
        if not words:
            return {
                'unique_words': 0,
                'lexical_diversity': 0,
                'type_token_ratio': 0,
                'hapax_legomena': 0,
                'content_words': 0
            }
        
        word_count = len(words)
        unique_words = set(words)
        unique_count = len(unique_words)
        
        # Type-Token Ratio (TTR)
        ttr = unique_count / word_count
        
        # Hapax Legomena (کلماتی که فقط یکبار استفاده شده‌اند)
        word_freq = Counter(words)
        hapax = sum(1 for count in word_freq.values() if count == 1)
        
        # کلمات محتوایی (غیر ایست)
        content_words = [w for w in words if w not in self.STOPWORDS]
        
        return {
            'unique_words': unique_count,
            'lexical_diversity': round(ttr, 4),
            'type_token_ratio': round(ttr, 4),
            'hapax_legomena': hapax,
            'hapax_ratio': round(hapax / word_count, 4) if word_count > 0 else 0,
            'content_words': len(content_words),
            'content_word_ratio': round(len(content_words) / word_count, 4) if word_count > 0 else 0
        }
    
    def _sentence_statistics(self, sentences: List[str]) -> Dict:
        """
        آمار جملات
        """
        if not sentences:
            return {
                'min_sentence_length': 0,
                'max_sentence_length': 0,
                'sentence_length_std': 0,
                'short_sentences': 0,
                'long_sentences': 0
            }
        
        # طول جملات (تعداد کلمات)
        sentence_lengths = [len(s.split()) for s in sentences]
        
        min_len = min(sentence_lengths)
        max_len = max(sentence_lengths)
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        
        # انحراف معیار
        variance = sum((x - avg_len) ** 2 for x in sentence_lengths) / len(sentence_lengths)
        std_dev = math.sqrt(variance)
        
        # جملات کوتاه (< 5 کلمه) و بلند (> 25 کلمه)
        short = sum(1 for l in sentence_lengths if l < 5)
        long = sum(1 for l in sentence_lengths if l > 25)
        
        return {
            'min_sentence_length': min_len,
            'max_sentence_length': max_len,
            'sentence_length_std': round(std_dev, 2),
            'short_sentences': short,
            'long_sentences': long,
            'short_sentence_ratio': round(short / len(sentences), 4),
            'long_sentence_ratio': round(long / len(sentences), 4)
        }
    
    def _readability_score(self, basic: Dict, sentence: Dict) -> Dict:
        """
        محاسبه امتیاز خوانایی
        
        برای فارسی، فرمول سفارشی بر اساس:
        - میانگین طول کلمات
        - میانگین طول جملات
        - تنوع ساختاری
        """
        avg_word_len = basic.get('avg_word_length', 4)
        avg_sent_len = basic.get('avg_sentence_length', 15)
        
        # فرمول خوانایی فارسی (سفارشی)
        # مقادیر ایده‌آل: طول کلمه 4-5، طول جمله 15-20
        
        word_penalty = abs(avg_word_len - 4.5) * 5
        sentence_penalty = abs(avg_sent_len - 17) * 2
        
        # انحراف معیار جملات (تنوع خوب است)
        std_bonus = min(sentence.get('sentence_length_std', 0) * 2, 10)
        
        score = 100 - word_penalty - sentence_penalty + std_bonus
        score = max(0, min(100, score))
        
        # تعیین سطح
        if score >= 80:
            level = 'بسیار آسان'
        elif score >= 60:
            level = 'آسان'
        elif score >= 40:
            level = 'متوسط'
        elif score >= 20:
            level = 'سخت'
        else:
            level = 'بسیار سخت'
        
        return {
            'score': round(score, 2),
            'level': level
        }
    
    def _word_distribution(self, words: List[str], top_n: int = 20) -> Dict:
        """
        توزیع فراوانی کلمات
        """
        # فیلتر کلمات ایست و کوتاه
        content_words = [w for w in words if w not in self.STOPWORDS and len(w) > 2]
        
        word_freq = Counter(content_words)
        top_words = word_freq.most_common(top_n)
        
        return {
            'top_words': top_words,
            'total_unique': len(word_freq)
        }
    
    def _content_density(self, words: List[str]) -> float:
        """
        محاسبه تراکم محتوا
        
        نسبت کلمات محتوایی به کل کلمات
        """
        if not words:
            return 0
        
        content_words = [w for w in words if w not in self.STOPWORDS]
        return round(len(content_words) / len(words), 4)
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'char_count': 0,
            'word_count': 0,
            'sentence_count': 0,
            'paragraph_count': 0,
            'avg_word_length': 0,
            'avg_sentence_length': 0,
            'unique_words': 0,
            'lexical_diversity': 0,
            'readability_score': 0,
            'readability_level': 'نامشخص',
            'content_density': 0
        }
    
    def compare_texts(self, text1: str, text2: str) -> Dict:
        """
        مقایسه آماری دو متن
        """
        stats1 = self.analyze(text1)
        stats2 = self.analyze(text2)
        
        comparison = {}
        
        # مقایسه معیارهای کلیدی
        keys = ['word_count', 'avg_sentence_length', 'lexical_diversity', 
                'readability_score', 'content_density']
        
        for key in keys:
            v1 = stats1.get(key, 0)
            v2 = stats2.get(key, 0)
            diff = v2 - v1
            comparison[key] = {
                'text1': v1,
                'text2': v2,
                'difference': round(diff, 4),
                'percent_change': round((diff / v1 * 100) if v1 else 0, 2)
            }
        
        return comparison


# تست ماژول
if __name__ == "__main__":
    stats = TextStatistics()
    
    test_text = """
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان طبیعی فارسی می‌پردازد.
    هدف اصلی طراحی یک سیستم هوشمند برای تحلیل احساسات متون فارسی است.
    روش‌شناسی این پژوهش شامل جمع‌آوری داده‌های متنی از شبکه‌های اجتماعی فارسی‌زبان است.
    مدل پیشنهادی از معماری ترنسفورمر استفاده می‌کند.
    نتایج نشان می‌دهد که مدل پیشنهادی با دقت ۹۲ درصد عملکرد بهتری دارد.
    """
    
    result = stats.analyze(test_text)
    
    print("=" * 60)
    print("📊 آمار متنی پیشرفته")
    print("=" * 60)
    
    print("\n📝 آمار پایه:")
    print(f"   تعداد کاراکتر: {result['char_count']}")
    print(f"   تعداد کلمات: {result['word_count']}")
    print(f"   تعداد جملات: {result['sentence_count']}")
    print(f"   میانگین طول کلمه: {result['avg_word_length']}")
    print(f"   میانگین طول جمله: {result['avg_sentence_length']}")
    
    print("\n📈 تنوع واژگانی:")
    print(f"   کلمات یکتا: {result['unique_words']}")
    print(f"   تنوع واژگانی: {result['lexical_diversity']}")
    print(f"   تراکم محتوا: {result['content_density']}")
    
    print("\n📖 خوانایی:")
    print(f"   نمره خوانایی: {result['readability_score']}")
    print(f"   سطح: {result['readability_level']}")

