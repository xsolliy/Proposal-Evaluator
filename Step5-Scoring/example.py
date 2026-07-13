"""
اسکریپت نمونه استفاده از سیستم امتیازدهی
این اسکریپت نحوه استفاده از ماژول‌های مختلف را نمایش می‌دهد
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from scoring.structure_scorer import StructureScorer
from scoring.reference_scorer import ReferenceScorer
from scoring.originality_scorer import OriginalityScorer
from scoring.final_calculator import FinalScoreCalculator
from scoring.report_generator import ReportGenerator
from scoring.evaluation_pipeline import EvaluationPipeline


def example_basic_usage():
    """مثال استفاده اساسی از EvaluationPipeline"""
    print("=" * 80)
    print("مثال 1: استفاده اساسی از EvaluationPipeline")
    print("=" * 80)
    
    # ایجاد خط لوله ارزیابی
    pipeline = EvaluationPipeline()
    
    # داده‌های نمونه
    sections = {
        'abstract': 'در این پژوهش به بررسی کاربردهای یادگیری ماشین در پردازش زبان طبیعی فارسی پرداخته می‌شود. ' * 20,
        'introduction': 'یادگیری ماشین یکی از شاخه‌های مهم هوش مصنوعی است که در سال‌های اخیر پیشرفت‌های چشمگیری داشته است. ' * 40,
        'methodology': 'در این پژوهش از روش‌های یادگیری عمیق و شبکه‌های عصبی برای پردازش متن‌های فارسی استفاده می‌شود. ' * 50,
        'references': 'منابع در انتها آورده شده است.'
    }
    
    references = [
        'احمدی، علی (1402). یادگیری ماشین و کاربردهای آن. تهران: نشر علم، صص 120-145.',
        'محمدی، مریم (1401). پردازش زبان طبیعی فارسی. مشهد: دانشگاه فردوسی.',
        'رضایی، حسن و کریمی، فاطمه (1400). شبکه‌های عصبی عمیق. تهران: انتشارات دانشگاهی.',
        'Smith, J., & Johnson, A. (2022). Deep Learning for NLP. MIT Press.',
        'Williams, R. (2021). Machine Learning Fundamentals. ACM Transactions, 15(3), pp. 123-145.',
        'Brown, M., et al. (2023). Neural Networks in Practice. IEEE, Vol. 42, pp. 567-589.',
        'Davis, K. (2022). Advanced AI Techniques. Springer.',
        'Miller, L. (2021). Natural Language Processing. Cambridge University Press.',
        'Wilson, T. (2023). Deep Learning Applications. Oxford University Press.',
        'Taylor, S. (2022). AI and Machine Learning. Pearson.'
    ]
    
    plagiarism_result = {
        'originality_score': 88.5,
        'plagiarism_percentage': 11.5,
        'max_similarity': 11.5,
        'similar_documents': [
            {'id': 'PROP-2023-001', 'similarity': 11.5},
            {'id': 'PROP-2023-045', 'similarity': 8.2}
        ],
        'checked_against': 250
    }
    
    # ارزیابی کامل
    print("\nدر حال ارزیابی پروپوزال...")
    report = pipeline.evaluate(
        sections=sections,
        references=references,
        plagiarism_result=plagiarism_result,
        writing_score=87.5,
        content_score=91.0
    )
    
    # نمایش نتایج
    print("\n" + "=" * 80)
    print("نتایج ارزیابی:")
    print("=" * 80)
    
    final_eval = report['final_evaluation']
    print(f"\n📊 نمره نهایی: {final_eval['final_score']:.2f}/100")
    print(f"🏆 درجه: {final_eval['grade']}")
    print(f"📈 سطح: {final_eval['level']}")
    print(f"✅ وضعیت: {'قبول' if final_eval['pass'] else 'رد'}")
    
    print("\n" + "-" * 80)
    print("نمرات جزئی:")
    print("-" * 80)
    for criterion, score in final_eval['individual_scores'].items():
        criterion_names = {
            'writing': 'نگارش',
            'structure': 'ساختار',
            'content': 'محتوا',
            'references': 'منابع',
            'originality': 'اصالت'
        }
        name = criterion_names.get(criterion, criterion)
        weight = final_eval['weights'][criterion] * 100
        print(f"  {name:10s}: {score:5.1f}/100  (وزن: {weight:4.1f}%)")
    
    print("\n" + "-" * 80)
    print("نقاط قوت:")
    print("-" * 80)
    for i, strength in enumerate(report['analysis']['strengths'][:3], 1):
        print(f"  {i}. {strength}")
    
    print("\n" + "-" * 80)
    print("نقاط ضعف:")
    print("-" * 80)
    for i, weakness in enumerate(report['analysis']['weaknesses'][:3], 1):
        print(f"  {i}. {weakness}")
    
    print("\n" + "-" * 80)
    print("پیشنهادات:")
    print("-" * 80)
    for i, recommendation in enumerate(report['recommendations']['general'][:3], 1):
        print(f"  {i}. {recommendation}")
    
    # ذخیره گزارش
    generator = ReportGenerator()
    output_file = Path(__file__).parent / 'sample_report.json'
    generator.save_to_file(report, str(output_file))
    print(f"\n💾 گزارش کامل در فایل ذخیره شد: {output_file}")
    
    return report


def example_individual_scorers():
    """مثال استفاده از scorer های جداگانه"""
    print("\n\n" + "=" * 80)
    print("مثال 2: استفاده جداگانه از Scorers")
    print("=" * 80)
    
    # 1. StructureScorer
    print("\n--- 1. ارزیابی ساختار ---")
    structure_scorer = StructureScorer()
    
    sections = {
        'abstract': 'چکیده پروپوزال ' * 30,
        'introduction': 'مقدمه ' * 60,
        'methodology': 'روش‌شناسی ' * 80,
        'references': 'منابع'
    }
    
    structure_result = structure_scorer.score(sections)
    print(f"نمره ساختار: {structure_result['score']:.2f}/100")
    print(f"بخش‌های ناقص: {', '.join(structure_result['missing_required']) if structure_result['missing_required'] else 'ندارد'}")
    
    # 2. ReferenceScorer
    print("\n--- 2. ارزیابی منابع ---")
    reference_scorer = ReferenceScorer()
    
    references = [
        'احمدی، علی (1402). کتاب اول. تهران: نشر علم.',
        'محمدی، مریم (1401). کتاب دوم. مشهد: دانشگاه.',
        'Smith, J. (2022). Book Three. MIT Press.',
        'Johnson, A. (2021). Article Four. ACM, 15(3).',
        'Williams, R. (2023). Book Five. Springer.'
    ]
    
    references_result = reference_scorer.score(references)
    print(f"نمره منابع: {references_result['score']:.2f}/100")
    print(f"تعداد منابع: {references_result['analysis']['count']}")
    print(f"منابع فارسی: {references_result['analysis']['persian_count']}")
    print(f"منابع انگلیسی: {references_result['analysis']['english_count']}")
    
    # 3. OriginalityScorer
    print("\n--- 3. ارزیابی اصالت ---")
    originality_scorer = OriginalityScorer()
    
    plagiarism_result = {
        'originality_score': 92.0,
        'plagiarism_percentage': 8.0,
        'max_similarity': 8.0,
        'similar_documents': [],
        'checked_against': 150
    }
    
    originality_result = originality_scorer.score(plagiarism_result)
    print(f"نمره اصالت: {originality_result['score']:.2f}/100")
    print(f"درصد تشابه: {originality_result['plagiarism_percentage']:.1f}%")
    print(f"وضعیت: {'اصیل' if originality_result['is_original'] else 'مشکوک به تقلب'}")
    
    # 4. FinalScoreCalculator
    print("\n--- 4. محاسبه نمره نهایی ---")
    calculator = FinalScoreCalculator()
    
    final_result = calculator.calculate(
        writing_score=85.0,
        structure_score=structure_result['score'],
        content_score=88.0,
        references_score=references_result['score'],
        originality_score=originality_result['score']
    )
    
    print(f"نمره نهایی: {final_result['final_score']:.2f}/100")
    print(f"درجه: {final_result['grade']}")
    print(f"قبولی: {'بله' if final_result['pass'] else 'خیر'}")


def example_input_validation():
    """مثال اعتبارسنجی ورودی"""
    print("\n\n" + "=" * 80)
    print("مثال 3: اعتبارسنجی ورودی")
    print("=" * 80)
    
    pipeline = EvaluationPipeline()
    
    # ورودی معتبر
    print("\n--- ورودی معتبر ---")
    is_valid, errors = pipeline.validate_input(
        sections={'abstract': 'test'},
        references=['ref1', 'ref2'],
        writing_score=85.0,
        content_score=90.0
    )
    
    print(f"معتبر: {is_valid}")
    if errors:
        print(f"خطاها: {errors}")
    
    # ورودی نامعتبر
    print("\n--- ورودی نامعتبر ---")
    is_valid, errors = pipeline.validate_input(
        sections="not a dict",  # نوع نادرست
        writing_score=150.0,    # نمره نامعتبر
        content_score=-10.0     # نمره منفی
    )
    
    print(f"معتبر: {is_valid}")
    if errors:
        print("خطاها:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")


def example_compact_report():
    """مثال تولید گزارش خلاصه"""
    print("\n\n" + "=" * 80)
    print("مثال 4: گزارش خلاصه")
    print("=" * 80)
    
    # محاسبه نمره نهایی
    calculator = FinalScoreCalculator()
    final_result = calculator.calculate(
        writing_score=85.0,
        structure_score=82.0,
        content_score=90.0,
        references_score=78.0,
        originality_score=95.0
    )
    
    # تولید گزارش خلاصه
    generator = ReportGenerator()
    compact = generator.generate_compact(final_result)
    
    print("\nگزارش خلاصه:")
    print("-" * 80)
    import json
    print(json.dumps(compact, ensure_ascii=False, indent=2))


def main():
    """اجرای تمام مثال‌ها"""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "  🎯 نمونه‌های استفاده از سیستم امتیازدهی پروپوزال  ".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)
    
    try:
        # مثال 1: استفاده اساسی
        report = example_basic_usage()
        
        # مثال 2: Scorers جداگانه
        example_individual_scorers()
        
        # مثال 3: اعتبارسنجی
        example_input_validation()
        
        # مثال 4: گزارش خلاصه
        example_compact_report()
        
        print("\n\n" + "=" * 80)
        print("✅ تمام مثال‌ها با موفقیت اجرا شدند!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n\n❌ خطا در اجرا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

