"""
توابع کمکی برای API
"""

import os
import tempfile
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile
import aiofiles
from loguru import logger

from .exceptions import (
    UnsupportedFileFormatError,
    FileTooLargeError,
    FileEmptyError
)


# پیکربندی
MAX_FILE_SIZE_MB = 50
SUPPORTED_FORMATS = ['.pdf', '.docx', '.doc']
UPLOAD_DIR = Path(tempfile.gettempdir()) / 'proposal_uploads'


async def validate_upload_file(file: UploadFile) -> None:
    """
    اعتبارسنجی فایل آپلود شده
    
    Args:
        file: فایل آپلود شده
        
    Raises:
        UnsupportedFileFormatError: فرمت نامعتبر
        FileEmptyError: فایل خالی
    """
    # بررسی نام فایل
    if not file.filename:
        raise FileEmptyError()
    
    # بررسی پسوند
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        raise UnsupportedFileFormatError(file_ext)
    
    logger.info(f"File validated: {file.filename}")


async def save_upload_file(file: UploadFile) -> Path:
    """
    ذخیره فایل آپلود شده
    
    Args:
        file: فایل آپلود شده
        
    Returns:
        Path مسیر فایل ذخیره شده
        
    Raises:
        FileTooLargeError: فایل بزرگ‌تر از حد مجاز
    """
    # ایجاد دایرکتوری در صورت عدم وجود
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    # ساخت مسیر فایل
    file_path = UPLOAD_DIR / file.filename
    
    # ذخیره فایل
    total_size = 0
    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(8192):  # 8KB chunks
                total_size += len(chunk)
                
                # بررسی حجم
                if total_size > max_size_bytes:
                    # حذف فایل ناقص
                    if file_path.exists():
                        file_path.unlink()
                    raise FileTooLargeError(total_size / (1024 * 1024), MAX_FILE_SIZE_MB)
                
                await f.write(chunk)
        
        logger.info(f"File saved: {file_path} ({total_size / 1024:.2f} KB)")
        return file_path
    
    except Exception as e:
        # حذف فایل در صورت خطا
        if file_path.exists():
            file_path.unlink()
        raise


async def cleanup_file(file_path: Path) -> None:
    """
    حذف فایل موقت
    
    Args:
        file_path: مسیر فایل
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"File cleaned up: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {e}")


def format_file_size(size_bytes: int) -> str:
    """
    فرمت کردن حجم فایل
    
    Args:
        size_bytes: حجم به بایت
        
    Returns:
        رشته فرمت شده (مثل "2.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def get_file_info(file_path: Path) -> Tuple[str, float, str]:
    """
    دریافت اطلاعات فایل
    
    Args:
        file_path: مسیر فایل
        
    Returns:
        Tuple شامل (نام، حجم به MB، نوع)
    """
    file_name = file_path.name
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    file_type = file_path.suffix.lower().replace('.', '')
    
    return file_name, file_size_mb, file_type

