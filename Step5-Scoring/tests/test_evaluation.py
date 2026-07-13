"""
تست‌های یکپارچگی برای سیستم امتیازدهی
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from scoring.structure_scorer import StructureScorer
from scoring.reference_scorer import ReferenceScorer
from scoring.originality_scorer import OriginalityScorer
from scoring.final_calculator import FinalScoreCalculator
from scoring.report_generator import ReportGenerator
from scoring.evaluation_pipeline import EvaluationPipeline


# نمونه داده‌های تست
SAMPLE_SECTIONS = {
    'abstract': 'این یک چکیده نمونه است. ' * 30,  # ~150 کلمه
    'introduction': 'این یک مقدمه نمونه است. ' * 60,  # ~300 کلمه
    'methodology': 'این یک روش‌شناسی نمونه است. ' * 80,  # ~400 کلمه
    'references': 'منابع اینجا قرار می‌گیرند.'
}

SAMPLE_REFERENCES = [
    'احمدی، علی (1402). هوش مصنوعی و کاربردهای آن. تهران: نشر علم.',
    'محمدی، مریم (1401). پردازش زبان طبیعی. مشهد: دانشگاه فردوسی.',
    'Smith, J. (2022). Deep Learning Fundamentals. MIT Press.',
    'Johnson, A., & Williams, B. (2021). Neural Networks. ACM, 15(3), pp. 123-145.',
    'رضایی، حسن (1400). یادگیری ماشین. تهران: انتشارات دانشگاهی.'
]

SAMPLE_PLAGIARISM_RESULT = {
    'originality_score': 85.0,
    'plagiarism_percentage': 15.0,
    'max_similarity': 15.0,
    'similar_documents': [
        {'id': 'DOC-001', 'similarity': 15.0}
    ],
    'checked_against': 100
}


class TestStructureScorer:
    """تست‌های StructureScorer"""
    
    def test_basic_scoring(self):
        """تست امتیازدهی اساسی"""
        scorer = StructureScorer()
        result = scorer.score(SAMPLE_SECTIONS)
        
        assert 'score' in result
        assert 0 <= result['score'] <= 100
        assert result['weight'] == 0.20
        assert 'grade' in result
    
    def test_missing_required_sections(self):
        """تست بخش‌های الزامی ناقص"""
        scorer = StructureScorer()
        incomplete_sections = {'abstract': 'test'}
        
        result = scorer.score(incomplete_sections)
        
        assert len(result['missing_required']) > 0
        assert result['score'] < 100
    
    def test_all_sections_present(self):
        """تست زمانی که تمام بخش‌ها موجود است"""
        scorer = StructureScorer()
        complete_sections = {
            **SAMPLE_SECTIONS,
            'literature_review': 'پیشینه پژوهش' * 100,
            'objectives': 'اهداف پژوهش' * 50
        }
        
        result = scorer.score(complete_sections)
        
        assert len(result['missing_required']) == 0
        assert result['score'] >= 90  # باید نمره بالایی داشته باشد


class TestReferenceScorer:
    """تست‌های ReferenceScorer"""
    
    def test_basic_scoring(self):
        """تست امتیازدهی اساسی"""
        scorer = ReferenceScorer()
        result = scorer.score(SAMPLE_REFERENCES)
        
        assert 'score' in result
        assert 0 <= result['score'] <= 100
        assert result['weight'] == 0.15
        assert 'analysis' in result
    
    def test_empty_references(self):
        """تست با منابع خالی"""
        scorer = ReferenceScorer()
        result = scorer.score([])
        
        assert result['score'] == 0
        assert result['analysis']['count'] == 0
    
    def test_language_diversity(self):
        """تست تنوع زبانی منابع"""
        scorer = ReferenceScorer()
        result = scorer.score(SAMPLE_REFERENCES)
        
        assert result['analysis']['persian_count'] > 0
        assert result['analysis']['english_count'] > 0


class TestOriginalityScorer:
    """تست‌های OriginalityScorer"""
    
    def test_basic_scoring(self):
        """تست امتیازدهی اساسی"""
        scorer = OriginalityScorer()
        result = scorer.score(SAMPLE_PLAGIARISM_RESULT)
        
        assert 'score' in result
        assert 0 <= result['score'] <= 100
        assert result['weight'] == 0.05
        assert 'is_original' in result
    
    def test_high_plagiarism(self):
        """تست با تقلب بالا"""
        scorer = OriginalityScorer()
        high_plagiarism = {
            **SAMPLE_PLAGIARISM_RESULT,
            'originality_score': 20.0,
            'max_similarity': 80.0
        }
        
        result = scorer.score(high_plagiarism)
        
        assert result['score'] < 50
        assert result['is_original'] == False
        assert result['warning'] is not None
    
    def test_original_work(self):
        """تست با کار اصیل"""
        scorer = OriginalityScorer()
        original = {
            **SAMPLE_PLAGIARISM_RESULT,
            'originality_score': 95.0,
            'max_similarity': 5.0
        }
        
        result = scorer.score(original)
        
        assert result['score'] >= 90
        assert result['is_original'] == True


class TestFinalScoreCalculator:
    """تست‌های FinalScoreCalculator"""
    
    def test_basic_calculation(self):
        """تست محاسبه اساسی"""
        calculator = FinalScoreCalculator()
        result = calculator.calculate(
            writing_score=85.0,
            structure_score=80.0,
            content_score=90.0,
            references_score=75.0,
            originality_score=95.0
        )
        
        assert 'final_score' in result
        assert 0 <= result['final_score'] <= 100
        assert 'grade' in result
        assert result['pass'] == True
    
    def test_weight_calculation(self):
        """تست محاسبه وزن‌ها"""
        calculator = FinalScoreCalculator()
        result = calculator.calculate(
            writing_score=80.0,
            structure_score=80.0,
            content_score=80.0,
            references_score=80.0,
            originality_score=80.0
        )
        
        # با نمرات یکسان، نمره نهایی باید 80 باشد
        assert abs(result['final_score'] - 80.0) < 0.1
    
    def test_failing_score(self):
        """تست نمره قبول نشده"""
        calculator = FinalScoreCalculator()
        result = calculator.calculate(
            writing_score=50.0,
            structure_score=45.0,
            content_score=55.0,
            references_score=40.0,
            originality_score=60.0
        )
        
        assert result['pass'] == False
        assert result['final_score'] < 60


class TestReportGenerator:
    """تست‌های ReportGenerator"""
    
    def test_generate_report(self):
        """تست تولید گزارش کامل"""
        generator = ReportGenerator()
        
        # نمونه نتایج
        final_score_result = {
            'final_score': 85.0,
            'grade': 'خوب',
            'level': 'B',
            'pass': True,
            'individual_scores': {
                'writing': 85.0,
                'structure': 80.0,
                'content': 90.0,
                'references': 75.0,
                'originality': 95.0
            },
            'weighted_scores': {
                'writing': 21.25,
                'structure': 16.0,
                'content': 31.5,
                'references': 11.25,
                'originality': 4.75
            },
            'weights': {
                'writing': 0.25,
                'structure': 0.20,
                'content': 0.35,
                'references': 0.15,
                'originality': 0.05
            },
            'analysis': {
                'strengths': ['محتوا عالی است'],
                'weaknesses': ['منابع نیاز به بهبود دارد'],
                'dominant_criterion': 'محتوا',
                'weakest_criterion': 'منابع'
            },
            'statistics': {
                'min_score': 75.0,
                'max_score': 95.0,
                'average_score': 85.0,
                'score_range': 20.0,
                'standard_deviation': 7.5,
                'consistency': 'یکنواخت'
            },
            'recommendations': ['ادامه دهید!']
        }
        
        writing_result = {'score': 85.0, 'grade': 'خوب', 'recommendations': []}
        structure_result = {'score': 80.0, 'grade': 'خوب', 'recommendations': []}
        content_result = {'score': 90.0, 'grade': 'عالی', 'recommendations': []}
        references_result = {'score': 75.0, 'grade': 'متوسط', 'recommendations': []}
        originality_result = {'score': 95.0, 'grade': 'عالی', 'warning': None, 'recommendations': []}
        
        report = generator.generate(
            final_score_result=final_score_result,
            writing_result=writing_result,
            structure_result=structure_result,
            content_result=content_result,
            references_result=references_result,
            originality_result=originality_result
        )
        
        # بررسی ساختار گزارش
        assert 'report_id' in report
        assert 'final_evaluation' in report
        assert 'detailed_results' in report
        assert 'summary' in report
        assert report['status'] == 'success'
    
    def test_generate_compact_report(self):
        """تست تولید گزارش خلاصه"""
        generator = ReportGenerator()
        
        final_score_result = {
            'final_score': 85.0,
            'grade': 'خوب',
            'pass': True,
            'individual_scores': {
                'writing': 85.0,
                'structure': 80.0,
                'content': 90.0,
                'references': 75.0,
                'originality': 95.0
            },
            'analysis': {
                'strengths': ['محتوا عالی است'],
                'weaknesses': ['منابع نیاز به بهبود دارد']
            }
        }
        
        compact = generator.generate_compact(final_score_result)
        
        assert 'final_score' in compact
        assert 'grade' in compact
        assert 'pass' in compact
        assert len(compact) < 10  # خلاصه باید کوتاه باشد


class TestEvaluationPipeline:
    """تست‌های یکپارچگی EvaluationPipeline"""
    
    def test_full_evaluation(self):
        """تست ارزیابی کامل"""
        pipeline = EvaluationPipeline()
        
        report = pipeline.evaluate(
            sections=SAMPLE_SECTIONS,
            references=SAMPLE_REFERENCES,
            plagiarism_result=SAMPLE_PLAGIARISM_RESULT,
            writing_score=85.0,
            content_score=90.0
        )
        
        # بررسی ساختار گزارش نهایی
        assert 'report_id' in report
        assert 'final_evaluation' in report
        assert 'detailed_results' in report
        assert report['status'] == 'success'
        
        # بررسی نمره نهایی
        final_score = report['final_evaluation']['final_score']
        assert 0 <= final_score <= 100
    
    def test_input_validation(self):
        """تست اعتبارسنجی ورودی"""
        pipeline = EvaluationPipeline()
        
        # ورودی معتبر
        is_valid, errors = pipeline.validate_input(
            sections=SAMPLE_SECTIONS,
            references=SAMPLE_REFERENCES,
            writing_score=85.0,
            content_score=90.0
        )
        
        assert is_valid == True
        assert len(errors) == 0
        
        # ورودی نامعتبر
        is_valid, errors = pipeline.validate_input(
            writing_score=150.0  # نمره نامعتبر
        )
        
        assert is_valid == False
        assert len(errors) > 0
    
    def test_get_weights(self):
        """تست دریافت وزن‌ها"""
        pipeline = EvaluationPipeline()
        weights = pipeline.get_scoring_weights()
        
        assert sum(weights.values()) == pytest.approx(1.0, 0.001)
        assert weights['writing'] == 0.25
        assert weights['content'] == 0.35
    
    def test_pipeline_info(self):
        """تست اطلاعات خط لوله"""
        pipeline = EvaluationPipeline()
        info = pipeline.get_pipeline_info()
        
        assert 'version' in info
        assert 'components' in info
        assert 'scoring_weights' in info
        assert info['evaluation_steps'] == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

