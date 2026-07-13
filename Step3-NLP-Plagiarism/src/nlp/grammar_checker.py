"""
ماژول بررسی املا و گرامر فارسی
==============================

این ماژول متن فارسی را از نظر املا و گرامر بررسی می‌کند.

Classes:
    GrammarChecker: بررسی‌کننده املا و گرامر

Example:
    >>> checker = GrammarChecker()
    >>> result = checker.check("این متن غلط امللایی دارد")
    >>> print(result['spelling_errors'])
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrammarChecker:
    """
    کلاس بررسی املا و گرامر فارسی
    
    این کلاس از روش‌های مبتنی بر قاعده و آماری برای شناسایی خطاها استفاده می‌کند.
    
    Attributes:
        common_words (set): مجموعه کلمات رایج فارسی
        spelling_patterns (list): الگوهای اشتباهات رایج املایی
        
    Example:
        >>> checker = GrammarChecker()
        >>> result = checker.check("این یک متن تست است.")
        >>> print(f"خطاهای املایی: {result['spelling_error_count']}")
    """
    
    # اشتباهات رایج املایی فارسی
    COMMON_MISSPELLINGS = {
        'اندازی': 'اندازی',
        'میشود': 'می‌شود',
        'میکند': 'می‌کند',
        'میتواند': 'می‌تواند',
        'نمیتواند': 'نمی‌تواند',
        'بعلت': 'به علت',
        'بجای': 'به جای',
        'بطور': 'به طور',
        'بنابرین': 'بنابراین',
        'همانطور': 'همان‌طور',
        'اینگونه': 'این‌گونه',
        'آنچنان': 'آن‌چنان',
    }
    
    # الگوهای گرامری نادرست
    GRAMMAR_PATTERNS = [
        # فاصله قبل از علائم نگارشی
        (r'\s+[،.؛:؟!]', 'فاصله اضافی قبل از علامت نگارشی'),
        # عدم فاصله بعد از علائم نگارشی
        (r'[،.؛:؟!][^\s\n]', 'عدم فاصله بعد از علامت نگارشی'),
        # تکرار فاصله
        (r'\s{3,}', 'فاصله‌های اضافی'),
        # تکرار نقطه
        (r'\.{2,}(?!\.)', 'نقطه‌های تکراری'),
        # شروع جمله با حرف کوچک انگلیسی
        (r'[.؟!]\s+[a-z]', 'شروع جمله با حرف کوچک'),
    ]
    
    # پسوندها و پیشوندهای فارسی که باید نیم‌فاصله داشته باشند
    HALF_SPACE_RULES = {
        'prefixes': ['می', 'نمی', 'بر', 'در', 'بی'],
        'suffixes': ['ها', 'های', 'ای', 'ام', 'ات', 'اش', 'تر', 'ترین']
    }
    
    def __init__(self, use_hazm: bool = True):
        """
        مقداردهی اولیه GrammarChecker
        
        Args:
            use_hazm: استفاده از Hazm برای لماتیزاسیون
        """
        self.use_hazm = use_hazm
        self.lemmatizer = None
        self._init_hazm()
        self._load_word_list()
    
    def _init_hazm(self) -> None:
        """راه‌اندازی Hazm"""
        if self.use_hazm:
            try:
                from hazm import Lemmatizer
                self.lemmatizer = Lemmatizer()
                logger.info("Hazm Lemmatizer بارگذاری شد")
            except ImportError:
                logger.warning("Hazm نصب نیست")
                self.use_hazm = False
    
    def _load_word_list(self) -> None:
        """بارگذاری لیست کلمات صحیح فارسی"""
        # لیست پایه کلمات رایج فارسی
        self.common_words = {
            'و', 'در', 'به', 'از', 'که', 'این', 'را', 'با', 'است', 'برای',
            'آن', 'یک', 'خود', 'تا', 'کرد', 'بر', 'هم', 'نیز', 'شد', 'شده',
            'می', 'گفت', 'او', 'ما', 'اما', 'یا', 'اگر', 'هر', 'بود', 'چه',
            'همه', 'باید', 'دارد', 'پس', 'ها', 'های', 'شود', 'کند', 'بین',
            'کنند', 'هستند', 'بوده', 'دیگر', 'همچنین', 'توسط', 'پژوهش',
            'تحقیق', 'مطالعه', 'بررسی', 'روش', 'نتایج', 'هدف', 'مقدمه',
            'چکیده', 'منابع', 'فصل', 'بخش', 'جدول', 'نمودار', 'شکل',
            'صفحه', 'فهرست', 'پیوست', 'ضمیمه', 'مراجع', 'کتاب', 'مقاله',
            'دانشگاه', 'استاد', 'دانشجو', 'پایان‌نامه', 'رساله', 'پروپوزال',
            # افعال پرکاربرد
            'است', 'بود', 'شد', 'کرد', 'گفت', 'داشت', 'خواهد', 'باشد',
            'شده', 'کرده', 'گفته', 'داشته', 'می‌شود', 'می‌کند', 'می‌توان',
            # صفات
            'خوب', 'بد', 'بزرگ', 'کوچک', 'مهم', 'اصلی', 'جدید', 'قدیم',
            'اول', 'دوم', 'سوم', 'آخر', 'بعد', 'قبل', 'زیاد', 'کم',
        }
    
    def check(self, text: str) -> Dict:
        """
        بررسی کامل متن از نظر املا و گرامر
        
        Args:
            text: متن ورودی
            
        Returns:
            dict: نتایج بررسی
            {
                'spelling_errors': list,
                'grammar_errors': list,
                'half_space_errors': list,
                'spelling_error_count': int,
                'grammar_error_count': int,
                'spelling_accuracy': float,
                'grammar_score': float,
                'suggestions': list
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        # بررسی‌های مختلف
        spelling_errors = self._check_spelling(text)
        grammar_errors = self._check_grammar(text)
        half_space_errors = self._check_half_spaces(text)
        
        # محاسبه آمار
        words = text.split()
        word_count = len(words)
        
        spelling_error_count = len(spelling_errors)
        grammar_error_count = len(grammar_errors) + len(half_space_errors)
        
        # محاسبه دقت املایی
        if word_count > 0:
            spelling_accuracy = max(0, (word_count - spelling_error_count) / word_count * 100)
        else:
            spelling_accuracy = 100
        
        # محاسبه نمره گرامر
        total_errors = spelling_error_count + grammar_error_count
        if word_count > 0:
            error_rate = total_errors / word_count
            grammar_score = max(0, 100 - (error_rate * 200))  # هر خطا 2 نمره کم می‌کند
        else:
            grammar_score = 100
        
        # پیشنهادات بهبود
        suggestions = self._generate_suggestions(
            spelling_errors, grammar_errors, half_space_errors
        )
        
        return {
            'spelling_errors': spelling_errors,
            'grammar_errors': grammar_errors,
            'half_space_errors': half_space_errors,
            'spelling_error_count': spelling_error_count,
            'grammar_error_count': grammar_error_count,
            'spelling_accuracy': round(spelling_accuracy, 2),
            'grammar_score': round(grammar_score, 2),
            'suggestions': suggestions
        }
    
    def _check_spelling(self, text: str) -> List[Dict]:
        """
        بررسی املای کلمات
        
        Args:
            text: متن ورودی
            
        Returns:
            list: لیست خطاهای املایی
        """
        errors = []
        
        # بررسی اشتباهات رایج
        for wrong, correct in self.COMMON_MISSPELLINGS.items():
            if wrong in text:
                # پیدا کردن موقعیت‌ها
                for match in re.finditer(re.escape(wrong), text):
                    errors.append({
                        'type': 'spelling',
                        'word': wrong,
                        'position': match.start(),
                        'suggestion': correct,
                        'message': f'«{wrong}» باید «{correct}» نوشته شود'
                    })
        
        # بررسی کلمات ناشناخته (اختیاری - می‌تواند false positive داشته باشد)
        words = re.findall(r'[\u0600-\u06FF]+', text)
        
        for word in words:
            if len(word) > 2:
                # بررسی با لماتایزر
                root = word
                if self.lemmatizer:
                    try:
                        root = self.lemmatizer.lemmatize(word)
                    except:
                        pass
                
                # اگر کلمه یا ریشه آن در لیست نباشد، مشکوک است
                # (در نسخه production باید از دیکشنری کامل استفاده شود)
        
        return errors
    
    def _check_grammar(self, text: str) -> List[Dict]:
        """
        بررسی قواعد گرامری
        
        Args:
            text: متن ورودی
            
        Returns:
            list: لیست خطاهای گرامری
        """
        errors = []
        
        for pattern, message in self.GRAMMAR_PATTERNS:
            for match in re.finditer(pattern, text):
                errors.append({
                    'type': 'grammar',
                    'text': match.group(),
                    'position': match.start(),
                    'message': message
                })
        
        return errors
    
    def _check_half_spaces(self, text: str) -> List[Dict]:
        """
        بررسی استفاده صحیح از نیم‌فاصله
        
        Args:
            text: متن ورودی
            
        Returns:
            list: لیست خطاهای نیم‌فاصله
        """
        errors = []
        
        # بررسی پیشوندها
        for prefix in self.HALF_SPACE_RULES['prefixes']:
            # الگو: پیشوند + فاصله معمولی + کلمه
            pattern = rf'\b{prefix}\s+(?=[^\s])'
            for match in re.finditer(pattern, text):
                errors.append({
                    'type': 'half_space',
                    'text': match.group(),
                    'position': match.start(),
                    'message': f'بعد از «{prefix}» باید نیم‌فاصله باشد'
                })
        
        # بررسی پسوندها
        for suffix in self.HALF_SPACE_RULES['suffixes']:
            # الگو: کلمه + فاصله معمولی + پسوند
            pattern = rf'(?<=[^\s])\s+{suffix}\b'
            for match in re.finditer(pattern, text):
                errors.append({
                    'type': 'half_space',
                    'text': match.group(),
                    'position': match.start(),
                    'message': f'قبل از «{suffix}» باید نیم‌فاصله باشد'
                })
        
        return errors
    
    def _generate_suggestions(
        self,
        spelling_errors: List[Dict],
        grammar_errors: List[Dict],
        half_space_errors: List[Dict]
    ) -> List[str]:
        """
        تولید پیشنهادات بهبود
        
        Args:
            spelling_errors: خطاهای املایی
            grammar_errors: خطاهای گرامری
            half_space_errors: خطاهای نیم‌فاصله
            
        Returns:
            list: لیست پیشنهادات
        """
        suggestions = []
        
        if spelling_errors:
            suggestions.append(
                f"تعداد {len(spelling_errors)} خطای املایی یافت شد. "
                "لطفاً کلمات مشخص شده را بازبینی کنید."
            )
        
        if grammar_errors:
            # گروه‌بندی خطاها
            error_types = Counter(e['message'] for e in grammar_errors)
            for error_type, count in error_types.most_common(3):
                suggestions.append(f"مشکل: {error_type} ({count} مورد)")
        
        if half_space_errors:
            suggestions.append(
                f"تعداد {len(half_space_errors)} مورد استفاده نادرست از نیم‌فاصله. "
                "از نیم‌فاصله (Ctrl+Shift+2) استفاده کنید."
            )
        
        if not suggestions:
            suggestions.append("متن از نظر املایی و گرامری مشکل خاصی ندارد.")
        
        return suggestions
    
    def _empty_result(self) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'spelling_errors': [],
            'grammar_errors': [],
            'half_space_errors': [],
            'spelling_error_count': 0,
            'grammar_error_count': 0,
            'spelling_accuracy': 100.0,
            'grammar_score': 100.0,
            'suggestions': []
        }
    
    def correct_text(self, text: str) -> str:
        """
        اصلاح خودکار خطاهای رایج
        
        Args:
            text: متن ورودی
            
        Returns:
            str: متن اصلاح شده
        """
        corrected = text
        
        # اصلاح اشتباهات رایج
        for wrong, correct in self.COMMON_MISSPELLINGS.items():
            corrected = corrected.replace(wrong, correct)
        
        # اصلاح فاصله‌های اضافی
        corrected = re.sub(r'\s+', ' ', corrected)
        
        # اصلاح فاصله قبل از علائم
        corrected = re.sub(r'\s+([،.؛:؟!])', r'\1', corrected)
        
        # اضافه کردن فاصله بعد از علائم
        corrected = re.sub(r'([،.؛:؟!])([^\s\n])', r'\1 \2', corrected)
        
        return corrected.strip()


# تست ماژول
if __name__ == "__main__":
    checker = GrammarChecker()
    
    test_text = """
    این یک متن تست است که میخواهیم بررسی کنیم.
    بعلت اینکه در این متن اشتباهات املایی هست ،  باید آنها را پیدا کنیم.
    همانطور که میبینید نیم فاصله ها هم درست نیستند.
    """
    
    result = checker.check(test_text)
    
    print("=" * 60)
    print("📝 نتایج بررسی املا و گرامر")
    print("=" * 60)
    print(f"\n✏️ خطاهای املایی: {result['spelling_error_count']}")
    print(f"📐 خطاهای گرامری: {result['grammar_error_count']}")
    print(f"📊 دقت املایی: {result['spelling_accuracy']}%")
    print(f"📊 نمره گرامر: {result['grammar_score']}")
    
    print("\n💡 پیشنهادات:")
    for suggestion in result['suggestions']:
        print(f"   • {suggestion}")

