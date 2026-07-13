"""
ماژول پیش‌پردازش پروپوزال
========================

این ماژول شامل ابزارهای استخراج و پیش‌پردازش متن پروپوزال است.

Components:
    - TextExtractor: استخراج متن از PDF و Word
    - TextNormalizer: نرمال‌سازی متن فارسی
    - SectionDetector: شناسایی بخش‌های پروپوزال
"""

from .text_extractor import TextExtractor
from .normalizer import TextNormalizer
from .section_detector import SectionDetector

__all__ = [
    'TextExtractor',
    'TextNormalizer', 
    'SectionDetector'
]

__version__ = '1.0.0'
__author__ = 'Proposal Evaluation System'











