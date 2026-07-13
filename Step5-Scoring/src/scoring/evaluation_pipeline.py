"""
ماژول یکپارچه‌سازی خط لوله ارزیابی کامل
این ماژول تمام ماژول‌های ارزیابی را یکپارچه می‌کند
"""

from typing import Dict, Optional
from datetime import datetime
import time
from loguru import logger

# تعریف سراسری List برای حل مشکل import
try:
    from typing import List
except ImportError:
    List = list

from .structure_scorer import StructureScorer
from .reference_scorer import ReferenceScorer
from .originality_scorer import OriginalityScorer
from .final_calculator import FinalScoreCalculator
from .report_generator import ReportGenerator


class EvaluationPipeline:
    """
    خط لوله یکپارچه ارزیابی پروپوزال
    
    این کلاس تمام مراحل ارزیابی را به صورت یکپارچه اجرا می‌کند:
    1. محاسبه نمره ساختار
    2. محاسبه نمره منابع
    3. محاسبه نمره اصالت
    4. تجمیع نمرات و محاسبه نمره نهایی
    5. تولید گزارش جامع
    """
    
    def __init__(self):
        """مقداردهی اولیه ماژول‌ها"""
        logger.info("Initializing EvaluationPipeline")
        
        self.structure_scorer = StructureScorer()
        self.reference_scorer = ReferenceScorer()
        self.originality_scorer = OriginalityScorer()
        self.final_calculator = FinalScoreCalculator()
        self.report_generator = ReportGenerator()
        
        logger.info("EvaluationPipeline initialized successfully")
    
    def evaluate(
        self,
        sections: Dict[str, str],
        references: list,
        plagiarism_result: Dict,
        writing_score: float,
        content_score: float,
        preprocessing_result: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        ارزیابی کامل پروپوزال
        
        Args:
            sections: بخش‌های پروپوزال {'abstract': 'متن...', ...}
            references: لیست منابع
            plagiarism_result: نتیجه تشخیص سرقت ادبی
            writing_score: نمره نگارشی (از ماژول NLP)
            content_score: نمره محتوا (از ماژول LLM)
            preprocessing_result: نتیجه پیش‌پردازش (اختیاری)
            metadata: متادیتای اضافی (اختیاری)
        
        Returns:
            Dict گزارش کامل ارزیابی
        """
        logger.info("Starting comprehensive evaluation")
        start_time = time.time()
        
        try:
            # مرحله 1: محاسبه نمره ساختار
            logger.info("Step 1/5: Calculating structure score")
            structure_result = self.structure_scorer.score(sections, metadata)
            structure_score = structure_result['score']
            
            # مرحله 2: محاسبه نمره منابع
            logger.info("Step 2/5: Calculating references score")
            references_result = self.reference_scorer.score(references, metadata)
            references_score = references_result['score']
            
            # مرحله 3: محاسبه نمره اصالت
            logger.info("Step 3/5: Calculating originality score")
            originality_result = self.originality_scorer.score(
                plagiarism_result, metadata
            )
            originality_score = originality_result['score']
            
            # مرحله 4: تجمیع نمرات و محاسبه نمره نهایی
            logger.info("Step 4/5: Calculating final score")
            final_score_result = self.final_calculator.calculate(
                writing_score=writing_score,
                structure_score=structure_score,
                content_score=content_score,
                references_score=references_score,
                originality_score=originality_score,
                metadata=metadata
            )
            
            # مرحله 5: تولید گزارش جامع
            logger.info("Step 5/5: Generating comprehensive report")
            
            # ساخت نتایج خام برای گزارش
            writing_result = {
                'score': writing_score,
                'grade': self._get_grade(writing_score),
                'weight': 0.25,
                'weighted_score': writing_score * 0.25,
                'recommendations': []
            }
            
            content_result = {
                'score': content_score,
                'grade': self._get_grade(content_score),
                'weight': 0.35,
                'weighted_score': content_score * 0.35,
                'recommendations': []
            }
            
            # تولید گزارش کامل
            report = self.report_generator.generate(
                final_score_result=final_score_result,
                writing_result=writing_result,
                structure_result=structure_result,
                content_result=content_result,
                references_result=references_result,
                originality_result=originality_result,
                preprocessing_result=preprocessing_result,
                metadata=metadata
            )
            
            # افزودن زمان ارزیابی
            elapsed_time = time.time() - start_time
            report['evaluation_info']['actual_time'] = f"{elapsed_time:.2f} seconds"
            
            logger.info(
                f"Evaluation completed successfully in {elapsed_time:.2f}s. "
                f"Final score: {final_score_result['final_score']:.2f}/100"
            )
            
            return report
        
        except Exception as e:
            logger.error(f"Error during evaluation: {e}")
            raise
    
    def evaluate_structure_only(
        self,
        sections: Dict[str, str],
        metadata: Optional[Dict] = None
    ) -> Dict:
        """ارزیابی فقط ساختار پروپوزال"""
        logger.info("Evaluating structure only")
        return self.structure_scorer.score(sections, metadata)
    
    def evaluate_references_only(
        self,
        references: list,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """ارزیابی فقط منابع پروپوزال"""
        logger.info("Evaluating references only")
        return self.reference_scorer.score(references, metadata)
    
    def evaluate_originality_only(
        self,
        plagiarism_result: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """ارزیابی فقط اصالت پروپوزال"""
        logger.info("Evaluating originality only")
        return self.originality_scorer.score(plagiarism_result, metadata)
    
    def calculate_final_score_only(
        self,
        writing_score: float,
        structure_score: float,
        content_score: float,
        references_score: float,
        originality_score: float
    ) -> Dict:
        """محاسبه فقط نمره نهایی"""
        logger.info("Calculating final score only")
        return self.final_calculator.calculate(
            writing_score=writing_score,
            structure_score=structure_score,
            content_score=content_score,
            references_score=references_score,
            originality_score=originality_score
        )
    
    def get_scoring_weights(self) -> Dict[str, float]:
        """دریافت وزن‌های امتیازدهی"""
        return self.final_calculator.WEIGHTS.copy()
    
    def validate_input(
        self,
        sections: Optional[Dict] = None,
        references: Optional[list] = None,
        plagiarism_result: Optional[Dict] = None,
        writing_score: Optional[float] = None,
        content_score: Optional[float] = None
    ) -> tuple:
        """
        اعتبارسنجی ورودی‌ها
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # بررسی sections
        if sections is not None:
            if not isinstance(sections, dict):
                errors.append("sections باید یک دیکشنری باشد")
            elif not sections:
                errors.append("sections نمی‌تواند خالی باشد")
        
        # بررسی references
        if references is not None:
            if not isinstance(references, list):
                errors.append("references باید یک لیست باشد")
        
        # بررسی plagiarism_result
        if plagiarism_result is not None:
            if not isinstance(plagiarism_result, dict):
                errors.append("plagiarism_result باید یک دیکشنری باشد")
            else:
                required_keys = ['originality_score', 'max_similarity']
                missing_keys = [k for k in required_keys if k not in plagiarism_result]
                if missing_keys:
                    errors.append(
                        f"plagiarism_result فاقد کلیدهای ضروری است: {missing_keys}"
                    )
        
        # بررسی writing_score
        if writing_score is not None:
            if not isinstance(writing_score, (int, float)):
                errors.append("writing_score باید عدد باشد")
            elif not 0 <= writing_score <= 100:
                errors.append("writing_score باید بین 0 تا 100 باشد")
        
        # بررسی content_score
        if content_score is not None:
            if not isinstance(content_score, (int, float)):
                errors.append("content_score باید عدد باشد")
            elif not 0 <= content_score <= 100:
                errors.append("content_score باید بین 0 تا 100 باشد")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def _get_grade(self, score: float) -> str:
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
    
    def get_pipeline_info(self) -> Dict:
        """دریافت اطلاعات خط لوله"""
        return {
            'version': '1.0.0',
            'components': {
                'structure_scorer': 'StructureScorer',
                'reference_scorer': 'ReferenceScorer',
                'originality_scorer': 'OriginalityScorer',
                'final_calculator': 'FinalScoreCalculator',
                'report_generator': 'ReportGenerator'
            },
            'scoring_weights': self.get_scoring_weights(),
            'evaluation_steps': 5
        }

