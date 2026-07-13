"""
مدیریت Promptها
===============

این ماژول promptهای تخصصی ارزیابی پروپوزال را مدیریت می‌کند.

Classes:
    PromptManager: مدیریت و ساخت promptها

Example:
    >>> manager = PromptManager()
    >>> prompt = manager.get_structure_prompt(sections)
    >>> print(prompt)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """قالب پرامپت"""
    name: str
    system_prompt: str
    user_prompt_template: str
    expected_format: str


class PromptManager:
    """
    کلاس مدیریت Promptها
    
    این کلاس promptهای تخصصی برای ارزیابی پروپوزال را مدیریت می‌کند.
    
    Prompts:
        - structure: ارزیابی ساختار (20%)
        - content: ارزیابی محتوا (35%)
        - references: ارزیابی منابع (15%)
        
    Example:
        >>> manager = PromptManager()
        >>> prompt = manager.build_structure_prompt(sections, metadata)
    """
    
    # پرامپت سیستم پایه
    BASE_SYSTEM_PROMPT = """تو یک ارزیاب متخصص پروپوزال‌های تحقیقاتی فارسی هستی.
وظیفه تو ارزیابی دقیق و منصفانه پروپوزال‌ها بر اساس معیارهای مشخص است.

قوانین مهم:
1. همیشه به فارسی پاسخ بده
2. نمره را دقیق و بین 0 تا 100 بده
3. بازخورد سازنده ارائه بده
4. نقاط قوت و ضعف را مشخص کن
5. پاسخ را در قالب JSON معتبر برگردان
"""
    
    def __init__(self):
        """مقداردهی اولیه PromptManager"""
        self.templates = self._init_templates()
    
    def _init_templates(self) -> Dict[str, PromptTemplate]:
        """مقداردهی قالب‌های پرامپت"""
        
        templates = {}
        
        # ========================================
        # پرامپت ارزیابی ساختار (20%)
        # ========================================
        templates['structure'] = PromptTemplate(
            name='structure',
            system_prompt=self.BASE_SYSTEM_PROMPT + """
برای ارزیابی ساختار، این معیارها را بررسی کن:
- وجود همه بخش‌های ضروری (چکیده، مقدمه، روش، منابع)
- ترتیب منطقی بخش‌ها
- تناسب حجم هر بخش
- انسجام کلی ساختار
""",
            user_prompt_template="""
لطفاً ساختار این پروپوزال را ارزیابی کن:

## بخش‌های شناسایی شده:
{sections_list}

## آمار:
- تعداد کلمات: {word_count}
- تعداد جملات: {sentence_count}
- تعداد بخش‌ها: {section_count}

## وزن این بخش: 20% از نمره کل

پاسخ را در این قالب JSON برگردان:
{{
    "score": <عدد 0-100>,
    "missing_sections": ["لیست بخش‌های ناقص"],
    "structure_issues": ["مشکلات ساختاری"],
    "strengths": ["نقاط قوت"],
    "weaknesses": ["نقاط ضعف"],
    "recommendations": ["پیشنهادات بهبود"],
    "summary": "خلاصه ارزیابی در یک پاراگراف"
}}
""",
            expected_format='json'
        )
        
        # ========================================
        # پرامپت ارزیابی محتوا (35%)
        # ========================================
        templates['content'] = PromptTemplate(
            name='content',
            system_prompt=self.BASE_SYSTEM_PROMPT + """
برای ارزیابی محتوا، این معیارها را بررسی کن:
- وضوح بیان مسئله و هدف
- کیفیت مرور ادبیات
- دقت روش‌شناسی
- قابلیت اجرا
- نوآوری
- ارتباط منطقی بخش‌ها
""",
            user_prompt_template="""
لطفاً محتوای این پروپوزال را ارزیابی کن:

## چکیده:
{abstract}

## مقدمه:
{introduction}

## روش‌شناسی:
{methodology}

## کلمات کلیدی:
{keywords}

