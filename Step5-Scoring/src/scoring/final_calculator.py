"""
ماژول محاسبه نمره نهایی پروپوزال
این ماژول تمام نمرات جزئی را تجمیع و نمره نهایی را محاسبه می‌کند
"""

from typing import Dict, Optional, List
from datetime import datetime
from loguru import logger


class FinalScoreCalculator:
    """
    محاسبه‌گر نمره نهایی پروپوزال
    
    این کلاس تمام نمرات جزئی را با وزن‌های مشخص ترکیب می‌کند:
    - نگارش: 25%
    - ساختار: 20%
    - محتوا: 35%
    - منابع: 15%
    - اصالت: 5%
    """
    
    # وزن‌های ثابت برای هر معیار
    WEIGHTS = {
        'writing': 0.25,      # نگارش: 25%
        'structure': 0.20,    # ساختار: 20%
        'content': 0.35,      # محتوا: 35%
        'references': 0.15,   # منابع: 15%
        'originality': 0.05   # اصالت: 5%
    }
    
    # آستانه‌های درجه‌بندی
    GRADE_THRESHOLDS = {
        'excellent': 90,
        'very_good': 85,
        'good': 80,
        'above_average': 75,
        'average': 70,
        'below_average': 60,
        'weak': 50,
        'very_weak': 40
    }
    
    def __init__(self):
        """مقداردهی اولیه"""
        # اعتبارسنجی وزن‌ها
        total_weight = sum(self.WEIGHTS.values())
        if abs(total_weight - 1.0) > 0.001:
            raise ValueError(f"مجموع وزن‌ها باید 1 باشد، نه {total_weight}")
        
        logger.info("FinalScoreCalculator initialized")
    
    def calculate(
        self,
        writing_score: float,
        structure_score: float,
        content_score: float,
        references_score: float,
        originality_score: float,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        محاسبه نمره نهایی از ترکیب وزنی تمام نمرات
        
        Args:
            writing_score: نمره نگارشی (0-100)
            structure_score: نمره ساختار (0-100)
            content_score: نمره محتوا (0-100)
            references_score: نمره منابع (0-100)
            originality_score: نمره اصالت (0-100)
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict شامل نمره نهایی و جزئیات کامل
        """
        logger.info("Calculating final score")
        
        # اعتبارسنجی نمرات ورودی
        scores = {
            'writing': writing_score,
            'structure': structure_score,
            'content': content_score,
            'references': references_score,
            'originality': originality_score
        }
        
        self._validate_scores(scores)
        
        # محاسبه نمره نهایی (میانگین وزن‌دار)
        final_score = (
            writing_score * self.WEIGHTS['writing'] +
            structure_score * self.WEIGHTS['structure'] +
            content_score * self.WEIGHTS['content'] +
            references_score * self.WEIGHTS['references'] +
            originality_score * self.WEIGHTS['originality']
        )
        
        # محاسبه نمرات وزن‌دار هر بخش
        weighted_scores = {
            'writing': writing_score * self.WEIGHTS['writing'],
            'structure': structure_score * self.WEIGHTS['structure'],
            'content': content_score * self.WEIGHTS['content'],
            'references': references_score * self.WEIGHTS['references'],
            'originality': originality_score * self.WEIGHTS['originality']
        }
        
        # تعیین درجه کلی
        grade = self._calculate_grade(final_score)
        
        # تحلیل نقاط قوت و ضعف
        strengths, weaknesses = self._analyze_strengths_weaknesses(scores)
        
        # محاسبه آمار
        statistics = self._calculate_statistics(scores)
        
        # تولید توصیه‌ها
        recommendations = self._generate_recommendations(scores, final_score)
        
        # ساخت گزارش نهایی
        result = {
            'final_score': round(final_score, 2),
            'grade': grade,
            'level': self._get_level(final_score),
            'individual_scores': {
                'writing': round(writing_score, 2),
                'structure': round(structure_score, 2),
                'content': round(content_score, 2),
                'references': round(references_score, 2),
                'originality': round(originality_score, 2)
            },
            'weighted_scores': {
                k: round(v, 2) for k, v in weighted_scores.items()
            },
            'weights': self.WEIGHTS,
            'statistics': statistics,
            'analysis': {
                'strengths': strengths,
                'weaknesses': weaknesses,
                'dominant_criterion': self._find_dominant_criterion(scores),
                'weakest_criterion': self._find_weakest_criterion(scores)
            },
            'recommendations': recommendations,
            'pass': final_score >= 60,  # حداقل نمره قبولی
            'evaluated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Final score calculated: {final_score:.2f}/100 ({grade})")
        return result
    
    def _validate_scores(self, scores: Dict[str, float]) -> None:
        """اعتبارسنجی نمرات ورودی"""
        for criterion, score in scores.items():
            if not isinstance(score, (int, float)):
                raise TypeError(
                    f"نمره {criterion} باید عدد باشد، نه {type(score)}"
                )
            if not 0 <= score <= 100:
                raise ValueError(
                    f"نمره {criterion} باید بین 0 تا 100 باشد، نه {score}"
                )
    
    def _calculate_grade(self, score: float) -> str:
        """تعیین درجه بر اساس نمره نهایی"""
        if score >= self.GRADE_THRESHOLDS['excellent']:
            return 'عالی'
        elif score >= self.GRADE_THRESHOLDS['very_good']:
            return 'خیلی خوب'
        elif score >= self.GRADE_THRESHOLDS['good']:
            return 'خوب'
        elif score >= self.GRADE_THRESHOLDS['above_average']:
            return 'بالاتر از متوسط'
        elif score >= self.GRADE_THRESHOLDS['average']:
            return 'متوسط'
        elif score >= self.GRADE_THRESHOLDS['below_average']:
            return 'قابل قبول'
        elif score >= self.GRADE_THRESHOLDS['weak']:
            return 'ضعیف'
        elif score >= self.GRADE_THRESHOLDS['very_weak']:
            return 'بسیار ضعیف'
        else:
            return 'نیاز به بازنویسی کامل'
    
    def _get_level(self, score: float) -> str:
        """تعیین سطح کلی پروپوزال"""
        if score >= 85:
            return 'A'
        elif score >= 75:
            return 'B'
        elif score >= 65:
            return 'C'
        elif score >= 55:
            return 'D'
        else:
            return 'F'
    
    def _analyze_strengths_weaknesses(
        self, 
        scores: Dict[str, float]
    ) -> tuple:
        """تحلیل نقاط قوت و ضعف"""
        strengths = []
        weaknesses = []
        
        # نام‌های فارسی معیارها
        criterion_names = {
            'writing': 'نگارش',
            'structure': 'ساختار',
            'content': 'محتوا',
            'references': 'منابع',
            'originality': 'اصالت'
        }
        
        for criterion, score in scores.items():
            name = criterion_names.get(criterion, criterion)
            
            if score >= 85:
                strengths.append(f"{name} در سطح عالی است (نمره: {score:.1f})")
            elif score >= 70:
                strengths.append(f"{name} در سطح خوب است (نمره: {score:.1f})")
            
            if score < 60:
                weaknesses.append(
                    f"{name} نیاز به بهبود جدی دارد (نمره: {score:.1f})"
                )
            elif score < 70:
                weaknesses.append(
                    f"{name} می‌تواند بهبود یابد (نمره: {score:.1f})"
                )
        
        if not strengths:
            strengths.append("تمام جنبه‌ها نیاز به بهبود دارند")
        
        if not weaknesses:
            weaknesses.append("نقطه ضعف خاصی شناسایی نشد")
        
        return strengths, weaknesses
    
    def _calculate_statistics(self, scores: Dict[str, float]) -> Dict:
        """محاسبه آمار نمرات"""
        score_values = list(scores.values())
        
        return {
            'min_score': round(min(score_values), 2),
            'max_score': round(max(score_values), 2),
            'average_score': round(sum(score_values) / len(score_values), 2),
            'score_range': round(max(score_values) - min(score_values), 2),
            'standard_deviation': round(self._calculate_std(score_values), 2),
            'consistency': self._assess_consistency(score_values)
        }
    
    def _calculate_std(self, values: list) -> float:
        """محاسبه انحراف معیار"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _assess_consistency(self, values: list) -> str:
        """ارزیابی یکنواختی نمرات"""
        score_range = max(values) - min(values)
        
        if score_range <= 10:
            return 'بسیار یکنواخت'
        elif score_range <= 20:
            return 'یکنواخت'
        elif score_range <= 30:
            return 'متوسط'
        elif score_range <= 40:
            return 'متغیر'
        else:
            return 'بسیار متغیر'
    
    def _find_dominant_criterion(self, scores: Dict[str, float]) -> str:
        """یافتن معیار برتر (بهترین نمره)"""
        dominant = max(scores.items(), key=lambda x: x[1])
        
        criterion_names = {
            'writing': 'نگارش',
            'structure': 'ساختار',
            'content': 'محتوا',
            'references': 'منابع',
            'originality': 'اصالت'
        }
        
        return f"{criterion_names.get(dominant[0], dominant[0])} ({dominant[1]:.1f})"
    
    def _find_weakest_criterion(self, scores: Dict[str, float]) -> str:
        """یافتن معیار ضعیف‌تر (ضعیف‌ترین نمره)"""
        weakest = min(scores.items(), key=lambda x: x[1])
        
        criterion_names = {
            'writing': 'نگارش',
            'structure': 'ساختار',
            'content': 'محتوا',
            'references': 'منابع',
            'originality': 'اصالت'
        }
        
        return f"{criterion_names.get(weakest[0], weakest[0])} ({weakest[1]:.1f})"
    
    def _generate_recommendations(
        self, 
        scores: Dict[str, float],
        final_score: float
    ) -> List[str]:
        """تولید توصیه‌های بهبود"""
        recommendations = []
        
        # توصیه بر اساس نمره کلی
        if final_score >= 85:
            recommendations.append(
                "پروپوزال در سطح عالی است. آماده ارائه و دفاع است."
            )
        elif final_score >= 70:
            recommendations.append(
                "پروپوزال خوب است. با رفع نواقص جزئی، آماده ارائه خواهد بود."
            )
        elif final_score >= 60:
            recommendations.append(
                "پروپوزال قابل قبول است اما نیاز به بهبود دارد."
            )
        else:
            recommendations.append(
                "پروپوزال نیاز به بازنگری اساسی دارد."
            )
        
        # توصیه‌های خاص بر اساس هر معیار
        criterion_names = {
            'writing': 'نگارش',
            'structure': 'ساختار',
            'content': 'محتوا',
            'references': 'منابع',
            'originality': 'اصالت'
        }
        
        # شناسایی ضعیف‌ترین معیار
        weakest = min(scores.items(), key=lambda x: x[1])
        if weakest[1] < 70:
            recommendations.append(
                f"بر بهبود {criterion_names.get(weakest[0])} "
                f"تمرکز کنید (نمره فعلی: {weakest[1]:.1f})"
            )
        
        # توصیه برای هر معیار ضعیف
        for criterion, score in scores.items():
            name = criterion_names.get(criterion, criterion)
            
            if criterion == 'content' and score < 75:
                recommendations.append(
                    f"محتوای علمی را تقویت کنید: "
                    "روش‌شناسی دقیق‌تر، اهداف واضح‌تر، نوآوری بیشتر"
                )
            elif criterion == 'writing' and score < 75:
                recommendations.append(
                    "کیفیت نگارش را بهبود دهید: "
                    "املا، گرامر و خوانایی متن"
                )
            elif criterion == 'structure' and score < 75:
                recommendations.append(
                    "ساختار پروپوزال را تکمیل کنید: "
                    "بخش‌های ناقص را اضافه کنید"
                )
            elif criterion == 'references' and score < 75:
                recommendations.append(
                    "منابع بیشتر و به‌روزتر اضافه کنید"
                )
            elif criterion == 'originality' and score < 75:
                recommendations.append(
                    "اصالت محتوا را افزایش دهید: "
                    "از کپی‌برداری بپرهیزید، دیدگاه منحصربه‌فرد ارائه دهید"
                )
        
        # اگر نمره بالاست، تشویق کن
        if final_score >= 85 and not recommendations:
            recommendations.append(
                "عملکرد عالی! همه معیارها در سطح مطلوب هستند."
            )
        
        return recommendations

