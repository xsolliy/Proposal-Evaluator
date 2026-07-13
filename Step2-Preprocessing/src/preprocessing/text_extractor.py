"""
ماژول استخراج متن از فایل‌های PDF و Word
=========================================

این ماژول متن را از فایل‌های PDF و DOCX استخراج می‌کند.

Classes:
    TextExtractor: کلاس اصلی برای استخراج متن

Example:
    >>> extractor = TextExtractor()
    >>> result = extractor.extract("proposal.pdf")
    >>> print(result['text'])
"""

import os
from typing import Dict, List, Optional, Union
from pathlib import Path
import logging

# تنظیم logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextExtractor:
    """
    کلاس استخراج متن از فایل‌های PDF و Word
    
    این کلاس از PyPDF2 و pdfplumber برای PDF و python-docx برای Word استفاده می‌کند.
    
    Attributes:
        supported_formats (list): فرمت‌های پشتیبانی شده ['pdf', 'docx']
        
    Example:
        >>> extractor = TextExtractor()
        >>> result = extractor.extract("my_proposal.pdf")
        >>> print(f"تعداد کلمات: {result['metadata']['word_count']}")
    """
    
    SUPPORTED_FORMATS = ['pdf', 'docx', 'doc']
    MAX_FILE_SIZE_MB = 50
    
    def __init__(self):
        """مقداردهی اولیه TextExtractor"""
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """بررسی نصب بودن پکیج‌های مورد نیاز"""
        missing = []
        
        try:
            import PyPDF2
        except ImportError:
            missing.append('PyPDF2')
        
        try:
            import pdfplumber
        except ImportError:
            missing.append('pdfplumber')
        
        try:
            import docx
        except ImportError:
            missing.append('python-docx')
        
        if missing:
            logger.warning(f"پکیج‌های زیر نصب نیستند: {', '.join(missing)}")
            logger.info("نصب با دستور: pip install " + " ".join(missing))
    
    def extract(self, file_path: str) -> Dict:
        """
        استخراج متن از فایل
        
        Args:
            file_path: مسیر فایل PDF یا DOCX
            
        Returns:
            dict: شامل متن استخراج شده و متادیتا
            {
                'text': str,
                'pages': list,
                'metadata': {
                    'file_name': str,
                    'file_type': str,
                    'file_size_mb': float,
                    'page_count': int,
                    'word_count': int,
                    'char_count': int
                },
                'success': bool,
                'error': str or None
            }
            
        Raises:
            FileNotFoundError: اگر فایل وجود نداشته باشد
            ValueError: اگر فرمت فایل پشتیبانی نشود
        """
        # بررسی وجود فایل
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"فایل یافت نشد: {file_path}")
        
        # بررسی فرمت
        file_ext = Path(file_path).suffix.lower().replace('.', '')
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"فرمت {file_ext} پشتیبانی نمی‌شود. "
                f"فرمت‌های مجاز: {self.SUPPORTED_FORMATS}"
            )
        
        # بررسی حجم فایل
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"حجم فایل ({file_size_mb:.1f} MB) بیش از حد مجاز "
                f"({self.MAX_FILE_SIZE_MB} MB) است"
            )
        
        # استخراج بر اساس فرمت
        try:
            if file_ext == 'pdf':
                result = self._extract_from_pdf(file_path)
            else:  # docx, doc
                result = self._extract_from_docx(file_path)
            
            # اضافه کردن متادیتا
            result['metadata']['file_name'] = os.path.basename(file_path)
            result['metadata']['file_type'] = file_ext
            result['metadata']['file_size_mb'] = round(file_size_mb, 2)
            result['success'] = True
            result['error'] = None
            
            logger.info(
                f"استخراج موفق: {result['metadata']['word_count']} کلمه "
                f"از {result['metadata']['page_count']} صفحه"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"خطا در استخراج: {str(e)}")
            return {
                'text': '',
                'pages': [],
                'metadata': {
                    'file_name': os.path.basename(file_path),
                    'file_type': file_ext,
                    'file_size_mb': round(file_size_mb, 2),
                    'page_count': 0,
                    'word_count': 0,
                    'char_count': 0
                },
                'success': False,
                'error': str(e)
            }
    
    def _extract_from_pdf(self, file_path: str) -> Dict:
        """
        استخراج متن از فایل PDF
        
        از دو روش استفاده می‌کند:
        1. PyPDF2 (سریع‌تر)
        2. pdfplumber (دقیق‌تر، در صورت نیاز)
        
        Args:
            file_path: مسیر فایل PDF
            
        Returns:
            dict: متن و متادیتا
        """
        import PyPDF2
        import pdfplumber
        
        pages_text = []
        full_text = ""
        
        # روش 1: PyPDF2 (اول تلاش می‌کنیم)
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                page_count = len(reader.pages)
                
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    pages_text.append({
                        'page_number': page_num + 1,
                        'text': text.strip()
                    })
                    full_text += text + "\n\n"
        
        except Exception as e:
            logger.warning(f"PyPDF2 ناموفق، استفاده از pdfplumber: {e}")
            pages_text = []
            full_text = ""
        
        # روش 2: pdfplumber (اگر PyPDF2 کافی نبود)
        if len(full_text.strip()) < 100:
            logger.info("استفاده از pdfplumber برای استخراج دقیق‌تر")
            pages_text = []
            full_text = ""
            
            with pdfplumber.open(file_path) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    pages_text.append({
                        'page_number': page_num + 1,
                        'text': text.strip()
                    })
                    full_text += text + "\n\n"
        
        # محاسبه آمار
        full_text = full_text.strip()
        words = full_text.split()
        
        return {
            'text': full_text,
            'pages': pages_text,
            'metadata': {
                'page_count': page_count,
                'word_count': len(words),
                'char_count': len(full_text)
            }
        }
    
    def _extract_from_docx(self, file_path: str) -> Dict:
        """
        استخراج متن از فایل Word (DOCX)
        
        Args:
            file_path: مسیر فایل DOCX
            
        Returns:
            dict: متن و متادیتا
        """
        from docx import Document
        
        doc = Document(file_path)
        
        paragraphs_text = []
        full_text = ""
        
        # استخراج پاراگراف‌ها
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs_text.append(text)
                full_text += text + "\n\n"
        
        # استخراج جداول
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(
                    cell.text.strip() for cell in row.cells
                )
                if row_text.strip():
                    full_text += row_text + "\n"
        
        full_text = full_text.strip()
        words = full_text.split()
        
        # تخمین تعداد صفحات (هر 500 کلمه یک صفحه)
        estimated_pages = max(1, len(words) // 500)
        
        return {
            'text': full_text,
            'pages': [{'page_number': 1, 'text': full_text}],
            'metadata': {
                'page_count': estimated_pages,
                'word_count': len(words),
                'char_count': len(full_text)
            }
        }
    
    def extract_from_text(self, text: str) -> Dict:
        """
        ایجاد ساختار استاندارد از متن خام
        
        Args:
            text: متن خام
            
        Returns:
            dict: ساختار استاندارد
        """
        text = text.strip()
        words = text.split()
        
        return {
            'text': text,
            'pages': [{'page_number': 1, 'text': text}],
            'metadata': {
                'file_name': 'direct_text',
                'file_type': 'text',
                'file_size_mb': len(text.encode('utf-8')) / (1024 * 1024),
                'page_count': max(1, len(words) // 500),
                'word_count': len(words),
                'char_count': len(text)
            },
            'success': True,
            'error': None
        }


# تست ماژول
if __name__ == "__main__":
    # تست با متن نمونه
    extractor = TextExtractor()
    
    sample_text = """
    عنوان: بررسی کاربرد یادگیری ماشین در پردازش زبان فارسی
    
    چکیده:
    این پژوهش به بررسی کاربرد الگوریتم‌های یادگیری ماشین در پردازش زبان طبیعی فارسی می‌پردازد.
    
    مقدمه:
    با گسترش روزافزون داده‌های متنی فارسی در فضای مجازی، نیاز به ابزارهای هوشمند پردازش زبان فارسی بیش از پیش احساس می‌شود.
    """
    
    result = extractor.extract_from_text(sample_text)
    
    print(f"✅ استخراج موفق")
    print(f"   تعداد کلمات: {result['metadata']['word_count']}")
    print(f"   تعداد کاراکتر: {result['metadata']['char_count']}")











