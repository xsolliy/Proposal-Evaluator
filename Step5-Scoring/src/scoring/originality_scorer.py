"""
ماژول محاسبه نمره اصالت پروپوزال
این ماژول نمره اصالت را بر اساس نتایج تشخیص سرقت ادبی محاسبه می‌کند
وزن: 5% از نمره کل
"""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger


class OriginalityScorer:
    """
    محاسبه‌گر نمره اصالت پروپوزال
    
    این کلاس نمره اصالت را بر اساس موارد زیر محاسبه می‌کند:
    - درصد تشابه با پروپوزال‌های قبلی
    - تعداد اسناد مشابه
    - الگوی توزیع تشابه
    """
    
    # وزن نمره اصالت در نمره کل
    WEIGHT = 0.05  # 5%
    
    # آستانه‌های تشخیص تقلب
    THRESHOLDS = {
        'very_high': 90,    # احتمال بسیار بالای تقلب
        'high': 70,         # احتمال بالای تقلب
        'moderate': 50,     # تشابه متوسط
        'low': 30,          # تشابه کم
        'minimal': 15       # تشابه بسیار کم
    }
    
    # وزن‌های محاسبه نمره
    SCORE_WEIGHTS = {
        'max_similarity': 0.70,      # بیشترین تشابه: 70%
        'average_similarity': 0.20,  # میانگین تشابه: 20%
        'similar_docs_count': 0.10   # تعداد اسناد مشابه: 10%
    }
    
    def __init__(self):
        """مقداردهی اولیه"""
        logger.info("OriginalityScorer initialized")
    
    def score(
        self, 
        plagiarism_result: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        محاسبه نمره اصالت پروپوزال
        
        Args:
            plagiarism_result: نتیجه تشخیص سرقت ادبی شامل:
                - originality_score: نمره اصالت (0-100)
                - plagiarism_percentage: درصد تشابه (0-100)
                - max_similarity: بیشترین تشابه (0-100)
                - similar_documents: لیست اسناد مشابه
                - checked_against: تعداد اسناد بررسی شده
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict شامل نمره و جزئیات ارزیابی
        """
        logger.info("Calculating originality score")
        
        # استخراج اطلاعات از نتیجه تشخیص تقلب
        originality = plagiarism_result.get('originality_score', 0)
        max_similarity = plagiarism_result.get('max_similarity', 0)
        plagiarism_pct = plagiarism_result.get('plagiarism_percentage', 0)
        similar_docs = plagiarism_result.get('similar_documents', [])
        checked_against = plagiarism_result.get('checked_against', 0)
        
        # محاسبه نمره نهایی اصالت
        final_score = self._calculate_final_score(
            originality, max_similarity, similar_docs
        )
        
        # تعیین سطح تشابه
        similarity_level = self._determine_similarity_level(max_similarity)
        
        # تعیین وضعیت اصالت
        is_original = self._is_original(max_similarity)
        
        # تعیین درجه
        grade = self._calculate_grade(final_score)
        
        # تولید هشدار در صورت نیاز
        warning = self._generate_warning(max_similarity, similar_docs)
        
        # ساخت گزارش جامع
        result = {
            'score': round(final_score, 2),
            'grade': grade,
            'weight': self.WEIGHT,
            'weighted_score': round(final_score * self.WEIGHT, 2),
            'originality_score': round(originality, 2),
            'plagiarism_percentage': round(plagiarism_pct, 2),
            'is_original': is_original,
            'similarity_level': similarity_level,
            'max_similarity': round(max_similarity, 2),
            'similar_documents_count': len(similar_docs),
            'checked_against': checked_against,
            'similar_documents': similar_docs[:5],  # فقط 5 سند برتر
            'warning': warning,
            'details': {
                'interpretation': self._interpret_result(max_similarity),
                'confidence': self._calculate_confidence(checked_against),
                'risk_assessment': self._assess_risk(max_similarity, similar_docs)
            },
            'recommendations': self._generate_recommendations(
                max_similarity, similar_docs
            ),
            'evaluated_at': datetime.now().isoformat()
        }
        
        logger.info(f"Originality score calculated: {final_score:.2f}/100")
        return result
    
    def _calculate_final_score(
        self,
        originality: float,
        max_similarity: float,
        similar_docs: List[Dict]
    ) -> float:
        """
        محاسبه نمره نهایی اصالت
        
        نمره اصالت = 100 - (وزن‌دار شده درصد تشابه)
        """
        # نمره اصلی بر اساس بیشترین تشابه
        base_score = max(0, 100 - max_similarity)
        
        # محاسبه میانگین تشابه با اسناد مشابه
        avg_similarity = 0
        if similar_docs:
            similarities = [doc.get('similarity', 0) for doc in similar_docs]
            avg_similarity = sum(similarities) / len(similarities)
        
        # محاسبه جریمه بر اساس تعداد اسناد مشابه
        similar_count_penalty = 0
        if len(similar_docs) > 5:
            # جریمه برای داشتن بیش از 5 سند مشابه
            similar_count_penalty = min(10, (len(similar_docs) - 5) * 1)
        
        # ترکیب وزنی نمرات
        final_score = (
            base_score * self.SCORE_WEIGHTS['max_similarity'] +
            (100 - avg_similarity) * self.SCORE_WEIGHTS['average_similarity'] +
            (100 - similar_count_penalty) * self.SCORE_WEIGHTS['similar_docs_count']
        )
        
        return min(100, max(0, final_score))
    
    def _determine_similarity_level(self, max_similarity: float) -> str:
        """تعیین سطح تشابه"""
        if max_similarity >= self.THRESHOLDS['very_high']:
            return 'بسیار بالا'
        elif max_similarity >= self.THRESHOLDS['high']:
            return 'بالا'
        elif max_similarity >= self.THRESHOLDS['moderate']:
            return 'متوسط'
        elif max_similarity >= self.THRESHOLDS['low']:
            return 'کم'
        elif max_similarity >= self.THRESHOLDS['minimal']:
            return 'بسیار کم'
        else:
            return 'ناچیز'
    
    def _is_original(self, max_similarity: float) -> bool:
        """تشخیص اصالت پروپوزال"""
        return max_similarity < self.THRESHOLDS['high']
    
    def _calculate_grade(self, score: float) -> str:
        """تعیین درجه بر اساس نمره"""
        if score >= 95:
            return 'عالی - کاملاً اصیل'
        elif score >= 85:
            return 'خوب - اصیل'
        elif score >= 70:
            return 'متوسط - قابل قبول'
        elif score >= 50:
            return 'ضعیف - نیاز به بررسی'
        else:
            return 'بسیار ضعیف - احتمال تقلب بالا'
    
    def _generate_warning(
        self,
        max_similarity: float,
        similar_docs: List[Dict]
    ) -> Optional[str]:
        """تولید پیام هشدار در صورت نیاز"""
        if max_similarity >= self.THRESHOLDS['very_high']:
            return (
                "⛔ هشدار شدید: احتمال بسیار بالای سرقت ادبی. "
                "این پروپوزال باید به صورت دستی بررسی شود."
            )
        elif max_similarity >= self.THRESHOLDS['high']:
            return (
                "⚠️ هشدار: تشابه بالا با سایر پروپوزال‌ها. "
                "لطفاً محتوای مشابه را بررسی کنید."
            )
        elif max_similarity >= self.THRESHOLDS['moderate']:
            return (
                "ℹ️ توجه: تشابه متوسط شناسایی شد. "
                "ممکن است به دلیل استفاده از منابع مشترک باشد."
            )
        
        return None
    
    def _interpret_result(self, max_similarity: float) -> str:
        """تفسیر نتیجه برای کاربر"""
        if max_similarity < self.THRESHOLDS['minimal']:
            return (
                "پروپوزال کاملاً اصیل است و تشابه بسیار کمی "
                "با پروپوزال‌های دیگر دارد."
            )
        elif max_similarity < self.THRESHOLDS['low']:
            return (
                "پروپوزال اصیل است. تشابه کم احتمالاً به دلیل "
                "استفاده از اصطلاحات رایج در حوزه است."
            )
        elif max_similarity < self.THRESHOLDS['moderate']:
            return (
                "پروپوزال دارای تشابه متوسطی است که می‌تواند "
                "به دلیل استفاده از منابع و مفاهیم مشترک باشد."
            )
        elif max_similarity < self.THRESHOLDS['high']:
            return (
                "تشابه قابل توجهی شناسایی شد. توصیه می‌شود "
                "بخش‌های مشابه بررسی و بازنویسی شوند."
            )
        elif max_similarity < self.THRESHOLDS['very_high']:
            return (
                "تشابه بالایی وجود دارد که نیازمند بررسی دقیق است. "
                "ممکن است نشان‌دهنده کپی‌برداری باشد."
            )
        else:
            return (
                "تشابه بسیار بالا شناسایی شد. این پروپوزال احتمالاً "
                "از پروپوزال دیگری کپی شده است."
            )
    
    def _calculate_confidence(self, checked_against: int) -> str:
        """محاسبه اعتماد به نتیجه بر اساس تعداد اسناد بررسی شده"""
        if checked_against >= 1000:
            return 'بسیار بالا'
        elif checked_against >= 500:
            return 'بالا'
        elif checked_against >= 100:
            return 'متوسط'
        elif checked_against >= 50:
            return 'کم'
        else:
            return 'بسیار کم'
    
    def _assess_risk(
        self,
        max_similarity: float,
        similar_docs: List[Dict]
    ) -> Dict:
        """ارزیابی ریسک تقلب"""
        risk_level = 'پایین'
        risk_score = 0
        
        if max_similarity >= self.THRESHOLDS['very_high']:
            risk_level = 'بسیار بالا'
            risk_score = 90
        elif max_similarity >= self.THRESHOLDS['high']:
            risk_level = 'بالا'
            risk_score = 70
        elif max_similarity >= self.THRESHOLDS['moderate']:
            risk_level = 'متوسط'
            risk_score = 50
        elif max_similarity >= self.THRESHOLDS['low']:
            risk_level = 'کم'
            risk_score = 30
        else:
            risk_level = 'بسیار کم'
            risk_score = 10
        
        # افزایش ریسک اگر تشابه با چندین سند وجود دارد
        if len(similar_docs) > 3:
            risk_score = min(100, risk_score + 10)
        
        return {
            'level': risk_level,
            'score': risk_score,
            'requires_review': max_similarity >= self.THRESHOLDS['moderate']
        }
    
    def _generate_recommendations(
        self,
        max_similarity: float,
        similar_docs: List[Dict]
    ) -> List[str]:
        """تولید پیشنهادات برای بهبود اصالت"""
        recommendations = []
        
        if max_similarity >= self.THRESHOLDS['high']:
            recommendations.append(
                "بخش‌های مشابه را شناسایی و به صورت کامل بازنویسی کنید"
            )
            recommendations.append(
                "از عبارات و جملات متفاوت برای بیان مفاهیم استفاده کنید"
            )
            recommendations.append(
                "اطمینان حاصل کنید که تمام نقل‌قول‌ها به درستی ذکر شده‌اند"
            )
        elif max_similarity >= self.THRESHOLDS['moderate']:
            recommendations.append(
                "بخش‌های با تشابه بالا را مشخص و بازنویسی کنید"
            )
            recommendations.append(
                "از پارافریز کردن به جای کپی مستقیم استفاده کنید"
            )
        elif max_similarity >= self.THRESHOLDS['low']:
            recommendations.append(
                "تشابه موجود در حد مجاز است، اما سعی کنید منحصربه‌فردتر بنویسید"
            )
        else:
            recommendations.append(
                "پروپوزال از نظر اصالت عالی است. ادامه دهید!"
            )
        
        if len(similar_docs) > 5:
            recommendations.append(
                f"تشابه با {len(similar_docs)} سند شناسایی شد. "
                "احتمالاً از منابع مشترک استفاده کرده‌اید. "
                "سعی کنید دیدگاه منحصربه‌فرد خود را بیشتر نمایان کنید."
            )
        
        return recommendations
    
    def get_weighted_score(self, score: float) -> float:
        """
        محاسبه نمره وزن‌دار برای نمره کل
        
        Args:
            score: نمره اصالت (0-100)
        
        Returns:
            نمره وزن‌دار (0-5)
        """
        return round(score * self.WEIGHT, 2)

