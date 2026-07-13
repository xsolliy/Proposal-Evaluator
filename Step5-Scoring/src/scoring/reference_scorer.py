"""
ماژول محاسبه نمره منابع پروپوزال
این ماژول نمره منابع را بر اساس تعداد، کیفیت، تنوع و به‌روز بودن محاسبه می‌کند
وزن: 15% از نمره کل
"""

import re
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class ReferenceScorer:
    """
    محاسبه‌گر نمره منابع پروپوزال
    
    این کلاس نمره منابع را بر اساس موارد زیر محاسبه می‌کند:
    - تعداد منابع (کمیت)
    - به‌روز بودن منابع (سال انتشار)
    - تنوع منابع (فارسی/انگلیسی، کتاب/مقاله/...)
    - کیفیت فرمت‌نویسی
    """
    
    # وزن نمره منابع در نمره کل
    WEIGHT = 0.15  # 15%
    
    # معیارهای ارزیابی و وزن هر کدام
    CRITERIA_WEIGHTS = {
        'quantity': 0.30,      # تعداد: 30%
        'recency': 0.35,       # به‌روز بودن: 35%
        'diversity': 0.20,     # تنوع: 20%
        'quality': 0.15        # کیفیت فرمت: 15%
    }
    
    # آستانه‌های تعداد منابع
    QUANTITY_THRESHOLDS = {
        'excellent': 25,
        'good': 20,
        'acceptable': 15,
        'minimum': 10
    }
    
    # آستانه‌های به‌روز بودن (سال)
    RECENCY_THRESHOLDS = {
        'very_recent': 3,    # در 3 سال اخیر
        'recent': 5,         # در 5 سال اخیر
        'acceptable': 10     # در 10 سال اخیر
    }
    
    # الگوهای Regex برای شناسایی سال
    YEAR_PATTERNS = [
        r'\b(13\d{2})\b',           # سال شمسی (1300-1399)
        r'\b(14\d{2})\b',           # سال شمسی (1400-1499)
        r'\((\d{4})\)',             # سال میلادی در پرانتز
        r'\b(19\d{2})\b',           # سال میلادی (1900-1999)
        r'\b(20\d{2})\b'            # سال میلادی (2000-2099)
    ]
    
    # نشانه‌های منابع انگلیسی
    ENGLISH_INDICATORS = [
        re.compile(r'[A-Za-z]{3,}'),  # کلمات انگلیسی
        re.compile(r'\bet al\b', re.IGNORECASE),
        re.compile(r'\bpp\b', re.IGNORECASE),
        re.compile(r'\bVol\b', re.IGNORECASE),
        re.compile(r'\bdoi:\b', re.IGNORECASE)
    ]
    
    def __init__(self):
        """مقداردهی اولیه"""
        self.current_year = datetime.now().year
        logger.info("ReferenceScorer initialized")
    
    def score(
        self, 
        references: List[str], 
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        محاسبه نمره منابع پروپوزال
        
        Args:
            references: لیست منابع (هر منبع یک رشته)
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict شامل نمره و جزئیات ارزیابی
        """
        logger.info(f"Calculating reference score for {len(references)} references")
        
        # تحلیل منابع
        analysis = self._analyze_references(references)
        
        # محاسبه نمرات جزئی
        quantity_score = self._score_quantity(analysis['count'])
        recency_score = self._score_recency(analysis['years'])
        diversity_score = self._score_diversity(analysis)
        quality_score = self._score_quality(analysis)
        
        # محاسبه نمره نهایی (میانگین وزنی)
        final_score = (
            quantity_score * self.CRITERIA_WEIGHTS['quantity'] +
            recency_score * self.CRITERIA_WEIGHTS['recency'] +
            diversity_score * self.CRITERIA_WEIGHTS['diversity'] +
            quality_score * self.CRITERIA_WEIGHTS['quality']
        )
        
        # تعیین درجه
        grade = self._calculate_grade(final_score)
        
        # ساخت گزارش جامع
        result = {
            'score': round(final_score, 2),
            'grade': grade,
            'weight': self.WEIGHT,
            'weighted_score': round(final_score * self.WEIGHT, 2),
            'breakdown': {
                'quantity_score': round(quantity_score, 2),
                'recency_score': round(recency_score, 2),
                'diversity_score': round(diversity_score, 2),
                'quality_score': round(quality_score, 2)
            },
            'analysis': analysis,
            'statistics': self._calculate_statistics(analysis),
            'strengths': self._identify_strengths(analysis),
            'weaknesses': self._identify_weaknesses(analysis),
            'recommendations': self._generate_recommendations(analysis),
            'evaluated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Reference score calculated: {final_score:.2f}/100")
        return result
    
    def _analyze_references(self, references: List[str]) -> Dict:
        """تحلیل جامع منابع"""
        analysis = {
            'count': len(references),
            'years': [],
            'persian_count': 0,
            'english_count': 0,
            'recent_count': 0,
            'very_recent_count': 0,
            'formatted_count': 0,
            'with_year': 0,
            'average_length': 0
        }
        
        total_length = 0
        
        for ref in references:
            # طول منبع
            total_length += len(ref)
            
            # استخراج سال
            year = self._extract_year(ref)
            if year:
                analysis['years'].append(year)
                analysis['with_year'] += 1
                
                # بررسی به‌روز بودن
                years_old = self.current_year - year
                if years_old <= self.RECENCY_THRESHOLDS['very_recent']:
                    analysis['very_recent_count'] += 1
                if years_old <= self.RECENCY_THRESHOLDS['recent']:
                    analysis['recent_count'] += 1
            
            # تشخیص زبان
            if self._is_english(ref):
                analysis['english_count'] += 1
            else:
                analysis['persian_count'] += 1
            
            # بررسی کیفیت فرمت
            if self._is_well_formatted(ref):
                analysis['formatted_count'] += 1
        
        # محاسبه میانگین طول
        if references:
            analysis['average_length'] = total_length / len(references)
        
        return analysis
    
    def _extract_year(self, reference: str) -> Optional[int]:
        """استخراج سال از منبع"""
        for pattern in self.YEAR_PATTERNS:
            matches = re.findall(pattern, reference)
            if matches:
                year = int(matches[-1])  # آخرین سال پیدا شده
                
                # تبدیل سال شمسی به میلادی (تقریبی)
                if 1300 <= year <= 1500:
                    year = year + 621
                
                # بررسی معقول بودن سال
                if 1950 <= year <= self.current_year + 1:
                    return year
        
        return None
    
    def _is_english(self, reference: str) -> bool:
        """تشخیص منبع انگلیسی"""
        # شمارش کلمات انگلیسی
        english_words = 0
        for pattern in self.ENGLISH_INDICATORS:
            if pattern.search(reference):
                english_words += len(pattern.findall(reference))
        
        # اگر بیش از 3 کلمه انگلیسی دارد، احتمالاً انگلیسی است
        return english_words >= 3
    
    def _is_well_formatted(self, reference: str) -> bool:
        """بررسی کیفیت فرمت‌نویسی منبع"""
        # معیارهای فرمت خوب:
        # 1. داشتن نقطه و ویرگول
        # 2. داشتن سال
        # 3. طول مناسب (بیشتر از 30 کاراکتر)
        # 4. داشتن پرانتز برای سال
        
        has_punctuation = '.' in reference or '،' in reference
        has_year = self._extract_year(reference) is not None
        good_length = len(reference) >= 30
        has_parentheses = '(' in reference and ')' in reference
        
        # حداقل 3 معیار باید برقرار باشد
        return sum([has_punctuation, has_year, good_length, has_parentheses]) >= 3
    
    def _score_quantity(self, count: int) -> float:
        """محاسبه نمره تعداد منابع"""
        if count >= self.QUANTITY_THRESHOLDS['excellent']:
            return 100
        elif count >= self.QUANTITY_THRESHOLDS['good']:
            return 90
        elif count >= self.QUANTITY_THRESHOLDS['acceptable']:
            return 75
        elif count >= self.QUANTITY_THRESHOLDS['minimum']:
            return 60
        else:
            # نمره متناسب با تعداد
            return (count / self.QUANTITY_THRESHOLDS['minimum']) * 60
    
    def _score_recency(self, years: List[int]) -> float:
        """محاسبه نمره به‌روز بودن منابع"""
        if not years:
            return 50  # نمره متوسط اگر سالی شناسایی نشد
        
        # محاسبه درصد منابع جدید
        recent_ratio = 0
        very_recent_ratio = 0
        
        for year in years:
            years_old = self.current_year - year
            if years_old <= self.RECENCY_THRESHOLDS['very_recent']:
                very_recent_ratio += 1
            if years_old <= self.RECENCY_THRESHOLDS['recent']:
                recent_ratio += 1
        
        very_recent_ratio = very_recent_ratio / len(years)
        recent_ratio = recent_ratio / len(years)
        
        # محاسبه نمره بر اساس درصد منابع جدید
        score = (very_recent_ratio * 60 + recent_ratio * 40) * 100
        
        return min(100, score)
    
    def _score_diversity(self, analysis: Dict) -> float:
        """محاسبه نمره تنوع منابع"""
        persian = analysis['persian_count']
        english = analysis['english_count']
        total = analysis['count']
        
        if total == 0:
            return 0
        
        # تنوع زبانی (ترجیحاً ترکیبی از فارسی و انگلیسی)
        language_diversity = 0
        if persian > 0 and english > 0:
            # بهترین حالت: ترکیب متعادل
            ratio = min(persian, english) / max(persian, english)
            language_diversity = 50 + (ratio * 50)
        elif english > 0:
            # فقط انگلیسی
            language_diversity = 70
        else:
            # فقط فارسی
            language_diversity = 60
        
        return language_diversity
    
    def _score_quality(self, analysis: Dict) -> float:
        """محاسبه نمره کیفیت فرمت‌نویسی"""
        if analysis['count'] == 0:
            return 0
        
        # درصد منابع با فرمت مناسب
        formatted_ratio = analysis['formatted_count'] / analysis['count']
        
        # درصد منابع با سال مشخص
        with_year_ratio = analysis['with_year'] / analysis['count']
        
        # نمره کیفیت
        quality_score = (formatted_ratio * 60 + with_year_ratio * 40) * 100
        
        return quality_score
    
    def _calculate_grade(self, score: float) -> str:
        """تعیین درجه بر اساس نمره"""
        if score >= 90:
            return 'عالی'
        elif score >= 80:
            return 'خوب'
        elif score >= 70:
            return 'متوسط'
        elif score >= 60:
            return 'قابل قبول'
        else:
            return 'نیاز به بازنگری'
    
    def _calculate_statistics(self, analysis: Dict) -> Dict:
        """محاسبه آمار کلی منابع"""
        stats = {
            'total_count': analysis['count'],
            'persian_count': analysis['persian_count'],
            'english_count': analysis['english_count'],
            'recent_count': analysis['recent_count'],
            'very_recent_count': analysis['very_recent_count'],
            'average_length': round(analysis['average_length'], 1),
            'with_year': analysis['with_year'],
            'well_formatted': analysis['formatted_count']
        }
        
        if analysis['years']:
            stats['oldest_year'] = min(analysis['years'])
            stats['newest_year'] = max(analysis['years'])
            stats['average_year'] = round(sum(analysis['years']) / len(analysis['years']))
        
        return stats
    
    def _identify_strengths(self, analysis: Dict) -> List[str]:
        """شناسایی نقاط قوت منابع"""
        strengths = []
        
        if analysis['count'] >= self.QUANTITY_THRESHOLDS['excellent']:
            strengths.append("تعداد منابع بسیار خوب است")
        
        if analysis['count'] > 0:
            recent_ratio = analysis['recent_count'] / analysis['count']
            if recent_ratio >= 0.6:
                strengths.append("بیشتر منابع به‌روز هستند")
        
        if analysis['persian_count'] > 0 and analysis['english_count'] > 0:
            strengths.append("تنوع زبانی منابع مناسب است")
        
        if analysis['count'] > 0:
            formatted_ratio = analysis['formatted_count'] / analysis['count']
            if formatted_ratio >= 0.8:
                strengths.append("کیفیت فرمت‌نویسی عالی است")
        
        return strengths
    
    def _identify_weaknesses(self, analysis: Dict) -> List[str]:
        """شناسایی نقاط ضعف منابع"""
        weaknesses = []
        
        if analysis['count'] < self.QUANTITY_THRESHOLDS['minimum']:
            weaknesses.append("تعداد منابع کم است")
        
        if analysis['count'] > 0:
            recent_ratio = analysis['recent_count'] / analysis['count']
            if recent_ratio < 0.4:
                weaknesses.append("منابع به‌روز کم هستند")
        
        if analysis['english_count'] == 0:
            weaknesses.append("منابع انگلیسی وجود ندارد")
        
        if analysis['count'] > 0:
            formatted_ratio = analysis['formatted_count'] / analysis['count']
            if formatted_ratio < 0.5:
                weaknesses.append("کیفیت فرمت‌نویسی ضعیف است")
        
        return weaknesses
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """تولید پیشنهادات برای بهبود منابع"""
        recommendations = []
        
        if analysis['count'] < self.QUANTITY_THRESHOLDS['good']:
            needed = self.QUANTITY_THRESHOLDS['good'] - analysis['count']
            recommendations.append(
                f"حداقل {needed} منبع دیگر اضافه کنید"
            )
        
        if analysis['count'] > 0:
            recent_ratio = analysis['recent_count'] / analysis['count']
            if recent_ratio < 0.6:
                recommendations.append(
                    "منابع جدیدتر (5 سال اخیر) اضافه کنید"
                )
        
        if analysis['english_count'] == 0:
            recommendations.append(
                "منابع معتبر انگلیسی به پروپوزال اضافه کنید"
            )
        
        if analysis['count'] > 0:
            formatted_ratio = analysis['formatted_count'] / analysis['count']
            if formatted_ratio < 0.7:
                recommendations.append(
                    "فرمت‌نویسی منابع را اصلاح و یکنواخت کنید"
                )
        
        if not recommendations:
            recommendations.append("کیفیت منابع مناسب است")
        
        return recommendations
    
    def get_weighted_score(self, score: float) -> float:
        """
        محاسبه نمره وزن‌دار برای نمره کل
        
        Args:
            score: نمره منابع (0-100)
        
        Returns:
            نمره وزن‌دار (0-15)
        """
        return round(score * self.WEIGHT, 2)

