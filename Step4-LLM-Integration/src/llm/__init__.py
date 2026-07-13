"""
ماژول LLM - ارتباط با Ollama و ارزیابی هوشمند
=============================================

این ماژول شامل ابزارهای ارتباط با LLM آفلاین است.

Components:
    - OllamaClient: ارتباط با سرور Ollama
    - PromptManager: مدیریت promptها
    - StructureAnalyzer: ارزیابی ساختار (20%)
    - ContentAnalyzer: ارزیابی محتوا (35%)
    - ReferenceAnalyzer: ارزیابی منابع (15%)
    - LLMAnalyzer: کلاس یکپارچه‌ساز
"""

from .ollama_client import OllamaClient
from .prompt_manager import PromptManager
from .structure_analyzer import StructureAnalyzer
from .content_analyzer import ContentAnalyzer
from .reference_analyzer import ReferenceAnalyzer
from .llm_analyzer import LLMAnalyzer

__all__ = [
    'OllamaClient',
    'PromptManager',
    'StructureAnalyzer',
    'ContentAnalyzer',
    'ReferenceAnalyzer',
    'LLMAnalyzer'
]

__version__ = '1.0.0'

