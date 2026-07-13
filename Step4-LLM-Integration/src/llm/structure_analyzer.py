"""
ارزیاب ساختار پروپوزال
=====================

این ماژول ساختار پروپوزال را با کمک LLM ارزیابی می‌کند.

Classes:
    StructureAnalyzer: ارزیاب ساختار (20% از نمره کل)

Example:
    >>> analyzer = StructureAnalyzer(client)
    >>> result = analyzer.analyze(sections, metadata)
    >>> print(result['score'])
"""

import json
import re
from typing import Dict, List, Optional
import logging

from .ollama_client import OllamaClient
from .prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StructureAnalyzer:
    """
    کلاس ارزیابی ساختار پروپوزال
    
    این کلاس ساختار پروپوزال را ارزیابی می‌کند و 20% از نمره کل را تعیین می‌کند.
    
    معیارهای ارزیابی:
    - وجود بخش‌های ضروری
    - ترتیب منطقی بخش‌ها
    - تناسب حجم
    - انسجام ساختاری
    
    Attributes:
        client (OllamaClient): کلاینت Ollama
        prompt_manager (PromptManager): مدیر پرامپت‌ها
        weight (float): وزن در نمره کل (20%)
        
    Example:
        >>> analyzer = StructureAnalyzer(client)
        >>> result = analyzer.analyze(sections, {'word_count': 1500})
        >>> print(f"نمره ساختار: {result['score']}/100")
    """
    
    # بخش‌های ضروری پروپوزال
    REQUIRED_SECTIONS = {
        'abstract': {'persian': 'چکیده', 'weight': 15},
        'introduction': {'persian': 'مقدمه', 'weight': 15},
        'methodology': {'persian': 'روش‌شناسی', 'weight': 20},
        'references': {'persian': 'منابع', 'weight': 15}
    }
    
    # بخش‌های تکمیلی
    OPTIONAL_SECTIONS = {
        'literature_review': {'persian': 'پیشینه پژوهش', 'weight': 10},
        'objectives': {'persian': 'اهداف', 'weight': 5},
        'hypotheses': {'persian': 'فرضیه‌ها', 'weight': 5},
        'conclusion': {'persian': 'نتیجه‌گیری', 'weight': 5},
        'keywords': {'persian': 'کلیدواژه‌ها', 'weight': 5},
        'timeline': {'persian': 'زمان‌بندی', 'weight': 5}
    }
    
    def __init__(self, client: OllamaClient = None):
        """
        مقداردهی اولیه StructureAnalyzer
        
        Args:
            client: کلاینت Ollama (اختیاری)
        """
        self.client = client or OllamaClient()
        self.prompt_manager = PromptManager()
        self.weight = 0.20  # 20% از نمره کل
    
    def analyze(
        self, 
        sections: Dict[str, str],
        metadata: Dict,
        use_llm: bool = True
    ) -> Dict:
        """
        ارزیابی کامل ساختار
        
        Args:
            sections: بخش‌های شناسایی شده
            metadata: متادیتا (آمار متن)
            use_llm: استفاده از LLM
            
        Returns:
            dict: نتایج ارزیابی
        """
        # ارزیابی قاعده‌مند (Rule-based)
        rule_based_result = self._rule_based_analysis(sections, metadata)
        
        # اگر LLM در دسترس و فعال باشد
        llm_result = None
        if use_llm and self.client.is_available():
            llm_result = self._llm_analysis(sections, metadata)
        
        # ترکیب نتایج
        final_result = self._combine_results(rule_based_result, llm_result)
        
        return final_result
    
    def _rule_based_analysis(
        self, 
        sections: Dict[str, str],
        metadata: Dict
    ) -> Dict:
        """
        ارزیابی قاعده‌مند ساختار
        
        Args:
            sections: بخش‌ها
            metadata: متادیتا
            
        Returns:
            dict: نتایج ارزیابی قاعده‌مند
        """
        score = 0
        max_score = 100
        missing_sections = []
        issues = []
        strengths = []
        
        # 1. بررسی بخش‌های ضروری (65 امتیاز)
        required_score = 0
        for section, info in self.REQUIRED_SECTIONS.items():
            if section in sections and sections[section]:
                content = sections[section]
                word_count = len(content.split())
                
                # بررسی حداقل طول
                if word_count >= 50:
                    required_score += info['weight']
                    strengths.append(f"بخش {info['persian']} کامل است")
                else:
                    required_score += info['weight'] * 0.5
                    issues.append(f"بخش {info['persian']} کوتاه است ({word_count} کلمه)")
            else:
                missing_sections.append(info['persian'])
        
        score += required_score
        
        # 2. بررسی بخش‌های تکمیلی (35 امتیاز)
        optional_score = 0
        for section, info in self.OPTIONAL_SECTIONS.items():
            if section in sections and sections[section]:
                optional_score += info['weight']
        
        score += optional_score
        
        # 3. بررسی تناسب حجم (تا -20 امتیاز جریمه)
        word_count = metadata.get('word_count', 0)
        if word_count < 500:
            penalty = 20
            issues.append(f"حجم کل خیلی کم است ({word_count} کلمه)")
        elif word_count < 1000:
            penalty = 10
            issues.append(f"حجم کل کمتر از حد انتظار است ({word_count} کلمه)")
        elif word_count > 10000:
            penalty = 10
            issues.append(f"حجم کل زیاد است ({word_count} کلمه)")
        else:
            penalty = 0
            strengths.append(f"حجم مناسب ({word_count} کلمه)")
        
        score = max(0, score - penalty)
        
        # 4. تولید توصیه‌ها
        recommendations = []
        if missing_sections:
            recommendations.append(f"افزودن بخش‌های: {', '.join(missing_sections)}")
        if word_count < 1000:
            recommendations.append("افزایش حجم محتوا")
        
        return {
            'score': round(score, 2),
            'method': 'rule_based',
            'breakdown': {
                'required_sections': required_score,
                'optional_sections': optional_score,
                'penalty': penalty
            },
            'missing_sections': missing_sections,
            'issues': issues,
            'strengths': strengths,
            'recommendations': recommendations
        }
    
    def _llm_analysis(
        self, 
        sections: Dict[str, str],
        metadata: Dict
    ) -> Optional[Dict]:
        """
        ارزیابی با LLM
        
        Args:
            sections: بخش‌ها
            metadata: متادیتا
            
        Returns:
            dict یا None: نتایج LLM
        """
        try:
            # ساخت پرامپت
            system_prompt, user_prompt = self.prompt_manager.build_structure_prompt(
                sections, metadata
            )
            
            # ارسال به LLM
            response = self.client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            if not response['success']:
                logger.warning(f"خطای LLM: {response['error']}")
                return None
            
            # پارس JSON
            result = self._parse_llm_response(response['content'])
            result['method'] = 'llm'
            result['tokens'] = response['tokens']
            result['duration'] = response['duration']
            
            return result
            
        except Exception as e:
            logger.error(f"خطا در ارزیابی LLM: {e}")
            return None
    
    def _parse_llm_response(self, content: str) -> Dict:
        """
        پارس پاسخ JSON از LLM
        
        Args:
            content: پاسخ LLM
            
        Returns:
            dict: داده‌های پارس شده
        """
        try:
            # پیدا کردن JSON در پاسخ
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            
            # اگر JSON نبود، ساختار پیش‌فرض
            return {
                'score': 50,
                'raw_response': content,
                'parse_error': 'JSON not found'
            }
            
        except json.JSONDecodeError as e:
            logger.warning(f"خطای پارس JSON: {e}")
            return {
                'score': 50,
                'raw_response': content,
                'parse_error': str(e)
            }
    
    def _combine_results(
        self, 
        rule_based: Dict,
        llm_result: Optional[Dict]
    ) -> Dict:
        """
        ترکیب نتایج قاعده‌مند و LLM
        
        Args:
            rule_based: نتایج قاعده‌مند
            llm_result: نتایج LLM
            
        Returns:
            dict: نتایج ترکیبی
        """
        if llm_result is None:
            rule_based['combined'] = False
            return rule_based
        
        # میانگین وزنی
        rule_weight = 0.4
        llm_weight = 0.6
        
        combined_score = (
            rule_based['score'] * rule_weight +
            llm_result.get('score', 50) * llm_weight
        )
        
        return {
            'score': round(combined_score, 2),
            'grade': self._get_grade(combined_score),
            'combined': True,
            'rule_based_score': rule_based['score'],
            'llm_score': llm_result.get('score', 50),
            'missing_sections': rule_based.get('missing_sections', []),
            'issues': rule_based.get('issues', []) + llm_result.get('structure_issues', []),
            'strengths': rule_based.get('strengths', []) + llm_result.get('strengths', []),
            'recommendations': llm_result.get('recommendations', rule_based.get('recommendations', [])),
            'summary': llm_result.get('summary', ''),
            'breakdown': rule_based.get('breakdown', {}),
            'llm_details': {
                'tokens': llm_result.get('tokens', 0),
                'duration': llm_result.get('duration', 0)
            }
        }
    
    def _get_grade(self, score: float) -> str:
        """تعیین درجه"""
        if score >= 90:
            return 'عالی'
        elif score >= 75:
            return 'خوب'
        elif score >= 60:
            return 'متوسط'
        elif score >= 40:
            return 'ضعیف'
        else:
            return 'ناقص'
    
    def get_weighted_score(self, score: float) -> float:
        """
        تبدیل به نمره وزن‌دار
        
        Args:
            score: نمره خام (0-100)
            
        Returns:
            float: نمره وزن‌دار (0-20)
        """
        return (score / 100) * 20


