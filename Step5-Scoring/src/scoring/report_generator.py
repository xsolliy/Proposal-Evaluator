"""
ماژول تولید گزارش جامع ارزیابی پروپوزال
این ماژول گزارش JSON کامل و ساختاریافته تولید می‌کند
"""

import json
from typing import Dict, Optional, Any
from datetime import datetime
import hashlib
from loguru import logger


class ReportGenerator:
    """
    تولیدکننده گزارش جامع ارزیابی
    
    این کلاس گزارش کامل JSON شامل تمام نتایج ارزیابی را تولید می‌کند
    """
    
    # نسخه فرمت گزارش
    REPORT_VERSION = "1.0.0"
    
    def __init__(self):
        """مقداردهی اولیه"""
        logger.info("ReportGenerator initialized")
    
    def generate(
        self,
        final_score_result: Dict,
        writing_result: Dict,
        structure_result: Dict,
        content_result: Dict,
        references_result: Dict,
        originality_result: Dict,
        preprocessing_result: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        تولید گزارش کامل ارزیابی
        
        Args:
            final_score_result: نتیجه محاسبه نمره نهایی
            writing_result: نتیجه ارزیابی نگارشی
            structure_result: نتیجه ارزیابی ساختار
            content_result: نتیجه ارزیابی محتوا
            references_result: نتیجه ارزیابی منابع
            originality_result: نتیجه ارزیابی اصالت
            preprocessing_result: نتیجه پیش‌پردازش (اختیاری)
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict گزارش کامل JSON
        """
        logger.info("Generating comprehensive evaluation report")
        
        # شناسه منحصربه‌فرد گزارش
        report_id = self._generate_report_id()
        
        # زمان ارزیابی
        evaluation_time = datetime.now()
        
        # ساخت گزارش کامل
        report = {
            # هدر گزارش
            'report_id': report_id,
            'version': self.REPORT_VERSION,
            'generated_at': evaluation_time.isoformat(),
            'status': 'success',
            
            # خلاصه نتایج
            'summary': self._generate_summary(final_score_result),
            
            # نمره نهایی و درجه
            'final_evaluation': {
                'final_score': final_score_result['final_score'],
                'grade': final_score_result['grade'],
                'level': final_score_result.get('level', 'N/A'),
                'pass': final_score_result.get('pass', False),
                'individual_scores': final_score_result['individual_scores'],
                'weighted_scores': final_score_result['weighted_scores'],
                'weights': final_score_result['weights']
            },
            
            # نتایج تفصیلی هر بخش
            'detailed_results': {
                'writing': self._extract_key_results(writing_result),
                'structure': self._extract_key_results(structure_result),
                'content': self._extract_key_results(content_result),
                'references': self._extract_key_results(references_result),
                'originality': self._extract_key_results(originality_result)
            },
            
            # تحلیل کلی
            'analysis': {
                'strengths': final_score_result['analysis']['strengths'],
                'weaknesses': final_score_result['analysis']['weaknesses'],
                'dominant_criterion': final_score_result['analysis']['dominant_criterion'],
                'weakest_criterion': final_score_result['analysis']['weakest_criterion'],
                'statistics': final_score_result['statistics']
            },
            
            # پیشنهادات و توصیه‌ها
            'recommendations': {
                'general': final_score_result['recommendations'],
                'specific': self._collect_specific_recommendations({
                    'writing': writing_result,
                    'structure': structure_result,
                    'content': content_result,
                    'references': references_result,
                    'originality': originality_result
                })
            },
            
            # هشدارها
            'warnings': self._collect_warnings({
                'originality': originality_result,
                'structure': structure_result,
                'content': content_result
            }),
            
            # متادیتای پروپوزال
            'proposal_metadata': self._extract_proposal_metadata(
                preprocessing_result, metadata
            ),
            
            # اطلاعات ارزیابی
            'evaluation_info': {
                'total_time': self._calculate_total_time({
                    'writing': writing_result,
                    'structure': structure_result,
                    'content': content_result,
                    'references': references_result,
                    'originality': originality_result
                }),
                'criteria_count': 5,
                'passed_criteria': self._count_passed_criteria(
                    final_score_result['individual_scores']
                ),
                'evaluator': 'AI System v1.0'
            }
        }
        
        logger.info(f"Report generated successfully: {report_id}")
        return report
    
    def generate_compact(
        self,
        final_score_result: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        تولید گزارش خلاصه (فقط نتایج کلیدی)
        
        Args:
            final_score_result: نتیجه محاسبه نمره نهایی
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict گزارش خلاصه
        """
        logger.info("Generating compact report")
        
        return {
            'final_score': final_score_result['final_score'],
            'grade': final_score_result['grade'],
            'pass': final_score_result.get('pass', False),
            'individual_scores': final_score_result['individual_scores'],
            'top_strength': final_score_result['analysis']['strengths'][0] \
                if final_score_result['analysis']['strengths'] else 'N/A',
            'top_weakness': final_score_result['analysis']['weaknesses'][0] \
                if final_score_result['analysis']['weaknesses'] else 'N/A',
            'generated_at': datetime.now().isoformat()
        }
    
    def save_to_file(
        self,
        report: Dict,
        file_path: str,
        pretty: bool = True
    ) -> None:
        """
        ذخیره گزارش در فایل JSON
        
        Args:
            report: گزارش به فرمت Dict
            file_path: مسیر فایل خروجی
            pretty: فرمت زیبای JSON (پیش‌فرض: True)
        """
        logger.info(f"Saving report to file: {file_path}")
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(report, f, ensure_ascii=False)
            
            logger.info(f"Report saved successfully to {file_path}")
        
        except Exception as e:
            logger.error(f"Error saving report to file: {e}")
            raise
    
    def _generate_report_id(self) -> str:
        """تولید شناسه منحصربه‌فرد گزارش"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{timestamp}-{id(self)}"
        hash_object = hashlib.md5(unique_string.encode())
        return f"EVAL-{hash_object.hexdigest()[:12].upper()}"
    
    def _generate_summary(self, final_score_result: Dict) -> str:
        """تولید خلاصه متنی نتایج"""
        score = final_score_result['final_score']
        grade = final_score_result['grade']
        pass_status = final_score_result.get('pass', False)
        
        if score >= 90:
            summary = (
                f"پروپوزال با نمره {score:.2f} ({grade}) در سطح عالی "
                "قرار دارد. تمام معیارها در سطح مطلوب هستند و "
                "پروپوزال آماده ارائه و دفاع است."
            )
        elif score >= 80:
            summary = (
                f"پروپوزال با نمره {score:.2f} ({grade}) کیفیت خوبی دارد. "
                "با رفع نواقص جزئی، آماده ارائه خواهد بود."
            )
        elif score >= 70:
            summary = (
                f"پروپوزال با نمره {score:.2f} ({grade}) در سطح متوسط "
                "قرار دارد. نیاز به بهبود در برخی بخش‌ها دارد."
            )
        elif score >= 60:
            summary = (
                f"پروپوزال با نمره {score:.2f} ({grade}) در حد قابل قبول "
                "است اما نیاز به بازنگری و بهبود جدی دارد."
            )
        else:
            summary = (
                f"پروپوزال با نمره {score:.2f} ({grade}) در سطح ضعیف "
                "قرار دارد و نیاز به بازنویسی اساسی دارد."
            )
        
        return summary
    
    def _extract_key_results(self, result: Dict) -> Dict:
        """استخراج نتایج کلیدی از هر بخش"""
        return {
            'score': result.get('score', 0),
            'grade': result.get('grade', 'N/A'),
            'weight': result.get('weight', 0),
            'weighted_score': result.get('weighted_score', 0),
            'key_findings': result.get('recommendations', [])[:3]  # 3 مورد اول
        }
    
    def _collect_specific_recommendations(self, results: Dict) -> Dict:
        """جمع‌آوری توصیه‌های خاص هر بخش"""
        recommendations = {}
        
        for criterion, result in results.items():
            if 'recommendations' in result and result['recommendations']:
                recommendations[criterion] = result['recommendations'][:3]  # 3 مورد اول
        
        return recommendations
    
    def _collect_warnings(self, results: Dict) -> list:
        """جمع‌آوری هشدارها از بخش‌های مختلف"""
        warnings = []
        
        # هشدار اصالت
        if 'originality' in results:
            warning = results['originality'].get('warning')
            if warning:
                warnings.append({
                    'type': 'plagiarism',
                    'severity': 'high' if '⛔' in warning else 'medium',
                    'message': warning
                })
        
        # هشدار ساختار
        if 'structure' in results:
            missing = results['structure'].get('missing_required', [])
            if missing:
                warnings.append({
                    'type': 'structure',
                    'severity': 'medium',
                    'message': f"بخش‌های الزامی ناقص: {', '.join(missing)}"
                })
        
        # هشدار محتوا
        if 'content' in results:
            score = results['content'].get('score', 100)
            if score < 50:
                warnings.append({
                    'type': 'content',
                    'severity': 'high',
                    'message': 'کیفیت محتوای علمی بسیار ضعیف است'
                })
        
        return warnings
    
    def _extract_proposal_metadata(
        self,
        preprocessing_result: Optional[Dict],
        metadata: Optional[Dict]
    ) -> Dict:
        """استخراج متادیتای پروپوزال"""
        proposal_metadata = {}
        
        if preprocessing_result and 'final_output' in preprocessing_result:
            output = preprocessing_result['final_output']
            
            if 'metadata' in output:
                proposal_metadata = {
                    'file_name': output['metadata'].get('file_name', 'N/A'),
                    'file_type': output['metadata'].get('file_type', 'N/A'),
                    'file_size_mb': output['metadata'].get('file_size_mb', 0),
                    'page_count': output['metadata'].get('page_count', 0),
                    'word_count': output['metadata'].get('word_count', 0),
                    'sentence_count': output['metadata'].get('sentence_count', 0),
                    'char_count': output['metadata'].get('char_count', 0)
                }
            
            if 'statistics' in output:
                proposal_metadata['statistics'] = output['statistics']
        
        # اضافه کردن متادیتای اضافی
        if metadata:
            proposal_metadata.update(metadata)
        
        return proposal_metadata
    
    def _calculate_total_time(self, results: Dict) -> str:
        """محاسبه زمان کل ارزیابی (تقریبی)"""
        # در حال حاضر، بازگشت یک مقدار ثابت
        # در پیاده‌سازی واقعی، باید زمان‌ها جمع شوند
        return "estimated 2-5 minutes"
    
    def _count_passed_criteria(self, scores: Dict) -> int:
        """شمارش معیارهایی که نمره قبولی دارند (>=60)"""
        return sum(1 for score in scores.values() if score >= 60)

