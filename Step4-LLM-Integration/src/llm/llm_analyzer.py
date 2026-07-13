"""
ارزیاب یکپارچه LLM
==================

این ماژول تمام ارزیابی‌های LLM را یکپارچه می‌کند.

Classes:
    LLMAnalyzer: ارزیاب یکپارچه

Example:
    >>> analyzer = LLMAnalyzer()
    >>> result = analyzer.analyze_proposal(proposal_data)
    >>> print(result['total_score'])
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .ollama_client import OllamaClient, OllamaConfig
from .prompt_manager import PromptManager
from .structure_analyzer import StructureAnalyzer
from .content_analyzer import ContentAnalyzer
from .reference_analyzer import ReferenceAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """
    کلاس یکپارچه ارزیابی با LLM
    
    این کلاس تمام ارزیابی‌های LLM را هماهنگ می‌کند:
    - ساختار (20%)
    - محتوا (35%)
    - منابع (15%)
    
    مجموع: 70% از نمره کل (30% باقیمانده توسط NLP محاسبه می‌شود)
    
    Attributes:
        client (OllamaClient): کلاینت Ollama
        structure_analyzer: ارزیاب ساختار
        content_analyzer: ارزیاب محتوا
        reference_analyzer: ارزیاب منابع
        
    Example:
        >>> analyzer = LLMAnalyzer()
        >>> result = analyzer.analyze_proposal({
        ...     'sections': {...},
        ...     'keywords': [...],
        ...     'references': [...]
        ... })
        >>> print(f"نمره LLM: {result['llm_score']}")
    """
    
    # وزن هر بخش
    WEIGHTS = {
        'structure': 0.20,   # 20%
        'content': 0.35,     # 35%
        'references': 0.15   # 15%
    }
    
    def __init__(
        self,
        model: str = "llama3.1:8b",
        host: str = "http://localhost",
        port: int = 11434
    ):
        """
        مقداردهی اولیه LLMAnalyzer
        
        Args:
            model: نام مدل LLM
            host: آدرس سرور Ollama
            port: پورت سرور
        """
        config = OllamaConfig(
            host=host,
            port=port,
            model=model,
            temperature=0.0
        )
        
        self.client = OllamaClient(config)
        self.prompt_manager = PromptManager()
        
        # ارزیاب‌های تخصصی
        self.structure_analyzer = StructureAnalyzer(self.client)
        self.content_analyzer = ContentAnalyzer(self.client)
        self.reference_analyzer = ReferenceAnalyzer(self.client)
        
        logger.info(f"LLMAnalyzer آماده شد با مدل: {model}")
    
    def analyze_proposal(
        self,
        proposal_data: Dict,
        use_llm: bool = True
    ) -> Dict:
        """
        ارزیابی کامل پروپوزال با LLM
        
        Args:
            proposal_data: داده‌های پروپوزال
                {
                    'sections': Dict[str, str],
                    'metadata': Dict,
                    'keywords': List[str],
                    'references': List[str]
                }
            use_llm: استفاده از LLM
            
        Returns:
            dict: نتایج کامل ارزیابی
        """
        sections = proposal_data.get('sections', {})
        metadata = proposal_data.get('metadata', {})
        keywords = proposal_data.get('keywords', [])
        references = proposal_data.get('references', [])
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'llm_available': self.client.is_available(),
            'model': self.client.config.model,
            'used_llm': use_llm and self.client.is_available()
        }
        
        # 1. ارزیابی ساختار (20%)
        logger.info("ارزیابی ساختار...")
        structure_result = self.structure_analyzer.analyze(
            sections, metadata, use_llm
        )
        results['structure'] = structure_result
        
        # 2. ارزیابی محتوا (35%)
        logger.info("ارزیابی محتوا...")
        content_result = self.content_analyzer.analyze(
            sections, keywords, use_llm
        )
        results['content'] = content_result
        
        # 3. ارزیابی منابع (15%)
        logger.info("ارزیابی منابع...")
        reference_result = self.reference_analyzer.analyze(
            references, use_llm
        )
        results['references'] = reference_result
        
        # محاسبه نمره LLM (70%)
        llm_score = (
            structure_result['score'] * self.WEIGHTS['structure'] +
            content_result['score'] * self.WEIGHTS['content'] +
            reference_result['score'] * self.WEIGHTS['references']
        )
        
        results['llm_score'] = round(llm_score, 2)
        results['llm_weighted'] = round(llm_score / 100 * 70, 2)  # از 70
        
        # خلاصه
        results['summary'] = self._generate_summary(results)
        
        # توصیه‌های اولویت‌دار
        results['priority_recommendations'] = self._prioritize_recommendations(results)
        
        return results
    
    def analyze_structure_only(
        self,
        sections: Dict[str, str],
        metadata: Dict
    ) -> Dict:
        """فقط ارزیابی ساختار"""
        return self.structure_analyzer.analyze(sections, metadata)
    
    def analyze_content_only(
        self,
        sections: Dict[str, str],
        keywords: List[str]
    ) -> Dict:
        """فقط ارزیابی محتوا"""
        return self.content_analyzer.analyze(sections, keywords)
    
    def analyze_references_only(
        self,
        references: List[str]
    ) -> Dict:
        """فقط ارزیابی منابع"""
        return self.reference_analyzer.analyze(references)
    
    def _generate_summary(self, results: Dict) -> Dict:
        """
        تولید خلاصه ارزیابی
        """
        structure_score = results['structure']['score']
        content_score = results['content']['score']
        reference_score = results['references']['score']
        
        # تعیین درجه کلی
        avg_score = (structure_score + content_score + reference_score) / 3
        
        if avg_score >= 85:
            overall_grade = 'عالی'
            verdict = 'تأیید'
        elif avg_score >= 70:
            overall_grade = 'خوب'
            verdict = 'تأیید مشروط'
        elif avg_score >= 55:
            overall_grade = 'متوسط'
            verdict = 'نیاز به بازنگری'
        else:
            overall_grade = 'ضعیف'
            verdict = 'رد'
        
        # جمع‌آوری نقاط قوت و ضعف
        all_strengths = []
        all_weaknesses = []
        
        for key in ['structure', 'content', 'references']:
            all_strengths.extend(results[key].get('strengths', []))
            all_weaknesses.extend(
                results[key].get('issues', []) + 
                results[key].get('weaknesses', [])
            )
        
        return {
            'average_score': round(avg_score, 2),
            'overall_grade': overall_grade,
            'verdict': verdict,
            'breakdown': {
                'structure': f"{structure_score}/100 (20%)",
                'content': f"{content_score}/100 (35%)",
                'references': f"{reference_score}/100 (15%)"
            },
            'key_strengths': all_strengths[:5],
            'key_weaknesses': all_weaknesses[:5]
        }
    
    def _prioritize_recommendations(self, results: Dict) -> List[str]:
        """
        اولویت‌بندی توصیه‌ها
        """
        all_recommendations = []
        
        # جمع‌آوری با اولویت
        priorities = [
            ('content', 3),      # محتوا اولویت بالا
            ('structure', 2),    # ساختار اولویت متوسط
            ('references', 1)    # منابع اولویت پایین
        ]
        
        for key, priority in priorities:
            recs = results[key].get('recommendations', [])
            for rec in recs:
                all_recommendations.append({
                    'text': rec,
                    'priority': priority,
                    'category': key
                })
        
        # مرتب‌سازی بر اساس اولویت
        all_recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return [r['text'] for r in all_recommendations[:7]]
    
    def get_final_report(
        self,
        proposal_data: Dict,
        nlp_scores: Dict = None
    ) -> Dict:
        """
        تولید گزارش نهایی با ترکیب NLP و LLM
        
        Args:
            proposal_data: داده‌های پروپوزال
            nlp_scores: نمرات NLP (نگارش و اصالت)
                {
                    'writing': float (0-100),
                    'originality': float (0-100)
                }
                
        Returns:
            dict: گزارش نهایی
        """
        # ارزیابی LLM
        llm_results = self.analyze_proposal(proposal_data)
        
        # نمرات NLP (اگر داده شده)
        writing_score = nlp_scores.get('writing', 0) if nlp_scores else 0
        originality_score = nlp_scores.get('originality', 0) if nlp_scores else 0
        
        # محاسبه نمره نهایی
        final_score = (
            writing_score * 0.25 +           # نگارش 25%
            llm_results['structure']['score'] * 0.20 +  # ساختار 20%
            llm_results['content']['score'] * 0.35 +    # محتوا 35%
            llm_results['references']['score'] * 0.15 + # منابع 15%
            originality_score * 0.05         # اصالت 5%
        )
        
        # تعیین درجه
        if final_score >= 85:
            grade = 'عالی'
            verdict = '✅ تأیید'
        elif final_score >= 70:
            grade = 'خوب'
            verdict = '✅ تأیید مشروط'
        elif final_score >= 55:
            grade = 'متوسط'
            verdict = '⚠️ نیاز به بازنگری'
        elif final_score >= 40:
            grade = 'ضعیف'
            verdict = '❌ نیاز به اصلاحات اساسی'
        else:
            grade = 'ناکافی'
            verdict = '❌ رد'
        
        return {
            'final_score': round(final_score, 2),
            'grade': grade,
            'verdict': verdict,
            'breakdown': {
                'writing': {
                    'score': writing_score,
                    'weight': '25%',
                    'contribution': round(writing_score * 0.25, 2)
                },
                'structure': {
                    'score': llm_results['structure']['score'],
                    'weight': '20%',
                    'contribution': round(llm_results['structure']['score'] * 0.20, 2)
                },
                'content': {
                    'score': llm_results['content']['score'],
                    'weight': '35%',
                    'contribution': round(llm_results['content']['score'] * 0.35, 2)
                },
                'references': {
                    'score': llm_results['references']['score'],
                    'weight': '15%',
                    'contribution': round(llm_results['references']['score'] * 0.15, 2)
                },
                'originality': {
                    'score': originality_score,
                    'weight': '5%',
                    'contribution': round(originality_score * 0.05, 2)
                }
            },
            'llm_details': llm_results,
            'recommendations': llm_results['priority_recommendations'],
            'generated_at': datetime.now().isoformat()
        }
    
    def is_ready(self) -> bool:
        """بررسی آمادگی سیستم"""
        return self.client.is_available()
    
    def get_status(self) -> Dict:
        """وضعیت سیستم"""
        return {
            'ollama_available': self.client.is_available(),
            'model': self.client.config.model,
            'model_available': self.client.is_model_available(),
            'available_models': self.client.list_models()
        }


# تست
if __name__ == "__main__":
    analyzer = LLMAnalyzer()
    
    print("=" * 60)
    print("🤖 تست LLMAnalyzer")
    print("=" * 60)
    
    # بررسی وضعیت
    status = analyzer.get_status()
    print(f"\n📊 وضعیت:")
    print(f"   Ollama: {'✅' if status['ollama_available'] else '❌'}")
    print(f"   مدل: {status['model']}")
    
    # داده تست
    test_data = {
        'sections': {
            'abstract': 'این پژوهش به بررسی هوش مصنوعی می‌پردازد. ' * 5,
            'introduction': 'مسئله اصلی این است که... ضرورت انجام این تحقیق... ' * 10,
            'methodology': 'روش تحقیق شامل جمع‌آوری داده و تحلیل است. ' * 10,
            'references': 'منابع...'
        },
        'metadata': {'word_count': 800, 'sentence_count': 40},
        'keywords': ['هوش مصنوعی', 'یادگیری ماشین'],
        'references': [
            'احمدی (1402). کتاب هوش مصنوعی. تهران.',
            'Smith, J. (2023). AI Applications. Journal of AI.'
        ]
    }
    
    # اجرا بدون LLM
    result = analyzer.analyze_proposal(test_data, use_llm=False)
    
    print(f"\n📊 نتایج (بدون LLM):")
    print(f"   نمره LLM: {result['llm_score']}/100")
    print(f"   سهم در کل: {result['llm_weighted']}/70")
    
    print(f"\n   ساختار: {result['structure']['score']}/100")
    print(f"   محتوا: {result['content']['score']}/100")
    print(f"   منابع: {result['references']['score']}/100")
    
    # گزارش نهایی
    final = analyzer.get_final_report(test_data, {
        'writing': 85,
        'originality': 90
    })
    
    print(f"\n🎯 گزارش نهایی:")
    print(f"   نمره نهایی: {final['final_score']}/100")
    print(f"   درجه: {final['grade']}")
    print(f"   رأی: {final['verdict']}")

