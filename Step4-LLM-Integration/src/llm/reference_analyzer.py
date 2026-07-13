"""
ارزیاب منابع پروپوزال
=====================

این ماژول منابع پروپوزال را ارزیابی می‌کند.

Classes:
    ReferenceAnalyzer: ارزیاب منابع (15% از نمره کل)

Example:
    >>> analyzer = ReferenceAnalyzer(client)
    >>> result = analyzer.analyze(references)
    >>> print(result['score'])
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

from .ollama_client import OllamaClient
from .prompt_manager import PromptManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReferenceAnalyzer:
    """
    کلاس ارزیابی منابع پروپوزال
    
    این کلاس منابع پروپوزال را ارزیابی می‌کند و 15% از نمره کل را تعیین می‌کند.
    
    معیارهای ارزیابی:
    - کمیت منابع (تعداد کافی)
    - کیفیت منابع (نوع منابع)
    - به‌روز بودن (قدمت)
    - ارتباط با موضوع
    
    Attributes:
        client (OllamaClient): کلاینت Ollama
        weight (float): وزن در نمره کل (15%)
    """
    
    # الگوهای شناسایی سال
    YEAR_PATTERNS = [
        r'\b(19|20)\d{2}\b',           # سال میلادی
        r'\b13[89]\d\b',                # سال شمسی 1380-1399
        r'\b14[01234]\d\b',             # سال شمسی 1400-1449
    ]
    
    # کلمات کلیدی منابع انگلیسی
    ENGLISH_INDICATORS = [
        'and', 'the', 'of', 'in', 'for', 'journal', 'vol', 'pp', 'doi'
    ]
    
    def __init__(self, client: OllamaClient = None):
        """
        مقداردهی اولیه ReferenceAnalyzer
        
        Args:
            client: کلاینت Ollama
        """
        self.client = client or OllamaClient()
        self.prompt_manager = PromptManager()
        self.weight = 0.15  # 15% از نمره کل
        self.current_year = datetime.now().year
    
    def analyze(
        self,
        references: List[str],
        use_llm: bool = True
    ) -> Dict:
        """
        ارزیابی کامل منابع
        
        Args:
            references: لیست منابع
            use_llm: استفاده از LLM
            
        Returns:
            dict: نتایج ارزیابی
        """
        if not references:
            return self._empty_result()
        
        # تحلیل آماری منابع
        stats = self._analyze_references_stats(references)
        
        # ارزیابی قاعده‌مند
        rule_based = self._rule_based_analysis(references, stats)
        
        # ارزیابی LLM
        llm_result = None
        if use_llm and self.client.is_available():
            llm_result = self._llm_analysis(references, stats)
        
        # ترکیب
        return self._combine_results(rule_based, llm_result, stats)
    
    def _analyze_references_stats(self, references: List[str]) -> Dict:
        """
        تحلیل آماری منابع
        
        Args:
            references: لیست منابع
            
        Returns:
            dict: آمار منابع
        """
        total = len(references)
        years = []
        persian_count = 0
        english_count = 0
        
        for ref in references:
            # استخراج سال
            year = self._extract_year(ref)
            if year:
                years.append(year)
            
            # تشخیص زبان
            if self._is_english(ref):
                english_count += 1
            else:
                persian_count += 1
        
        # محاسبه آمار سال‌ها
        recent_5_years = 0
        recent_10_years = 0
        
        for year in years:
            if year >= self.current_year - 5:
                recent_5_years += 1
            if year >= self.current_year - 10:
                recent_10_years += 1
        
        return {
            'total_count': total,
            'persian_count': persian_count,
            'english_count': english_count,
            'years': years,
            'recent_5_years': recent_5_years,
            'recent_10_years': recent_10_years,
            'oldest_year': min(years) if years else None,
            'newest_year': max(years) if years else None,
            'avg_year': sum(years) / len(years) if years else None
        }
    
    def _extract_year(self, reference: str) -> Optional[int]:
        """استخراج سال از منبع"""
        for pattern in self.YEAR_PATTERNS:
            match = re.search(pattern, reference)
            if match:
                year = int(match.group())
                # تبدیل شمسی به میلادی
                if 1380 <= year <= 1450:
                    year = year + 621
                return year
        return None
    
    def _is_english(self, reference: str) -> bool:
        """تشخیص منبع انگلیسی"""
        ref_lower = reference.lower()
        english_count = sum(1 for word in self.ENGLISH_INDICATORS if word in ref_lower)
        return english_count >= 2
    
    def _rule_based_analysis(
        self,
        references: List[str],
        stats: Dict
    ) -> Dict:
        """
        ارزیابی قاعده‌مند
        """
        scores = {
            'quantity': 0,
            'recency': 0,
            'diversity': 0,
            'quality': 0
        }
        
        issues = []
        strengths = []
        
        # 1. کمیت (25 امتیاز)
        count = stats['total_count']
        if count >= 20:
            scores['quantity'] = 25
            strengths.append(f"تعداد منابع کافی ({count} منبع)")
        elif count >= 15:
            scores['quantity'] = 20
            strengths.append(f"تعداد منابع مناسب ({count} منبع)")
        elif count >= 10:
            scores['quantity'] = 15
        elif count >= 5:
            scores['quantity'] = 10
            issues.append(f"تعداد منابع کم است ({count} منبع)")
        else:
            scores['quantity'] = 5
            issues.append(f"تعداد منابع ناکافی ({count} منبع)")
        
        # 2. به‌روز بودن (30 امتیاز)
        if stats['years']:
            recent_ratio = stats['recent_5_years'] / len(stats['years'])
            if recent_ratio >= 0.6:
                scores['recency'] = 30
                strengths.append("اکثر منابع به‌روز هستند")
            elif recent_ratio >= 0.4:
                scores['recency'] = 22
            elif recent_ratio >= 0.2:
                scores['recency'] = 15
                issues.append("بخشی از منابع قدیمی هستند")
            else:
                scores['recency'] = 8
                issues.append("اکثر منابع قدیمی هستند")
        else:
            scores['recency'] = 15  # اگر سال مشخص نباشد
        
        # 3. تنوع (25 امتیاز)
        persian_ratio = stats['persian_count'] / count if count > 0 else 0
        english_ratio = stats['english_count'] / count if count > 0 else 0
        
        # تنوع ایده‌آل: 30-70% فارسی و 30-70% انگلیسی
        if 0.3 <= persian_ratio <= 0.7 and 0.3 <= english_ratio <= 0.7:
            scores['diversity'] = 25
            strengths.append("تنوع خوب منابع فارسی و انگلیسی")
        elif persian_ratio > 0 and english_ratio > 0:
            scores['diversity'] = 18
        else:
            scores['diversity'] = 10
            if english_ratio == 0:
                issues.append("منابع انگلیسی ندارد")
            if persian_ratio == 0:
                issues.append("منابع فارسی ندارد")
        
        # 4. کیفیت فرمت (20 امتیاز)
        # بررسی ساده فرمت منابع
        formatted_count = 0
        for ref in references:
            # بررسی وجود عناصر استاندارد
            has_author = bool(re.search(r'[،,]', ref))
            has_year = bool(self._extract_year(ref))
            has_title = len(ref) > 50
            
            if sum([has_author, has_year, has_title]) >= 2:
                formatted_count += 1
        
        format_ratio = formatted_count / count if count > 0 else 0
        scores['quality'] = int(20 * format_ratio)
        
        if format_ratio >= 0.8:
            strengths.append("فرمت استناددهی مناسب")
        elif format_ratio < 0.5:
            issues.append("فرمت برخی منابع استاندارد نیست")
        
        total_score = sum(scores.values())
        
        return {
            'score': total_score,
            'method': 'rule_based',
            'subscores': scores,
            'issues': issues,
            'strengths': strengths,
            'recommendations': self._generate_recommendations(stats, issues)
        }
    
    def _llm_analysis(
        self,
        references: List[str],
        stats: Dict
    ) -> Optional[Dict]:
        """ارزیابی با LLM"""
        try:
            system_prompt, user_prompt = self.prompt_manager.build_references_prompt(
                references, stats
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
            return {'score': 50}
        except:
            return {'score': 50}
    
    def _combine_results(
        self,
        rule_based: Dict,
        llm_result: Optional[Dict],
        stats: Dict
    ) -> Dict:
        """ترکیب نتایج"""
        if llm_result is None:
            rule_based['combined'] = False
            rule_based['grade'] = self._get_grade(rule_based['score'])
            rule_based['statistics'] = stats
            return rule_based
        
        combined_score = (
            rule_based['score'] * 0.4 +
            llm_result.get('score', 50) * 0.6
        )
        
        return {
            'score': round(combined_score, 2),
            'grade': self._get_grade(combined_score),
            'combined': True,
            'rule_based_score': rule_based['score'],
            'llm_score': llm_result.get('score', 50),
            'subscores': {
                'quantity': llm_result.get('quantity_score', rule_based['subscores']['quantity']),
                'quality': llm_result.get('quality_score', rule_based['subscores']['quality']),
                'recency': llm_result.get('recency_score', rule_based['subscores']['recency']),
                'relevance': llm_result.get('relevance_score', 50)
            },
            'statistics': stats,
            'issues': llm_result.get('issues', []) or rule_based['issues'],
            'strengths': llm_result.get('strengths', []) or rule_based['strengths'],
            'recommendations': llm_result.get('recommendations', []) or rule_based['recommendations'],
            'summary': llm_result.get('summary', '')
        }
    
    def _generate_recommendations(self, stats: Dict, issues: List[str]) -> List[str]:
        """تولید توصیه‌ها"""
        recommendations = []
        
        if stats['total_count'] < 15:
            recommendations.append(f"افزودن حداقل {15 - stats['total_count']} منبع دیگر")
        
        if stats['recent_5_years'] < 5:
            recommendations.append("استفاده از منابع جدیدتر (5 سال اخیر)")
        
        if stats['english_count'] < 5:
            recommendations.append("افزودن منابع انگلیسی معتبر")
        
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
    
    def _empty_result(self) -> Dict:
        """نتیجه خالی"""
        return {
            'score': 0,
            'grade': 'ناقص',
            'combined': False,
            'issues': ['منابعی یافت نشد'],
            'recommendations': ['افزودن منابع معتبر']
        }
    
    def get_weighted_score(self, score: float) -> float:
        """
        تبدیل به نمره وزن‌دار
        
        Args:
            score: نمره خام (0-100)
            
        Returns:
            float: نمره وزن‌دار (0-15)
        """
        return (score / 100) * 15


# تست
if __name__ == "__main__":
    analyzer = ReferenceAnalyzer()
    
    test_refs = [
        "احمدی، علی (1402). هوش مصنوعی در آموزش. تهران: نشر دانش.",
        "رضایی، حسین و کریمی، زهرا (1399). یادگیری ماشین. فصلنامه علوم کامپیوتر، 15(2)، 45-60.",
        "Smith, J., & Brown, K. (2022). Deep Learning Applications. Journal of AI, 10(3), 123-140.",
        "Johnson, M. (2021). Neural Networks in Education. IEEE Trans., vol. 8, pp. 89-102.",
        "محمدی، رضا (1398). داده‌کاوی در پژوهش. مجله پژوهش، 12(1)، 15-28.",
    ]
    
    result = analyzer.analyze(test_refs, use_llm=False)
    
    print("=" * 60)
    print("📚 تست ارزیابی منابع")
    print("=" * 60)
    print(f"\n📊 نمره: {result['score']}/100")
    print(f"📊 درجه: {result['grade']}")
    print(f"📊 نمره وزن‌دار: {analyzer.get_weighted_score(result['score']):.2f}/15")
    
    stats = result.get('statistics', {})
    print(f"\n📈 آمار:")
    print(f"   کل: {stats.get('total_count', 0)}")
    print(f"   فارسی: {stats.get('persian_count', 0)}")
    print(f"   انگلیسی: {stats.get('english_count', 0)}")
    print(f"   5 سال اخیر: {stats.get('recent_5_years', 0)}")

