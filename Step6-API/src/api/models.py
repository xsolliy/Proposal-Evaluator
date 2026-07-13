"""
مدل‌های Pydantic برای درخواست‌ها و پاسخ‌های API
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class EvaluationStatus(str, Enum):
    """وضعیت‌های ارزیابی"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    SUCCESS = "success"
    FAILED = "failed"


class FileFormat(str, Enum):
    """فرمت‌های فایل پشتیبانی شده"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"


class HealthResponse(BaseModel):
    """پاسخ سلامت سیستم"""
    status: str = Field(..., description="وضعیت سیستم")
    version: str = Field(..., description="نسخه API")
    timestamp: datetime = Field(default_factory=datetime.now, description="زمان پاسخ")
    services: Dict[str, bool] = Field(..., description="وضعیت سرویس‌ها")


class EvaluationRequest(BaseModel):
    """درخواست ارزیابی (اختیاری - برای متادیتا)"""
    use_llm: bool = Field(default=True, description="استفاده از LLM برای تحلیل")
    detailed_report: bool = Field(default=True, description="گزارش تفصیلی")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="متادیتای اضافی")
    
    class Config:
        json_schema_extra = {
            "example": {
                "use_llm": True,
                "detailed_report": True,
                "metadata": {
                    "author": "محمد احمدی",
                    "university": "دانشگاه تهران"
                }
            }
        }


class ScoreDetail(BaseModel):
    """جزئیات نمره یک معیار"""
    score: float = Field(..., ge=0, le=100, description="نمره (0-100)")
    grade: str = Field(..., description="درجه")
    weight: float = Field(..., ge=0, le=1, description="وزن در نمره کل")
    weighted_score: float = Field(..., ge=0, le=100, description="نمره وزن‌دار")


class FinalEvaluation(BaseModel):
    """ارزیابی نهایی"""
    final_score: float = Field(..., ge=0, le=100, description="نمره نهایی")
    grade: str = Field(..., description="درجه")
    level: str = Field(..., description="سطح (A, B, C, etc.)")
    pass_status: bool = Field(..., alias="pass", description="وضعیت قبولی")
    individual_scores: Dict[str, float] = Field(..., description="نمرات جزئی")
    weighted_scores: Dict[str, float] = Field(..., description="نمرات وزن‌دار")
    weights: Dict[str, float] = Field(..., description="وزن‌ها")
    
    class Config:
        populate_by_name = True


class ProposalMetadata(BaseModel):
    """متادیتای پروپوزال"""
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size_mb: Optional[float] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    sentence_count: Optional[int] = None
    char_count: Optional[int] = None
    processing_time: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None


class Analysis(BaseModel):
    """تحلیل نقاط قوت و ضعف"""
    strengths: List[str] = Field(..., description="نقاط قوت")
    weaknesses: List[str] = Field(..., description="نقاط ضعف")
    dominant_criterion: str = Field(..., description="معیار برتر")
    weakest_criterion: str = Field(..., description="معیار ضعیف‌تر")
    statistics: Dict[str, Any] = Field(..., description="آمار")


class Warning(BaseModel):
    """هشدار"""
    type: str = Field(..., description="نوع هشدار")
    severity: str = Field(..., description="شدت (low, medium, high)")
    message: str = Field(..., description="پیام هشدار")


class EvaluationResponse(BaseModel):
    """پاسخ کامل ارزیابی"""
    report_id: str = Field(..., description="شناسه منحصربه‌فرد گزارش")
    version: str = Field(..., description="نسخه گزارش")
    generated_at: datetime = Field(..., description="زمان تولید")
    status: EvaluationStatus = Field(..., description="وضعیت ارزیابی")
    summary: str = Field(..., description="خلاصه نتایج")
    final_evaluation: FinalEvaluation = Field(..., description="ارزیابی نهایی")
    detailed_results: Optional[Dict[str, Any]] = Field(None, description="نتایج تفصیلی")
    analysis: Analysis = Field(..., description="تحلیل")
    recommendations: Dict[str, Any] = Field(..., description="پیشنهادات")
    warnings: List[Warning] = Field(default_factory=list, description="هشدارها")
    proposal_metadata: Optional[ProposalMetadata] = Field(None, description="متادیتای پروپوزال")
    evaluation_info: Dict[str, Any] = Field(..., description="اطلاعات ارزیابی")
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "EVAL-A1B2C3D4E5F6",
                "version": "1.0.0",
                "generated_at": "2024-12-23T10:30:00",
                "status": "completed",
                "summary": "پروپوزال با نمره 85.5 (خوب) کیفیت خوبی دارد...",
                "final_evaluation": {
                    "final_score": 85.5,
                    "grade": "خوب",
                    "level": "B",
                    "pass": True,
                    "individual_scores": {
                        "writing": 85.0,
                        "structure": 82.0,
                        "content": 90.0,
                        "references": 78.0,
                        "originality": 92.0
                    },
                    "weighted_scores": {
                        "writing": 21.25,
                        "structure": 16.4,
                        "content": 31.5,
                        "references": 11.7,
                        "originality": 4.6
                    },
                    "weights": {
                        "writing": 0.25,
                        "structure": 0.20,
                        "content": 0.35,
                        "references": 0.15,
                        "originality": 0.05
                    }
                },
                "analysis": {
                    "strengths": ["محتوای علمی عالی است"],
                    "weaknesses": ["منابع نیاز به تکمیل دارند"],
                    "dominant_criterion": "محتوا (90.0)",
                    "weakest_criterion": "منابع (78.0)",
                    "statistics": {}
                },
                "recommendations": {
                    "general": ["پروپوزال خوب است"],
                    "specific": {}
                },
                "warnings": [],
                "evaluation_info": {
                    "actual_time": "3.45 seconds"
                }
            }
        }


class CompactEvaluationResponse(BaseModel):
    """پاسخ خلاصه ارزیابی"""
    report_id: str = Field(..., description="شناسه گزارش")
    final_score: float = Field(..., ge=0, le=100, description="نمره نهایی")
    grade: str = Field(..., description="درجه")
    pass_status: bool = Field(..., alias="pass", description="وضعیت قبولی")
    individual_scores: Dict[str, float] = Field(..., description="نمرات جزئی")
    top_strength: str = Field(..., description="نقطه قوت برتر")
    top_weakness: str = Field(..., description="نقطه ضعف برتر")
    generated_at: datetime = Field(..., description="زمان تولید")
    
    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """پاسخ خطا"""
    error: str = Field(..., description="نوع خطا")
    message: str = Field(..., description="پیام خطا")
    detail: Optional[str] = Field(None, description="جزئیات خطا")
    timestamp: datetime = Field(default_factory=datetime.now, description="زمان خطا")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "فایل نامعتبر است",
                "detail": "فرمت فایل پشتیبانی نمی‌شود. فقط PDF و DOCX مجاز است.",
                "timestamp": "2024-12-23T10:30:00"
            }
        }


class EvaluationStatusResponse(BaseModel):
    """پاسخ وضعیت ارزیابی"""
    evaluation_id: str = Field(..., description="شناسه ارزیابی")
    status: EvaluationStatus = Field(..., description="وضعیت")
    progress: Optional[int] = Field(None, ge=0, le=100, description="درصد پیشرفت")
    message: Optional[str] = Field(None, description="پیام وضعیت")
    started_at: Optional[datetime] = Field(None, description="زمان شروع")
    completed_at: Optional[datetime] = Field(None, description="زمان اتمام")
    result: Optional[EvaluationResponse] = Field(None, description="نتیجه (در صورت اتمام)")

