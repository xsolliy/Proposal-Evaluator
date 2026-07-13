"""
کلاس‌های Exception سفارشی برای API
"""

from fastapi import HTTPException, status


class ProposalEvaluationException(HTTPException):
    """Exception پایه برای خطاهای ارزیابی"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class FileValidationError(ProposalEvaluationException):
    """خطای اعتبارسنجی فایل"""
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class UnsupportedFileFormatError(FileValidationError):
    """فرمت فایل پشتیبانی نمی‌شود"""
    def __init__(self, file_format: str):
        super().__init__(
            detail=f"فرمت فایل '{file_format}' پشتیبانی نمی‌شود. فقط PDF و DOCX مجاز است."
        )


class FileTooLargeError(FileValidationError):
    """فایل خیلی بزرگ است"""
    def __init__(self, size_mb: float, max_size_mb: int = 50):
        super().__init__(
            detail=f"حجم فایل ({size_mb:.2f} MB) بیش از حد مجاز ({max_size_mb} MB) است."
        )


class FileEmptyError(FileValidationError):
    """فایل خالی است"""
    def __init__(self):
        super().__init__(detail="فایل خالی است یا محتوایی ندارد.")


class TextExtractionError(ProposalEvaluationException):
    """خطا در استخراج متن"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"خطا در استخراج متن از فایل: {detail}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class PreprocessingError(ProposalEvaluationException):
    """خطا در پیش‌پردازش"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"خطا در پیش‌پردازش متن: {detail}",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class NLPError(ProposalEvaluationException):
    """خطا در پردازش NLP"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"خطا در پردازش زبان طبیعی: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class PlagiarismCheckError(ProposalEvaluationException):
    """خطا در تشخیص تقلب"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"خطا در تشخیص سرقت ادبی: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class LLMError(ProposalEvaluationException):
    """خطا در LLM"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"خطا در تحلیل با مدل زبانی: {detail}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


class ScoringError(ProposalEvaluationException):
    """خطا در امتیازدهی"""
    def __init__(self, detail: str):
        super().__init__(
            detail=f"خطا در محاسبه نمرات: {detail}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class EvaluationNotFoundError(ProposalEvaluationException):
    """ارزیابی پیدا نشد"""
    def __init__(self, evaluation_id: str):
        super().__init__(
            detail=f"ارزیابی با شناسه '{evaluation_id}' یافت نشد.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ServiceUnavailableError(ProposalEvaluationException):
    """سرویس در دسترس نیست"""
    def __init__(self, service_name: str):
        super().__init__(
            detail=f"سرویس '{service_name}' در دسترس نیست. لطفاً بعداً تلاش کنید.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

