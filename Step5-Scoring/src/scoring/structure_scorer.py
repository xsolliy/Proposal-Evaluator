"""
ماژول محاسبه نمره ساختاری پروپوزال
این ماژول نمره ساختار را بر اساس وجود بخش‌های الزامی و اختیاری محاسبه می‌کند
وزن: 20% از نمره کل
"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class StructureScorer:
    """
    محاسبه‌گر نمره ساختاری پروپوزال
    
    این کلاس نمره ساختار را بر اساس موارد زیر محاسبه می‌کند:
    - وجود بخش‌های الزامی (abstract, introduction, methodology, references)
    - وجود بخش‌های اختیاری (literature_review, objectives, discussion, etc.)
    - طول مناسب هر بخش
    - تناسب بخش‌ها با یکدیگر
    """
    
    # وزن نمره ساختار در نمره کل
    WEIGHT = 0.20  # 20%
    
    # بخش‌های الزامی و امتیاز هر کدام
    REQUIRED_SECTIONS = {
        'abstract': 25,        # چکیده: 25 امتیاز
        'introduction': 25,    # مقدمه: 25 امتیاز
        'methodology': 30,     # روش‌شناسی: 30 امتیاز
        'references': 20       # منابع: 20 امتیاز
    }
    
    # بخش‌های اختیاری (بونوس)
    OPTIONAL_SECTIONS = {
        'literature_review': 5,   # پیشینه پژوهش
        'objectives': 5,          # اهداف
        'questions': 3,           # سوالات پژوهشی
        'hypotheses': 3,          # فرضیه‌ها
        'findings': 4,            # یافته‌ها
        'discussion': 5,          # بحث و نتیجه‌گیری
        'appendix': 2             # پیوست
    }
    
    # حداقل طول مناسب برای هر بخش (تعداد کلمات)
    MIN_SECTION_LENGTHS = {
        'abstract': 150,
        'introduction': 300,
        'methodology': 400,
        'literature_review': 500,
        'references': 10  # حداقل 10 منبع
    }
    
    def __init__(self):
        """مقداردهی اولیه"""
        logger.info("StructureScorer initialized")
    
    def score(self, sections: Dict[str, str], metadata: Optional[Dict] = None) -> Dict:
        """
        محاسبه نمره ساختاری پروپوزال
        
        Args:
            sections: دیکشنری بخش‌های پروپوزال {'abstract': 'متن...', 'introduction': 'متن...', ...}
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict شامل نمره و جزئیات ارزیابی
        """
        logger.info("Calculating structure score")
        
        # محاسبه نمره بخش‌های الزامی
        required_score, required_details = self._score_required_sections(sections)
        
        # محاسبه نمره بخش‌های اختیاری (بونوس)
        optional_score, optional_details = self._score_optional_sections(sections)
        
        # محاسبه جریمه برای طول نامناسب بخش‌ها
        length_penalty, length_details = self._calculate_length_penalty(sections)
        
        # محاسبه نمره نهایی (حداکثر 100، حداقل 0)
        final_score = min(100, max(0, required_score + optional_score - length_penalty))
        
        # تعیین درجه
        grade = self._calculate_grade(final_score)
        
        # ساخت گزارش جامع
        result = {
            'score': round(final_score, 2),
            'grade': grade,
            'weight': self.WEIGHT,
            'weighted_score': round(final_score * self.WEIGHT, 2),
            'breakdown': {
                'required_sections_score': round(required_score, 2),
                'optional_sections_score': round(optional_score, 2),
                'length_penalty': round(length_penalty, 2)
            },
            'details': {
                'required_sections': required_details,
                'optional_sections': optional_details,
                'length_analysis': length_details
            },
            'missing_required': self._get_missing_required(sections),
            'present_optional': self._get_present_optional(sections),
            'recommendations': self._generate_recommendations(
                sections, required_details, optional_details, length_details
            ),
            'evaluated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Structure score calculated: {final_score:.2f}/100")
        return result
    
    def _score_required_sections(self, sections: Dict[str, str]) -> tuple:
        """محاسبه نمره بخش‌های الزامی"""
        total_score = 0
        details = {}
        
        for section, max_points in self.REQUIRED_SECTIONS.items():
            if section in sections and sections[section]:
                # بخش موجود است
                total_score += max_points
                details[section] = {
                    'present': True,
                    'score': max_points,
                    'max_score': max_points,
                    'word_count': len(sections[section].split())
                }
            else:
                # بخش موجود نیست
                details[section] = {
                    'present': False,
                    'score': 0,
                    'max_score': max_points,
                    'word_count': 0
                }
        
        return total_score, details
    
    def _score_optional_sections(self, sections: Dict[str, str]) -> tuple:
        """محاسبه نمره بخش‌های اختیاری (بونوس)"""
        total_score = 0
        details = {}
        
        for section, bonus_points in self.OPTIONAL_SECTIONS.items():
            if section in sections and sections[section]:
                # بخش اختیاری موجود است
                total_score += bonus_points
                details[section] = {
                    'present': True,
                    'bonus': bonus_points,
                    'word_count': len(sections[section].split())
                }
            else:
                details[section] = {
                    'present': False,
                    'bonus': 0,
                    'word_count': 0
                }
        
        return total_score, details
    
    def _calculate_length_penalty(self, sections: Dict[str, str]) -> tuple:
        """محاسبه جریمه برای طول نامناسب بخش‌ها"""
        penalty = 0
        details = {}
        
        for section, min_length in self.MIN_SECTION_LENGTHS.items():
            if section in sections and sections[section]:
                word_count = len(sections[section].split())
                
                if word_count < min_length:
                    # جریمه برای کوتاه بودن بخش
                    section_penalty = (min_length - word_count) / min_length * 10
                    penalty += section_penalty
                    
                    details[section] = {
                        'word_count': word_count,
                        'min_required': min_length,
                        'penalty': round(section_penalty, 2),
                        'status': 'too_short'
                    }
                else:
                    details[section] = {
                        'word_count': word_count,
                        'min_required': min_length,
                        'penalty': 0,
                        'status': 'acceptable'
                    }
        
        return penalty, details
    
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
    
    def _get_missing_required(self, sections: Dict[str, str]) -> List[str]:
        """لیست بخش‌های الزامی ناقص"""
        missing = []
        for section in self.REQUIRED_SECTIONS.keys():
            if section not in sections or not sections[section]:
                missing.append(section)
        return missing
    
    def _get_present_optional(self, sections: Dict[str, str]) -> List[str]:
        """لیست بخش‌های اختیاری موجود"""
        present = []
        for section in self.OPTIONAL_SECTIONS.keys():
            if section in sections and sections[section]:
                present.append(section)
        return present
    
    def _generate_recommendations(
        self, 
        sections: Dict[str, str],
        required_details: Dict,
        optional_details: Dict,
        length_details: Dict
    ) -> List[str]:
        """تولید پیشنهادات برای بهبود ساختار"""
        recommendations = []
        
        # پیشنهاد برای بخش‌های الزامی ناقص
        missing = self._get_missing_required(sections)
        if missing:
            recommendations.append(
                f"بخش‌های الزامی زیر را اضافه کنید: {', '.join(missing)}"
            )
        
        # پیشنهاد برای بخش‌های کوتاه
        for section, details in length_details.items():
            if details.get('status') == 'too_short':
                recommendations.append(
                    f"بخش {section} را گسترش دهید "
                    f"(حداقل {details['min_required']} کلمه)"
                )
        
        # پیشنهاد برای بخش‌های اختیاری مهم
        important_optional = ['literature_review', 'objectives', 'discussion']
        for section in important_optional:
            if section not in sections or not sections[section]:
                recommendations.append(
                    f"افزودن بخش {section} می‌تواند کیفیت پروپوزال را بهبود دهد"
                )
        
        # اگر پروپوزال خوب است، تشویق کن
        if not recommendations:
            recommendations.append("ساختار پروپوزال کامل و مناسب است")
        
        return recommendations
    
    def get_weighted_score(self, score: float) -> float:
        """
        محاسبه نمره وزن‌دار برای نمره کل
        
        Args:
            score: نمره ساختار (0-100)
        
        Returns:
            نمره وزن‌دار (0-20)
        """
        return round(score * self.WEIGHT, 2)

