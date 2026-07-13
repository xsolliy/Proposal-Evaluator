"""
ماژول NLP - تحلیل زبانی و نگارشی
================================

این ماژول شامل ابزارهای تحلیل زبانی متن فارسی است.

Components:
    - GrammarChecker: بررسی املا و گرامر
    - KeywordExtractor: استخراج کلمات کلیدی
    - TextSummarizer: خلاصه‌سازی متن
    - TextStatistics: آمار متنی پیشرفته
    - WritingScorer: محاسبه نمره نگارشی (25%)
"""

from .grammar_checker import GrammarChecker
from .keyword_extractor import KeywordExtractor
from .summarizer import TextSummarizer
from .text_statistics import TextStatistics
from .writing_scorer import WritingScorer

__all__ = [
    'GrammarChecker',
    'KeywordExtractor', 
    'TextSummarizer',
    'TextStatistics',
    'WritingScorer'
]

__version__ = '1.0.0'

