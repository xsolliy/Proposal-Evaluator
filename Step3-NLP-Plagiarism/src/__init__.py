"""
ماژول‌های گام سوم - NLP و تشخیص تقلب
====================================

این پکیج شامل دو زیرماژول است:

1. nlp: ابزارهای پردازش زبان طبیعی و نگارش
2. plagiarism: ابزارهای تشخیص تقلب و سرقت ادبی

Example:
    >>> from src.nlp import WritingScorer
    >>> from src.plagiarism import PlagiarismDetector
"""

from . import nlp
from . import plagiarism

__all__ = ['nlp', 'plagiarism']
__version__ = '1.0.0'

