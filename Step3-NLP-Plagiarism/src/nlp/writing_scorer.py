"""
ماژول محاسبه نمره نگارشی
========================

این ماژول نمره نگارشی (25% از نمره کل) را محاسبه می‌کند.

Classes:
    WritingScorer: محاسبه نمره نگارشی

Example:
    >>> scorer = WritingScorer()
    >>> result = scorer.score(text)
    >>> print(f"نمره نگارش: {result['final_score']}")
"""

from typing import Dict, List, Optional
import logging

from .grammar_checker import GrammarChecker
from .text_statistics import TextStatistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WritingScorer:
    """
    کلاس محاسبه نمره نگارشی
    
    نمره نگارشی شامل سه بخش است:
    - املا: 40% (از نمره نگارش)
    - گرامر: 30%
    - خوانایی: 30%
    
    نمره نگارش = 25% از نمره کل پروپوزال
    
    Attributes:
        grammar_checker (GrammarChecker): بررسی‌کننده گرامر
        text_stats (TextStatistics): آمار متنی
        
    Example:
        >>> scorer = WritingScorer()
        >>> result = scorer.score(text)
        >>> print(f"نمره نهایی: {result['final_score']}/100")
    """
    
    # وزن هر بخش در نمره نگارشی
    WEIGHTS = {
        'spelling': 0.40,    # 40%
        'grammar': 0.30,     # 30%
        'readability': 0.30  # 30%
    }
    
    # آستانه‌های خطا
    THRESHOLDS = {
        'excellent': 95,     # عالی
        'good': 80,          # خوب
        'average': 60,       # متوسط
        'poor': 40           # ضعیف
    }
    
    def __init__(self):
        """مقداردهی اولیه WritingScorer"""
        self.grammar_checker = GrammarChecker()
        self.text_stats = TextStatistics()
    
    def score(self, text: str) -> Dict:
        """
        محاسبه نمره نگارشی کامل
        
        Args:
            text: متن ورودی
            
        Returns:
            dict: نتایج کامل امتیازدهی
            {
                'final_score': float,
                'grade': str,
                'spelling_score': float,
                'grammar_score': float,
                'readability_score': float,
                'details': dict,
                'feedback': list
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # بررسی گرامر و املا
        grammar_result = self.grammar_checker.check(text)
        
        # آمار متنی
        stats_result = self.text_stats.analyze(text)
        
        # محاسبه نمرات جزئی
        spelling_score = self._calculate_spelling_score(grammar_result)
        grammar_score = self._calculate_grammar_score(grammar_result)
        readability_score = self._calculate_readability_score(stats_result)
        
        # محاسبه نمره نهایی
        final_score = (
            spelling_score * self.WEIGHTS['spelling'] +
            grammar_score * self.WEIGHTS['grammar'] +
            readability_score * self.WEIGHTS['readability']
        )
        
        # تعیین درجه
        grade = self._get_grade(final_score)
        
        # تولید بازخورد
        feedback = self._generate_feedback(
            spelling_score, grammar_score, readability_score,
            grammar_result, stats_result
        )
        
        return {
            'final_score': round(final_score, 2),
            'grade': grade,
            'spelling_score': round(spelling_score, 2),
            'grammar_score': round(grammar_score, 2),
            'readability_score': round(readability_score, 2),
            'weights': self.WEIGHTS,
            'details': {
                'spelling_errors': grammar_result['spelling_error_count'],
                'grammar_errors': grammar_result['grammar_error_count'],
                'half_space_errors': len(grammar_result['half_space_errors']),
                'readability_level': stats_result['readability_level'],
                'lexical_diversity': stats_result['lexical_diversity'],
                'avg_sentence_length': stats_result['avg_sentence_length']
            },
            'feedback': feedback
        }
    
    def _calculate_spelling_score(self, grammar_result: Dict) -> float:
        """
        محاسبه نمره املا
        
        Args:
            grammar_result: نتایج بررسی گرامر
            
        Returns:
            float: نمره املا (0-100)
        """
        accuracy = grammar_result.get('spelling_accuracy', 100)
        
        # اگر دقت بالای 98% باشد، 100 امتیاز
        if accuracy >= 98:
            return 100
        elif accuracy >= 95:
            return 90 + (accuracy - 95) * 2
        elif accuracy >= 90:
            return 70 + (accuracy - 90) * 4
        elif accuracy >= 80:
            return 50 + (accuracy - 80) * 2
        else:
            return max(0, accuracy * 0.6)
    
    def _calculate_grammar_score(self, grammar_result: Dict) -> float:
        """
        محاسبه نمره گرامر
        
        Args:
            grammar_result: نتایج بررسی گرامر
            
        Returns:
            float: نمره گرامر (0-100)
        """
        grammar_score = grammar_result.get('grammar_score', 100)
        half_space_errors = len(grammar_result.get('half_space_errors', []))
        
        # کاهش نمره برای خطاهای نیم‌فاصله
        half_space_penalty = min(half_space_errors * 2, 20)
        
        final = grammar_score - half_space_penalty
        return max(0, final)
    
    def _calculate_readability_score(self, stats_result: Dict) -> float:
        """
        محاسبه نمره خوانایی
        
        Args:
            stats_result: نتایج آمار متنی
            
        Returns:
            float: نمره خوانایی (0-100)
        """
        base_score = stats_result.get('readability_score', 50)
        
        # بونوس/جریمه برای تنوع واژگانی
        diversity = stats_result.get('lexical_diversity', 0)
        if 0.3 <= diversity <= 0.6:
            diversity_bonus = 10  # تنوع ایده‌آل
        elif diversity < 0.2:
            diversity_bonus = -10  # تکرار زیاد
        elif diversity > 0.8:
            diversity_bonus = -5  # خیلی متنوع (شاید ناپیوسته)
        else:
            diversity_bonus = 5
        
        # بونوس/جریمه برای طول جملات
        avg_len = stats_result.get('avg_sentence_length', 15)
        if 12 <= avg_len <= 22:
            length_bonus = 10  # طول ایده‌آل
        elif avg_len < 8:
            length_bonus = -10  # جملات خیلی کوتاه
        elif avg_len > 30:
            length_bonus = -15  # جملات خیلی بلند
        else:
            length_bonus = 0
        
        final = base_score + diversity_bonus + length_bonus
        return max(0, min(100, final))
    
    def _get_grade(self, score: float) -> str:
        """
        تعیین درجه بر اساس نمره
        
        Args:
            score: نمره نهایی
            
        Returns:
            str: درجه
        """
        if score >= self.THRESHOLDS['excellent']:
            return 'عالی'
        elif score >= self.THRESHOLDS['good']:
            return 'خوب'
        elif score >= self.THRESHOLDS['average']:
            return 'متوسط'
        elif score >= self.THRESHOLDS['poor']:
            return 'ضعیف'
        else:
            return 'نیاز به بازنگری'
    
    def _generate_feedback(
        self,
        spelling_score: float,
        grammar_score: float,
        readability_score: float,
        grammar_result: Dict,
        stats_result: Dict
    ) -> List[str]:
        """
        تولید بازخورد بر اساس نتایج
        
        Args:
            spelling_score: نمره املا
            grammar_score: نمره گرامر
            readability_score: نمره خوانایی
            grammar_result: نتایج گرامر
            stats_result: نتایج آمار
            
        Returns:
            list: لیست بازخوردها
        """
        feedback = []
        
        # بازخورد املا
        if spelling_score >= 95:
            feedback.append("✅ املای متن بسیار خوب است.")
        elif spelling_score >= 80:
            feedback.append(
                f"⚠️ تعداد {grammar_result['spelling_error_count']} خطای املایی یافت شد. "
                "لطفاً بازبینی کنید."
            )
        else:
            feedback.append(
                "❌ تعداد زیادی خطای املایی وجود دارد. "
                "پیشنهاد می‌شود از ویراستار استفاده کنید."
            )
        
        # بازخورد گرامر
        if grammar_score >= 95:
            feedback.append("✅ گرامر و نگارش متن استاندارد است.")
        elif grammar_score >= 80:
            half_space_count = len(grammar_result['half_space_errors'])
            if half_space_count > 0:
                feedback.append(
                    f"⚠️ {half_space_count} مورد استفاده نادرست از نیم‌فاصله. "
                    "از Ctrl+Shift+2 استفاده کنید."
                )
        else:
            feedback.append(
                "❌ مشکلات گرامری متعددی وجود دارد. "
                "لطفاً قواعد نگارش فارسی را رعایت کنید."
            )
        
        # بازخورد خوانایی
        level = stats_result['readability_level']
        avg_len = stats_result['avg_sentence_length']
        
        if readability_score >= 80:
            feedback.append(f"✅ خوانایی متن {level} است.")
        else:
            if avg_len > 25:
                feedback.append(
                    "⚠️ جملات خیلی بلند هستند. "
                    "پیشنهاد: جملات را کوتاه‌تر و ساده‌تر بنویسید."
                )
            elif avg_len < 10:
                feedback.append(
                    "⚠️ جملات خیلی کوتاه هستند. "
                    "پیشنهاد: جملات را با جزئیات بیشتری بنویسید."
                )
        
        # بازخورد تنوع واژگانی
        diversity = stats_result['lexical_diversity']
        if diversity < 0.2:
            feedback.append(
                "⚠️ تکرار کلمات زیاد است. "
                "پیشنهاد: از مترادف‌ها استفاده کنید."
            )
        elif diversity > 0.7:
            feedback.append(
                "💡 تنوع واژگانی زیاد است. "
                "مطمئن شوید متن پیوستگی دارد."
            )
        
        return feedback
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'final_score': 0,
            'grade': 'نامشخص',
            'spelling_score': 0,
            'grammar_score': 0,
            'readability_score': 0,
            'weights': self.WEIGHTS,
            'details': {},
            'feedback': ['متنی برای ارزیابی وجود ندارد.']
        }
    
    def get_weighted_score(self, score: float, total_weight: float = 25) -> float:
        """
        تبدیل نمره به وزن نهایی
        
        نمره نگارش = 25% از نمره کل
        
        Args:
            score: نمره نگارشی (0-100)
            total_weight: وزن در نمره کل (پیش‌فرض 25%)
            
        Returns:
            float: نمره وزن‌دار
        """
        return (score / 100) * total_weight


# تست ماژول
if __name__ == "__main__":
    scorer = WritingScorer()
    
    test_text = """
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان طبیعی فارسی میپردازد.
    هدف اصلی طراحی یک سیستم هوشمند برای تحلیل احساسات متون فارسی است.
    روش شناسی این پژوهش شامل جمع آوری داده های متنی از شبکه های اجتماعی فارسی زبان است.
    مدل پیشنهادی از معماری ترنسفورمر استفاده میکند که عملکرد خوبی دارد.
    نتایج نشان میدهد که مدل پیشنهادی با دقت 92 درصد عملکرد بهتری دارد.
    """
    
    result = scorer.score(test_text)
    
    print("=" * 60)
    print("📝 نمره نگارشی")
    print("=" * 60)
    
    print(f"\n🎯 نمره نهایی: {result['final_score']}/100")
    print(f"📊 درجه: {result['grade']}")
    
    print("\n📈 نمرات جزئی:")
    print(f"   املا (40%): {result['spelling_score']}")
    print(f"   گرامر (30%): {result['grammar_score']}")
    print(f"   خوانایی (30%): {result['readability_score']}")
    
    print("\n📋 جزئیات:")
    for key, value in result['details'].items():
        print(f"   {key}: {value}")
    
    print("\n💬 بازخوردها:")
    for fb in result['feedback']:
        print(f"   {fb}")
    
    # نمره وزن‌دار برای کل پروپوزال
    weighted = scorer.get_weighted_score(result['final_score'])
    print(f"\n🔢 سهم در نمره کل پروپوزال: {weighted:.2f}/25")

