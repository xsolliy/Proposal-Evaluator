"""
ماژول تشخیص تقلب
================

این ماژول شامل ابزارهای تشخیص تقلب و سرقت ادبی است.

Components:
    - TextEmbedder: تبدیل متن به embedding
    - SimilarityChecker: بررسی شباهت متون
    - PlagiarismDetector: تشخیص‌دهنده تقلب (یکپارچه)
"""

from .embedder import TextEmbedder
from .similarity_checker import SimilarityChecker
from .plagiarism_detector import PlagiarismDetector

__all__ = [
    'TextEmbedder',
    'SimilarityChecker',
    'PlagiarismDetector'
]

__version__ = '1.0.0'