# تست ماژول
if __name__ == "__main__":
    analyzer = StructureAnalyzer()
    
    # داده تست
    test_sections = {
        'abstract': 'این پروپوزال به بررسی کاربرد هوش مصنوعی می‌پردازد. ' * 10,
        'introduction': 'در سال‌های اخیر هوش مصنوعی رشد زیادی داشته است. ' * 20,
        'methodology': 'روش تحقیق شامل جمع‌آوری داده و تحلیل است. ' * 15,
        'references': 'منابع متعددی استفاده شده است.'
    }
    
    test_metadata = {
        'word_count': 500,
        'sentence_count': 30
    }
    
    print("=" * 60)
    print("🏗️ تست ارزیابی ساختار")
    print("=" * 60)
    
    result = analyzer.analyze(test_sections, test_metadata, use_llm=False)
    
    print(f"\n📊 نمره ساختار: {result['score']}/100")
    print(f"📊 نمره وزن‌دار: {analyzer.get_weighted_score(result['score']):.2f}/20")
    
    if result.get('missing_sections'):
        print(f"\n❌ بخش‌های ناقص: {', '.join(result['missing_sections'])}")
    
    if result.get('issues'):
        print(f"\n⚠️ مشکلات:")
        for issue in result['issues'][:5]:
            print(f"   • {issue}")
    
    if result.get('strengths'):
        print(f"\n✅ نقاط قوت:")
        for s in result['strengths'][:5]:
            print(f"   • {s}")