## وزن این بخش: 35% از نمره کل

پاسخ را در این قالب JSON برگردان:
{{
    "score": <عدد 0-100>,
    "problem_clarity": <عدد 0-100>,
    "methodology_quality": <عدد 0-100>,
    "innovation_level": <عدد 0-100>,
    "feasibility": <عدد 0-100>,
    "strengths": ["نقاط قوت محتوایی"],
    "weaknesses": ["نقاط ضعف محتوایی"],
    "content_gaps": ["خلاءهای محتوایی"],
    "recommendations": ["پیشنهادات بهبود"],
    "summary": "خلاصه ارزیابی محتوا"
}}
""",
            expected_format='json'
        )
        
        # ========================================
        # پرامپت ارزیابی منابع (15%)
        # ========================================
        templates['references'] = PromptTemplate(
            name='references',
            system_prompt=self.BASE_SYSTEM_PROMPT + """
برای ارزیابی منابع، این معیارها را بررسی کن:
- تعداد کافی منابع (حداقل 10-15)
- کیفیت منابع (مقالات معتبر، کتب مرجع)
- به‌روز بودن منابع (ترجیحاً 5 سال اخیر)
- ارتباط منابع با موضوع
- استناددهی صحیح در متن
""",
            user_prompt_template="""
لطفاً منابع این پروپوزال را ارزیابی کن:

## لیست منابع:
{references_list}

## آمار منابع:
- تعداد کل: {reference_count}
- منابع فارسی: {persian_refs}
- منابع انگلیسی: {english_refs}

## وزن این بخش: 15% از نمره کل

پاسخ را در این قالب JSON برگردان:
{{
    "score": <عدد 0-100>,
    "quantity_score": <عدد 0-100>,
    "quality_score": <عدد 0-100>,
    "recency_score": <عدد 0-100>,
    "relevance_score": <عدد 0-100>,
    "issues": ["مشکلات منابع"],
    "strengths": ["نقاط قوت"],
    "recommendations": ["پیشنهادات بهبود"],
    "summary": "خلاصه ارزیابی منابع"
}}
""",
            expected_format='json'
        )
        
        # ========================================
        # پرامپت ارزیابی کلی
        # ========================================
        templates['overall'] = PromptTemplate(
            name='overall',
            system_prompt=self.BASE_SYSTEM_PROMPT + """
تو باید یک ارزیابی کلی و نهایی از پروپوزال ارائه دهی.
نمرات جزئی داده شده و تو باید جمع‌بندی کنی.
""",
            user_prompt_template="""
لطفاً ارزیابی نهایی این پروپوزال را انجام بده:

## نمرات جزئی:
- نگارش: {writing_score}/100 (وزن 25%)
- ساختار: {structure_score}/100 (وزن 20%)
- محتوا: {content_score}/100 (وزن 35%)
- منابع: {reference_score}/100 (وزن 15%)
- اصالت: {originality_score}/100 (وزن 5%)

## خلاصه پروپوزال:
{summary}

