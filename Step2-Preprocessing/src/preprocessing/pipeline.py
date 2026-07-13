"""
Pipeline کامل پیش‌پردازش پروپوزال
==================================

این ماژول تمام مراحل پیش‌پردازش را یکپارچه می‌کند.

Classes:
    PreprocessingPipeline: کلاس اصلی Pipeline

Example:
    >>> pipeline = PreprocessingPipeline()
    >>> result = pipeline.process("proposal.pdf")
    >>> print(result['final_output'])
"""

import os
import time
import json
from typing import Dict, Optional, Union
from pathlib import Path
import logging

from .text_extractor import TextExtractor
from .normalizer import TextNormalizer
from .section_detector import SectionDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """
    Pipeline کامل پیش‌پردازش پروپوزال
    
    این کلاس تمام مراحل پیش‌پردازش را به صورت یکپارچه انجام می‌دهد:
    1. استخراج متن از فایل
    2. نرمال‌سازی متن
    3. شناسایی بخش‌ها
    
    Attributes:
        extractor (TextExtractor): استخراج‌کننده متن
        normalizer (TextNormalizer): نرمال‌کننده
        detector (SectionDetector): شناساگر بخش‌ها
        
    Example:
        >>> pipeline = PreprocessingPipeline()
        >>> result = pipeline.process("my_proposal.pdf")
        >>> print(f"نمره کامل بودن: {result['sections']['completeness_score']}")
    """
    
    def __init__(self, use_hazm: bool = True):
        """
        مقداردهی اولیه Pipeline
        
        Args:
            use_hazm: آیا از Hazm استفاده شود
        """
        self.extractor = TextExtractor()
        self.normalizer = TextNormalizer(use_hazm=use_hazm)
        self.detector = SectionDetector()
        
        logger.info("Pipeline پیش‌پردازش آماده شد")
    
    def process(self, input_source: Union[str, Path]) -> Dict:
        """
        پردازش کامل پروپوزال
        
        Args:
            input_source: مسیر فایل یا متن خام
            
        Returns:
            dict: نتیجه کامل پردازش
            {
                'success': bool,
                'processing_time': float,
                'extraction': dict,
                'normalization': dict,
                'sections': dict,
                'final_output': dict,
                'error': str or None
            }
        """
        start_time = time.time()
        
        try:
            # تشخیص نوع ورودی
            if os.path.isfile(str(input_source)):
                logger.info(f"پردازش فایل: {input_source}")
                return self._process_file(str(input_source), start_time)
            else:
                logger.info("پردازش متن خام")
                return self._process_text(str(input_source), start_time)
                
        except Exception as e:
            logger.error(f"خطا در پردازش: {str(e)}")
            return {
                'success': False,
                'processing_time': time.time() - start_time,
                'extraction': None,
                'normalization': None,
                'sections': None,
                'final_output': None,
                'error': str(e)
            }
    
    def _process_file(self, file_path: str, start_time: float) -> Dict:
        """پردازش فایل"""
        
        # مرحله 1: استخراج متن
        logger.info("مرحله 1: استخراج متن...")
        extraction_result = self.extractor.extract(file_path)
        
        if not extraction_result['success']:
            raise Exception(f"خطا در استخراج: {extraction_result['error']}")
        
        # مرحله 2: نرمال‌سازی
        logger.info("مرحله 2: نرمال‌سازی...")
        normalization_result = self.normalizer.normalize(extraction_result['text'])
        
        # مرحله 3: شناسایی بخش‌ها
        logger.info("مرحله 3: شناسایی بخش‌ها...")
        sections_result = self.detector.detect(normalization_result['normalized_text'])
        
        # ساخت خروجی نهایی
        processing_time = time.time() - start_time
        
        final_output = self._build_final_output(
            extraction_result,
            normalization_result,
            sections_result
        )
        
        logger.info(f"✅ پردازش کامل شد ({processing_time:.2f} ثانیه)")
        
        return {
            'success': True,
            'processing_time': round(processing_time, 2),
            'extraction': extraction_result,
            'normalization': normalization_result,
            'sections': sections_result,
            'final_output': final_output,
            'error': None
        }
    
    def _process_text(self, text: str, start_time: float) -> Dict:
        """پردازش متن خام"""
        
        # مرحله 1: ساخت ساختار از متن
        logger.info("مرحله 1: ساخت ساختار از متن...")
        extraction_result = self.extractor.extract_from_text(text)
        
        # مرحله 2: نرمال‌سازی
        logger.info("مرحله 2: نرمال‌سازی...")
        normalization_result = self.normalizer.normalize(text)
        
        # مرحله 3: شناسایی بخش‌ها
        logger.info("مرحله 3: شناسایی بخش‌ها...")
        sections_result = self.detector.detect(normalization_result['normalized_text'])
        
        # ساخت خروجی نهایی
        processing_time = time.time() - start_time
        
        final_output = self._build_final_output(
            extraction_result,
            normalization_result,
            sections_result
        )
        
        logger.info(f"✅ پردازش کامل شد ({processing_time:.2f} ثانیه)")
        
        return {
            'success': True,
            'processing_time': round(processing_time, 2),
            'extraction': extraction_result,
            'normalization': normalization_result,
            'sections': sections_result,
            'final_output': final_output,
            'error': None
        }
    
    def _build_final_output(
        self,
        extraction: Dict,
        normalization: Dict,
        sections: Dict
    ) -> Dict:
        """
        ساخت خروجی نهایی استاندارد
        
        این ساختار خروجی برای ماژول‌های بعدی (NLP، LLM، ...) استفاده می‌شود.
        """
        return {
            'raw_text': extraction['text'],
            'normalized_text': normalization['normalized_text'],
            'sections': {
                name: content 
                for name, content in sections['sections'].items() 
                if content
            },
            'metadata': {
                'file_name': extraction['metadata'].get('file_name', 'unknown'),
                'file_type': extraction['metadata'].get('file_type', 'text'),
                'file_size_mb': extraction['metadata'].get('file_size_mb', 0),
                'page_count': extraction['metadata'].get('page_count', 0),
                'word_count': normalization['statistics']['word_count'],
                'sentence_count': normalization['statistics']['sentence_count'],
                'char_count': normalization['statistics']['normalized_char_count'],
            },
            'statistics': {
                'unique_words': normalization['statistics']['unique_words'],
                'avg_word_length': normalization['statistics']['avg_word_length'],
                'avg_sentence_length': normalization['statistics']['avg_sentence_length'],
                'lexical_diversity': normalization['statistics']['lexical_diversity'],
            },
            'structure': {
                'detected_sections': sections['detected_sections'],
                'missing_required': sections['missing_required'],
                'completeness_score': sections['completeness_score'],
                'references_count': sections['references_count'],
            },
            'references': sections['references_list']
        }
    
    def process_batch(self, file_paths: list) -> list:
        """
        پردازش دسته‌ای چند فایل
        
        Args:
            file_paths: لیست مسیر فایل‌ها
            
        Returns:
            list: لیست نتایج پردازش
        """
        results = []
        total = len(file_paths)
        
        for i, path in enumerate(file_paths, 1):
            logger.info(f"پردازش {i}/{total}: {path}")
            result = self.process(path)
            result['file_path'] = path
            results.append(result)
        
        successful = sum(1 for r in results if r['success'])
        logger.info(f"✅ پردازش دسته‌ای کامل شد: {successful}/{total} موفق")
        
        return results
    
    def save_result(self, result: Dict, output_path: str) -> None:
        """
        ذخیره نتیجه در فایل JSON
        
        Args:
            result: نتیجه پردازش
            output_path: مسیر فایل خروجی
        """
        # تبدیل به JSON-serializable
        output = {
            'success': result['success'],
            'processing_time': result['processing_time'],
            'error': result['error'],
            'final_output': result['final_output'] if result['success'] else None
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        logger.info(f"نتیجه ذخیره شد: {output_path}")


# تست ماژول
if __name__ == "__main__":
    # ایجاد pipeline
    pipeline = PreprocessingPipeline()
    
    # متن تست
    test_proposal = """
    چکیده:
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان فارسی می‌پردازد.
    هدف اصلی، طراحی یک سیستم هوشمند برای تحلیل متون فارسی است.
    نتایج نشان می‌دهد که روش پیشنهادی دقت بالایی دارد.
    
    مقدمه:
    با گسترش روزافزون داده‌های متنی در فضای مجازی، نیاز به پردازش خودکار متن
    بیش از پیش احساس می‌شود. زبان فارسی به دلیل ویژگی‌های خاص خود نیازمند
    ابزارهای تخصصی است. در این پژوهش سعی شده است تا با استفاده از روش‌های
    نوین یادگیری ماشین، سیستمی کارآمد برای پردازش متون فارسی ارائه شود.
    
    پیشینه پژوهش:
    مطالعات متعددی در زمینه پردازش زبان فارسی انجام شده است.
    رضایی و همکاران (1399) یک سیستم تحلیل احساسات فارسی ارائه کردند.
    محمدی (1400) روشی برای استخراج کلیدواژه از متون فارسی معرفی کرد.
    
    روش‌شناسی:
    در این پژوهش از روش تحقیق تجربی استفاده خواهد شد.
    جامعه آماری شامل 10000 متن فارسی از شبکه‌های اجتماعی است.
    ابزار گردآوری داده‌ها شامل web scraping و API است.
    برای تحلیل از الگوریتم‌های یادگیری عمیق استفاده می‌شود.
    
    منابع:
    [1] رضایی، احمد. (1399). پردازش زبان فارسی. تهران: نشر علم.
    [2] محمدی، علی. (1400). یادگیری ماشین. اصفهان: دانشگاه اصفهان.
    [3] Smith, J. (2020). Natural Language Processing. MIT Press.
    """
    
    # پردازش
    result = pipeline.process(test_proposal)
    
    # نمایش نتایج
    print("\n" + "=" * 70)
    print("📊 نتایج پردازش Pipeline")
    print("=" * 70)
    
    if result['success']:
        output = result['final_output']
        
        print(f"\n✅ پردازش موفق ({result['processing_time']} ثانیه)")
        
        print("\n📄 متادیتا:")
        for key, value in output['metadata'].items():
            print(f"   {key}: {value}")
        
        print("\n📊 آمار متنی:")
        for key, value in output['statistics'].items():
            print(f"   {key}: {value}")
        
        print("\n📋 ساختار:")
        print(f"   بخش‌های یافت شده: {output['structure']['detected_sections']}")
        print(f"   بخش‌های گمشده: {output['structure']['missing_required']}")
        print(f"   درصد کامل بودن: {output['structure']['completeness_score']}%")
        print(f"   تعداد منابع: {output['structure']['references_count']}")
        
        print("\n📚 منابع:")
        for ref in output['references']:
            print(f"   • {ref[:60]}...")
    else:
        print(f"\n❌ خطا: {result['error']}")











