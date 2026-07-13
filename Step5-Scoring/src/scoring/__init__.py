"""
سیستم امتیازدهی و گزارش‌دهی پروپوزال‌های فارسی
این ماژول مسئول محاسبه نمرات نهایی و تولید گزارش جامع ارزیابی است
"""

from .structure_scorer import StructureScorer
from .reference_scorer import ReferenceScorer
from .originality_scorer import OriginalityScorer
from .final_calculator import FinalScoreCalculator
from .report_generator import ReportGenerator
from .evaluation_pipeline import EvaluationPipeline

__all__ = [
    'StructureScorer',
    'ReferenceScorer',
    'OriginalityScorer',
    'FinalScoreCalculator',
    'ReportGenerator',
    'EvaluationPipeline',
]

__version__ = '1.0.0'

