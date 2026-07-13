"""
ارزیاب محتوای پروپوزال
======================

این ماژول محتوای پروپوزال را با کمک LLM ارزیابی می‌کند.

Classes:
    ContentAnalyzer: ارزیاب محتوا (35% از نمره کل)

Example:
    >>> analyzer = ContentAnalyzer(client)
    >>> result = analyzer.analyze(sections, keywords)
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


class ContentAnalyzer:
    """
    کلاس ارزیابی محتوای پروپوزال
    
    این کلاس محتوای پروپوزال را ارزیابی می‌کند و 35% از نمره کل را تعیین می‌کند.
    
    معیارهای ارزیابی:
    - وضوح بیان مسئله
    - کیفیت روش‌شناسی
    - نوآوری
    - قابلیت اجرا
    - انسجام منطقی
    
    Attributes:
        client (OllamaClient): کلاینت Ollama
        weight (float): وزن در نمره کل (35%)
    """
    
    # کلمات کلیدی نشان‌دهنده کیفیت
    QUALITY_INDICATORS = {
        'problem': ['مسئله', 'مشکل', 'چالش', 'ضرورت', 'اهمیت', 'نیاز'],
        'objective': ['هدف', 'مقصد', 'منظور', 'غایت'],
        'method': ['روش', 'متد', 'رویکرد', 'شیوه', 'تکنیک'],
        'innovation': ['نوآوری', 'جدید', 'ابتکار', 'نوین', 'خلاقانه'],
        'result': ['نتیجه', 'یافته', 'دستاورد', 'حاصل']
    }
    
    def __init__(self, client: OllamaClient = None):
        """
        مقداردهی اولیه ContentAnalyzer
        
        Args:
            client: کلاینت Ollama
        """
        self.client = client or OllamaClient()
        self.prompt_manager = PromptManager()
        self.weight = 0.35  # 35% از نمره کل
    
    def analyze(
        self,
        sections: Dict[str, str],
        keywords: List[str] = None,
        use_llm: bool = True
    ) -> Dict:
        """
        ارزیابی کامل محتوا
        
        Args:
            sections: بخش‌های پروپوزال
            keywords: کلمات کلیدی
            use_llm: استفاده از LLM
            
        Returns:
            dict: نتایج ارزیابی
        """
        keywords = keywords or []
        
        # ارزیابی قاعده‌مند
        rule_based = self._rule_based_analysis(sections, keywords)
        
        # ارزیابی LLM
        llm_result = None
        if use_llm and self.client.is_available():
            llm_result = self._llm_analysis(sections, keywords)
        
        # ترکیب
        return self._combine_results(rule_based, llm_result)
    
    def _rule_based_analysis(
        self,
        sections: Dict[str, str],
        keywords: List[str]
    ) -> Dict:
        """
        ارزیابی قاعده‌مند محتوا
        """
        scores = {
            'problem_clarity': 0,
            'methodology_quality': 0,
            'innovation_level': 0,
            'feasibility': 0,
            'coherence': 0
        }
        
        issues = []
        strengths = []
        
        # 1. وضوح بیان مسئله (25 امتیاز)
        intro = sections.get('introduction', '') + sections.get('abstract', '')
        problem_count = sum(
            intro.count(word) for word in self.QUALITY_INDICATORS['problem']
        )
        if problem_count >= 3:
            scores['problem_clarity'] = 25
            strengths.append("مسئله تحقیق به خوبی بیان شده")
        elif problem_count >= 1:
            scores['problem_clarity'] = 15
        else:
            scores['problem_clarity'] = 5
            issues.append("بیان مسئله واضح نیست")
        
        # 2. کیفیت روش‌شناسی (25 امتیاز)
        method = sections.get('methodology', '')
        method_word_count = len(method.split())
        
        if method_word_count >= 200:
            scores['methodology_quality'] = 25
            strengths.append("روش‌شناسی مفصل است")
        elif method_word_count >= 100:
            scores['methodology_quality'] = 18
        elif method_word_count >= 50:
            scores['methodology_quality'] = 12
            issues.append("روش‌شناسی کوتاه است")
        else:
            scores['methodology_quality'] = 5
            issues.append("روش‌شناسی ناقص یا موجود نیست")
        
        # 3. نوآوری (20 امتیاز)
        all_text = ' '.join(sections.values())
        innovation_count = sum(
            all_text.count(word) for word in self.QUALITY_INDICATORS['innovation']
        )
        if innovation_count >= 3:
            scores['innovation_level'] = 20
            strengths.append("جنبه نوآورانه مشخص است")
        elif innovation_count >= 1:
            scores['innovation_level'] = 12
        else:
            scores['innovation_level'] = 5
            issues.append("نوآوری مشخص نیست")
        
        # 4. قابلیت اجرا (15 امتیاز)
        # بررسی وجود زمان‌بندی و جزئیات
        has_timeline = 'timeline' in sections or 'زمان' in all_text
        has_details = method_word_count >= 100
        
        if has_timeline and has_details:
            scores['feasibility'] = 15
            strengths.append("قابلیت اجرا مناسب")
        elif has_details:
            scores['feasibility'] = 10
        else:
            scores['feasibility'] = 5
            issues.append("جزئیات اجرایی کم است")
        
        # 5. انسجام (15 امتیاز)
        # بررسی ارتباط کلیدواژه‌ها با محتوا
        if keywords:
            keyword_matches = sum(1 for kw in keywords if kw in all_text)
            coherence_ratio = keyword_matches / len(keywords) if keywords else 0
            scores['coherence'] = int(15 * coherence_ratio)
        else:
            scores['coherence'] = 10
        
        total_score = sum(scores.values())
        
        return {
            'score': total_score,
            'method': 'rule_based',
            'subscores': scores,
            'issues': issues,
            'strengths': strengths,
            'recommendations': self._generate_recommendations(scores, issues)
        }
    
    def _llm_analysis(
        self,
        sections: Dict[str, str],
        keywords: List[str]
    ) -> Optional[Dict]:
        """
        ارزیابی با LLM
        """
        try:
            system_prompt, user_prompt = self.prompt_manager.build_content_prompt(
                sections, keywords
            )
            
            response = self.client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.0
            )
            
            if not response['success']:
                return None
            
            result = self._parse_llm_response(response['content'])
            result['method'] = 'llm'
            result['tokens'] = response['tokens']
            
            return result
            
        except Exception as e:
            logger.error(f"خطا در LLM: {e}")
            return None
    
    def _parse_llm_response(self, content: str) -> Dict:
        """پارس پاسخ JSON"""
        try:
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                return json.loads(json_match.group())
            return {'score': 50, 'parse_error': 'JSON not found'}
        except:
            return {'score': 50, 'parse_error': 'Invalid JSON'}
    
    def _combine_results(
        self,
        rule_based: Dict,
        llm_result: Optional[Dict]
    ) -> Dict:
        """ترکیب نتایج"""
        if llm_result is None:
            rule_based['combined'] = False
            rule_based['grade'] = self._get_grade(rule_based['score'])
            return rule_based
        
        # میانگین وزنی
        combined_score = (
            rule_based['score'] * 0.35 +
            llm_result.get('score', 50) * 0.65
        )
        
        return {
            'score': round(combined_score, 2),
            'grade': self._get_grade(combined_score),
            'combined': True,
            'rule_based_score': rule_based['score'],
            'llm_score': llm_result.get('score', 50),
            'subscores': {
                'problem_clarity': llm_result.get('problem_clarity', 
                    rule_based['subscores']['problem_clarity']),
                'methodology_quality': llm_result.get('methodology_quality',
                    rule_based['subscores']['methodology_quality']),
                'innovation_level': llm_result.get('innovation_level',
                    rule_based['subscores']['innovation_level']),
                'feasibility': llm_result.get('feasibility',
                    rule_based['subscores']['feasibility'])
            },
            'strengths': llm_result.get('strengths', []) or rule_based['strengths'],
            'weaknesses': llm_result.get('weaknesses', []) or rule_based['issues'],
            'content_gaps': llm_result.get('content_gaps', []),
            'recommendations': llm_result.get('recommendations', []) or rule_based['recommendations'],
            'summary': llm_result.get('summary', '')
        }
    
    def _generate_recommendations(
        self,
        scores: Dict[str, int],
        issues: List[str]
    ) -> List[str]:
        """تولید توصیه‌ها"""
        recommendations = []
        
        if scores['problem_clarity'] < 20:
            recommendations.append("بیان واضح‌تر مسئله و ضرورت تحقیق")
        if scores['methodology_quality'] < 20:
            recommendations.append("تشریح بیشتر روش‌شناسی و ابزارها")
        if scores['innovation_level'] < 15:
            recommendations.append("تأکید بر جنبه‌های نوآورانه تحقیق")
        if scores['feasibility'] < 10:
            recommendations.append("افزودن زمان‌بندی و جزئیات اجرایی")
        
        return recommendations
    
    def _get_grade(self, score: float) -> str:
        """تعیین درجه"""
        if score >= 85:
            return 'عالی'
        elif score >= 70:
            return 'خوب'
        elif score >= 55:
            return 'متوسط'
        elif score >= 40:
            return 'ضعیف'
        else:
            return 'ناکافی'
    
    def get_weighted_score(self, score: float) -> float:
        """
        تبدیل به نمره وزن‌دار
        
        Args:
            score: نمره خام (0-100)
            
        Returns:
            float: نمره وزن‌دار (0-35)
        """
        return (score / 100) * 35


# تست
if __name__ == "__main__":
    analyzer = ContentAnalyzer()
    
    test_sections = {
        'abstract': 'این پژوهش به بررسی مسئله کاربرد هوش مصنوعی می‌پردازد.',
        'introduction': 'اهمیت و ضرورت این تحقیق در چالش‌های موجود است. مشکل اصلی نبود سیستم مناسب است.',
        'methodology': 'روش تحقیق شامل جمع‌آوری داده، تحلیل و ارزیابی است. از رویکرد کمی استفاده می‌شود. ' * 5
    }
    
    result = analyzer.analyze(test_sections, ['هوش مصنوعی', 'یادگیری ماشین'], use_llm=False)
    
    print("=" * 60)
    print("📄 تست ارزیابی محتوا")
    print("=" * 60)
    print(f"\n📊 نمره: {result['score']}/100")
    print(f"📊 درجه: {result['grade']}")
    print(f"📊 نمره وزن‌دار: {analyzer.get_weighted_score(result['score']):.2f}/35")

