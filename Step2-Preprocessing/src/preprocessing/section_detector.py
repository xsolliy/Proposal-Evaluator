"""
ماژول شناسایی بخش‌های پروپوزال
===============================

این ماژول بخش‌های مختلف پروپوزال را شناسایی می‌کند.

Classes:
    SectionDetector: کلاس شناسایی بخش‌ها

Example:
    >>> detector = SectionDetector()
    >>> sections = detector.detect(normalized_text)
    >>> print(sections['abstract'])
"""

import re
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SectionDetector:
    """
    کلاس شناسایی بخش‌های پروپوزال
    
    این کلاس بخش‌های استاندارد یک پروپوزال علمی را شناسایی می‌کند:
    - چکیده (Abstract)
    - مقدمه (Introduction)
    - پیشینه پژوهش (Literature Review)
    - روش‌شناسی (Methodology)
    - یافته‌ها (Findings)
    - بحث و نتیجه‌گیری (Discussion)
    - منابع (References)
    
    Attributes:
        section_patterns (dict): الگوهای regex برای شناسایی بخش‌ها
        
    Example:
        >>> detector = SectionDetector()
        >>> result = detector.detect("چکیده: این پژوهش...")
        >>> print(result['sections']['abstract'])
    """
    
    # پیشوند اختیاری: شماره فصل/بخش، بولت، خط‌تیره و...
    # مثال: "1- مقدمه" ، "فصل اول: مقدمه" ، "۳-۱ روش تحقیق" ، "بخش دوم - پیشینه"
    _NUM_PREFIX = r'(?:(?:فصل|بخش)\s*(?:اول|دوم|سوم|چهارم|پنجم|ششم|هفتم|هشتم|نهم|دهم|\d+|[۰-۹]+)\s*[-:：.\s]*)?(?:[\d۰-۹]+[-.\s]*)*'

    # الگوهای عنوان بخش‌ها (فارسی و انگلیسی)
    SECTION_PATTERNS = {
        'abstract': [
            _NUM_PREFIX + r'چکیده\s*[:：\-]?\s*',
            _NUM_PREFIX + r'خلاصه\s*[:：\-]?\s*',
            r'Abstract\s*[:：\-]?\s*',
        ],
        'introduction': [
            _NUM_PREFIX + r'مقدمه\s*[:：\-]?\s*',
            _NUM_PREFIX + r'پیش\s*گفتار\s*[:：\-]?\s*',
            _NUM_PREFIX + r'کلیات\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            r'Introduction\s*[:：\-]?\s*',
            _NUM_PREFIX + r'درآمد\s*[:：\-]?\s*',
        ],
        'literature_review': [
            _NUM_PREFIX + r'پیشینه\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'مبانی\s*نظری\s*[:：\-]?\s*',
            _NUM_PREFIX + r'ادبیات\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'مرور\s*ادبیات\s*[:：\-]?\s*',
            r'Literature\s*Review\s*[:：\-]?\s*',
            r'Background\s*[:：\-]?\s*',
        ],
        'objectives': [
            _NUM_PREFIX + r'اهداف\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'هدف\s*(اصلی|کلی)?\s*[:：\-]?\s*',
            r'Objectives?\s*[:：\-]?\s*',
        ],
        'questions': [
            _NUM_PREFIX + r'سوالات?\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'پرسش\s*های?\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            r'Research\s*Questions?\s*[:：\-]?\s*',
        ],
        'hypotheses': [
            _NUM_PREFIX + r'فرضیه\s*های?\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'فرضیات\s*[:：\-]?\s*',
            r'Hypothes[ei]s\s*[:：\-]?\s*',
        ],
        'methodology': [
            _NUM_PREFIX + r'روش\s*(شناسی|تحقیق|پژوهش)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'متدولوژی\s*[:：\-]?\s*',
            _NUM_PREFIX + r'روش\s*اجرا(ی)?\s*(پژوهش|تحقیق)?\s*[:：\-]?\s*',
            r'Methodology\s*[:：\-]?\s*',
            r'Method\s*[:：\-]?\s*',
        ],
        'findings': [
            _NUM_PREFIX + r'یافته\s*ها\s*[:：\-]?\s*',
            _NUM_PREFIX + r'نتایج\s*[:：\-]?\s*',
            r'Findings?\s*[:：\-]?\s*',
            r'Results?\s*[:：\-]?\s*',
        ],
        'discussion': [
            _NUM_PREFIX + r'بحث\s*(و\s*نتیجه\s*گیری)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'نتیجه\s*گیری\s*[:：\-]?\s*',
            _NUM_PREFIX + r'جمع\s*بندی\s*[:：\-]?\s*',
            r'Discussion\s*[:：\-]?\s*',
            r'Conclusion\s*[:：\-]?\s*',
        ],
        'references': [
            _NUM_PREFIX + r'منابع\s*(و\s*مآخذ|و\s*ماخذ)?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'مراجع\s*[:：\-]?\s*',
            _NUM_PREFIX + r'فهرست\s*منابع\s*[:：\-]?\s*',
            r'References?\s*[:：\-]?\s*',
            r'Bibliography\s*[:：\-]?\s*',
        ],
        'appendix': [
            _NUM_PREFIX + r'پیوست\s*ها?\s*[:：\-]?\s*',
            _NUM_PREFIX + r'ضمیمه\s*ها?\s*[:：\-]?\s*',
            r'Appendix\s*[:：\-]?\s*',
            r'Appendices\s*[:：\-]?\s*',
        ]
    }
    
    # بخش‌های الزامی پروپوزال
    REQUIRED_SECTIONS = ['abstract', 'introduction', 'methodology', 'references']
    
    # بخش‌های اختیاری
    OPTIONAL_SECTIONS = ['literature_review', 'objectives', 'questions', 
                         'hypotheses', 'findings', 'discussion', 'appendix']
    
    def __init__(self):
        """مقداردهی اولیه SectionDetector"""
        self._compile_patterns()
    
    def _compile_patterns(self) -> None:
        """کامپایل الگوهای regex"""
        self.compiled_patterns = {}
        for section, patterns in self.SECTION_PATTERNS.items():
            combined = '|'.join(f'({p})' for p in patterns)
            self.compiled_patterns[section] = re.compile(
                combined, re.IGNORECASE | re.MULTILINE
            )
    
    def detect(self, text: str) -> Dict:
        """
        شناسایی بخش‌های پروپوزال
        
        Args:
            text: متن نرمال‌شده پروپوزال
            
        Returns:
            dict: شامل بخش‌های شناسایی شده و متادیتا
            {
                'sections': {
                    'abstract': str or None,
                    'introduction': str or None,
                    ...
                },
                'detected_sections': list,
                'missing_required': list,
                'section_order': list,
                'section_positions': dict,
                'completeness_score': float
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # پیدا کردن موقعیت‌های بخش‌ها
        section_positions = self._find_section_positions(text)
        
        # استخراج محتوای بخش‌ها
        sections = self._extract_sections(text, section_positions)
        
        # بررسی بخش‌های یافت شده
        detected = [s for s, content in sections.items() if content]
        missing_required = [s for s in self.REQUIRED_SECTIONS if s not in detected]
        
        # محاسبه درصد کامل بودن
        completeness = self._calculate_completeness(detected)
        
        # استخراج منابع
        references = self._extract_references(sections.get('references', ''))
        
        return {
            'sections': sections,
            'detected_sections': detected,
            'missing_required': missing_required,
            'section_order': list(section_positions.keys()),
            'section_positions': section_positions,
            'completeness_score': completeness,
            'references_list': references,
            'references_count': len(references)
        }
    
    def _find_section_positions(self, text: str) -> Dict[str, int]:
        """
        پیدا کردن موقعیت شروع هر بخش
        
        Args:
            text: متن پروپوزال
            
        Returns:
            dict: {section_name: start_position}
        """
        positions = {}
        
        for section, pattern in self.compiled_patterns.items():
            match = pattern.search(text)
            if match:
                positions[section] = match.start()
        
        # مرتب‌سازی بر اساس موقعیت
        sorted_positions = dict(sorted(positions.items(), key=lambda x: x[1]))
        
        return sorted_positions
    
    def _extract_sections(
        self, 
        text: str, 
        positions: Dict[str, int]
    ) -> Dict[str, Optional[str]]:
        """
        استخراج محتوای هر بخش
        
        Args:
            text: متن پروپوزال
            positions: موقعیت شروع بخش‌ها
            
        Returns:
            dict: {section_name: content}
        """
        sections = {section: None for section in self.SECTION_PATTERNS.keys()}
        
        if not positions:
            return sections
        
        position_list = list(positions.items())
        text_length = len(text)
        
        for i, (section, start_pos) in enumerate(position_list):
            # انتهای بخش = شروع بخش بعدی یا انتهای متن
            if i + 1 < len(position_list):
                end_pos = position_list[i + 1][1]
            else:
                end_pos = text_length
            
            # استخراج محتوا
            content = text[start_pos:end_pos]
            
            # حذف عنوان بخش از محتوا
            content = self.compiled_patterns[section].sub('', content, count=1)
            content = content.strip()
            
            if content:
                sections[section] = content
        
        return sections
    
    def _calculate_completeness(self, detected: List[str]) -> float:
        """
        محاسبه درصد کامل بودن پروپوزال
        
        Args:
            detected: لیست بخش‌های یافت شده
            
        Returns:
            float: درصد (0-100)
        """
        # وزن بخش‌های الزامی: 80%
        required_weight = 80
        # وزن بخش‌های اختیاری: 20%
        optional_weight = 20
        
        # محاسبه امتیاز بخش‌های الزامی
        required_found = sum(1 for s in self.REQUIRED_SECTIONS if s in detected)
        required_score = (required_found / len(self.REQUIRED_SECTIONS)) * required_weight
        
        # محاسبه امتیاز بخش‌های اختیاری
        optional_found = sum(1 for s in self.OPTIONAL_SECTIONS if s in detected)
        optional_score = (optional_found / len(self.OPTIONAL_SECTIONS)) * optional_weight
        
        return round(required_score + optional_score, 2)
    
    def _extract_references(self, references_text: str) -> List[str]:
        """
        استخراج لیست منابع
        
        Args:
            references_text: متن بخش منابع
            
        Returns:
            list: لیست منابع
        """
        if not references_text:
            return []
        
        references = []
        
        # الگوی شماره‌گذاری منابع
        patterns = [
            r'\[\d+\]\s*(.+?)(?=\[\d+\]|$)',  # [1] reference
            r'\d+\.\s*(.+?)(?=\d+\.|$)',       # 1. reference
            r'[-•]\s*(.+?)(?=[-•]|$)',         # - reference
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, references_text, re.DOTALL)
            if matches:
                references = [m.strip() for m in matches if m.strip()]
                break
        
        # اگر الگو پیدا نشد، تقسیم بر اساس خط جدید
        if not references:
            lines = references_text.split('\n')
            references = [line.strip() for line in lines 
                         if line.strip() and len(line.strip()) > 20]
        
        return references
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'sections': {section: None for section in self.SECTION_PATTERNS.keys()},
            'detected_sections': [],
            'missing_required': self.REQUIRED_SECTIONS.copy(),
            'section_order': [],
            'section_positions': {},
            'completeness_score': 0,
            'references_list': [],
            'references_count': 0
        }
    
    def get_section_summary(self, sections: Dict) -> Dict[str, int]:
        """
        خلاصه آماری از بخش‌ها
        
        Args:
            sections: دیکشنری بخش‌ها
            
        Returns:
            dict: {section_name: word_count}
        """
        summary = {}
        for section, content in sections.items():
            if content:
                word_count = len(content.split())
                summary[section] = word_count
        return summary


# تست ماژول
if __name__ == "__main__":
    detector = SectionDetector()
    
    # متن تست
    test_proposal = """
    چکیده:
    این پژوهش به بررسی کاربرد یادگیری ماشین در پردازش زبان فارسی می‌پردازد.
    هدف اصلی طراحی یک سیستم هوشمند برای تحلیل متون فارسی است.
    
    مقدمه:
    با گسترش روزافزون داده‌های متنی در فضای مجازی، نیاز به پردازش خودکار متن
    بیش از پیش احساس می‌شود. زبان فارسی به دلیل ویژگی‌های خاص خود نیازمند
    ابزارهای تخصصی است.
    
    پیشینه پژوهش:
    مطالعات متعددی در زمینه پردازش زبان فارسی انجام شده است. رضایی و همکاران (1399)
    یک سیستم تحلیل احساسات فارسی ارائه کردند.
    
    روش‌شناسی:
    در این پژوهش از روش تحقیق تجربی استفاده خواهد شد. جامعه آماری شامل
    10000 متن فارسی از شبکه‌های اجتماعی است.
    
    منابع:
    [1] رضایی، احمد. (1399). پردازش زبان فارسی. تهران: نشر علم.
    [2] محمدی، علی. (1400). یادگیری ماشین. اصفهان: دانشگاه اصفهان.
    [3] Smith, J. (2020). Natural Language Processing. MIT Press.
    """
    
    result = detector.detect(test_proposal)
    
    print("=" * 60)
    print("📋 بخش‌های شناسایی شده:")
    print("=" * 60)
    
    for section in result['detected_sections']:
        content = result['sections'][section]
        word_count = len(content.split()) if content else 0
        print(f"\n✅ {section}: ({word_count} کلمه)")
        if content:
            preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   {preview}")
    
    print("\n" + "=" * 60)
    print("📊 آمار:")
    print(f"   بخش‌های یافت شده: {len(result['detected_sections'])}")
    print(f"   بخش‌های الزامی گمشده: {result['missing_required']}")
    print(f"   درصد کامل بودن: {result['completeness_score']}%")
    print(f"   تعداد منابع: {result['references_count']}")