پاسخ را در این قالب JSON برگردان:
{{
    "final_score": <عدد 0-100>,
    "grade": "<عالی/خوب/متوسط/ضعیف/نیاز به بازنگری>",
    "overall_assessment": "ارزیابی کلی در 2-3 پاراگراف",
    "key_strengths": ["3 نقطه قوت اصلی"],
    "key_weaknesses": ["3 نقطه ضعف اصلی"],
    "priority_recommendations": ["3 پیشنهاد اولویت‌دار"],
    "verdict": "تصمیم نهایی: تأیید/تأیید مشروط/رد"
}}
""",
            expected_format='json'
        )
        
        return templates
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """
        دریافت قالب پرامپت
        
        Args:
            name: نام قالب
            
        Returns:
            PromptTemplate یا None
        """
        return self.templates.get(name)
    
    def build_structure_prompt(
        self, 
        sections: Dict[str, str],
        metadata: Dict
    ) -> tuple:
        """
        ساخت پرامپت ارزیابی ساختار
        
        Args:
            sections: بخش‌های پروپوزال
            metadata: متادیتا (آمار)
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        template = self.templates['structure']
        
        # ساخت لیست بخش‌ها
        sections_list = "\n".join([
            f"- {name}: {'✅ موجود' if content else '❌ خالی'} "
            f"({len(content.split()) if content else 0} کلمه)"
            for name, content in sections.items()
        ])
        
        user_prompt = template.user_prompt_template.format(
            sections_list=sections_list,
            word_count=metadata.get('word_count', 0),
            sentence_count=metadata.get('sentence_count', 0),
            section_count=len(sections)
        )
        
        return template.system_prompt, user_prompt
    
    def build_content_prompt(
        self, 
        sections: Dict[str, str],
        keywords: List[str]
    ) -> tuple:
        """
        ساخت پرامپت ارزیابی محتوا
        
        Args:
            sections: بخش‌های پروپوزال
            keywords: کلمات کلیدی
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        template = self.templates['content']
        
        # محدود کردن متن هر بخش
        max_chars = 2000
        
        user_prompt = template.user_prompt_template.format(
            abstract=self._truncate(sections.get('abstract', 'موجود نیست'), max_chars),
            introduction=self._truncate(sections.get('introduction', 'موجود نیست'), max_chars),
            methodology=self._truncate(sections.get('methodology', 'موجود نیست'), max_chars),
            keywords=', '.join(keywords[:10]) if keywords else 'موجود نیست'
        )
        
        return template.system_prompt, user_prompt
    
    def build_references_prompt(
        self, 
        references: List[str],
        stats: Dict
    ) -> tuple:
        """
        ساخت پرامپت ارزیابی منابع
        
        Args:
            references: لیست منابع
            stats: آمار منابع
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        template = self.templates['references']
        
        # ساخت لیست منابع
        references_list = "\n".join([
            f"{i+1}. {ref[:200]}..." if len(ref) > 200 else f"{i+1}. {ref}"
            for i, ref in enumerate(references[:20])  # حداکثر 20 منبع
        ])
        
        user_prompt = template.user_prompt_template.format(
            references_list=references_list or 'منابعی یافت نشد',
            reference_count=len(references),
            persian_refs=stats.get('persian_count', 0),
            english_refs=stats.get('english_count', 0)
        )
        
        return template.system_prompt, user_prompt
    
    def build_overall_prompt(
        self, 
        scores: Dict[str, float],
        summary: str
    ) -> tuple:
        """
        ساخت پرامپت ارزیابی کلی
        
        Args:
            scores: نمرات جزئی
            summary: خلاصه پروپوزال
            
        Returns:
            tuple: (system_prompt, user_prompt)
        """
        template = self.templates['overall']
        
        user_prompt = template.user_prompt_template.format(
            writing_score=scores.get('writing', 0),
            structure_score=scores.get('structure', 0),
            content_score=scores.get('content', 0),
            reference_score=scores.get('references', 0),
            originality_score=scores.get('originality', 0),
            summary=self._truncate(summary, 1000)
        )
        
        return template.system_prompt, user_prompt
    
    def _truncate(self, text: str, max_length: int) -> str:
        """کوتاه کردن متن"""
        if not text:
            return ''
        if len(text) <= max_length:
            return text
        return text[:max_length] + '...'
    
    def get_all_templates(self) -> Dict[str, str]:
        """دریافت همه قالب‌ها"""
        return {
            name: template.user_prompt_template
            for name, template in self.templates.items()
        }


# تست ماژول
if __name__ == "__main__":
    manager = PromptManager()
    
    print("=" * 60)
    print("📝 قالب‌های Prompt موجود")
    print("=" * 60)
    
    for name, template in manager.templates.items():
        print(f"\n🔹 {name}:")
        print(f"   سیستم: {template.system_prompt[:100]}...")

