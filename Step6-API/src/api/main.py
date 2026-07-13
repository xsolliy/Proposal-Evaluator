"""
FastAPI Application - سیستم ارزیابی هوشمند پروپوزال‌های فارسی
"""

import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .models import (
    HealthResponse,
    EvaluationResponse,
    CompactEvaluationResponse,
    ErrorResponse,
    EvaluationRequest
)
from .exceptions import ProposalEvaluationException
from .utils import validate_upload_file, save_upload_file, cleanup_file, get_file_info
from .integrated_evaluator import IntegratedEvaluator


# ===== Application Setup =====

app = FastAPI(
    title="Proposal Evaluation API",
    description="REST API برای ارزیابی هوشمند پروپوزال‌های فارسی",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در محیط تولید، دامنه‌های مشخص را اضافه کنید
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logger.add(
    "api.log",
    rotation="10 MB",
    retention="10 days",
    level="INFO"
)

# Initialize integrated evaluator
evaluator = IntegratedEvaluator()


# ===== Exception Handlers =====

@app.exception_handler(ProposalEvaluationException)
async def proposal_evaluation_exception_handler(
    request: Request,
    exc: ProposalEvaluationException
):
    """مدیریت خطاهای سفارشی"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            detail=None,
            timestamp=datetime.now()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """مدیریت خطاهای عمومی"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="خطای داخلی سرور",
            detail=str(exc),
            timestamp=datetime.now()
        ).model_dump()
    )


# ===== Startup/Shutdown Events =====

@app.on_event("startup")
async def startup_event():
    """رویدادهای راه‌اندازی"""
    logger.info("Starting Proposal Evaluation API...")
    logger.info("API is ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """رویدادهای خاموش شدن"""
    logger.info("Shutting down Proposal Evaluation API...")


# ===== Endpoints =====

@app.get("/", tags=["General"])
async def root():
    """صفحه اصلی"""
    return {
        "message": "سیستم ارزیابی هوشمند پروپوزال‌های فارسی",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["General"],
    summary="بررسی سلامت سیستم"
)
async def health_check():
    """
    بررسی وضعیت سلامت API و سرویس‌های وابسته
    """
    # بررسی وضعیت سرویس‌ها
    services = {
        "api": True,
        "preprocessing": True,
        "nlp": True,
        "plagiarism": True,
        "llm": False,  # این باید از سرویس واقعی چک شود
        "scoring": True
    }
    
    return HealthResponse(
        status="healthy" if all(services.values()) else "degraded",
        version="1.0.0",
        timestamp=datetime.now(),
        services=services
    )


@app.post(
    "/api/evaluate",
    response_model=EvaluationResponse,
    tags=["Evaluation"],
    summary="ارزیابی پروپوزال",
    description="آپلود و ارزیابی کامل پروپوزال با تمام معیارها"
)
async def evaluate_proposal(
    file: UploadFile = File(..., description="فایل پروپوزال (PDF یا DOCX)"),
    use_llm: bool = True,
    detailed_report: bool = True
):
    """
    ارزیابی کامل پروپوزال
    
    - **file**: فایل پروپوزال (PDF یا DOCX، حداکثر 50MB)
    - **use_llm**: استفاده از LLM برای تحلیل محتوا (پیش‌فرض: True)
    - **detailed_report**: تولید گزارش تفصیلی (پیش‌فرض: True)
    
    Returns:
        گزارش کامل ارزیابی شامل نمرات، تحلیل و توصیه‌ها
    """
    file_path = None
    
    try:
        logger.info(f"Received evaluation request for file: {file.filename}")
        
        # اعتبارسنجی فایل
        await validate_upload_file(file)
        
        # ذخیره فایل
        file_path = await save_upload_file(file)
        logger.info(f"File saved to: {file_path}")
        
        # ارزیابی یکپارچه با تمام ماژول‌ها
        logger.info("Starting integrated evaluation...")
        result = evaluator.evaluate_file(file_path, use_llm)
        
        # تبدیل به مدل پاسخ
        response = EvaluationResponse(**result)
        
        logger.info(f"Evaluation completed successfully: {response.report_id}")
        return response
    
    except ProposalEvaluationException:
        raise
    
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطا در ارزیابی: {str(e)}"
        )
    
    finally:
        # پاکسازی فایل موقت
        if file_path:
            await cleanup_file(file_path)


@app.post(
    "/api/evaluate/compact",
    response_model=CompactEvaluationResponse,
    tags=["Evaluation"],
    summary="ارزیابی خلاصه پروپوزال"
)
async def evaluate_proposal_compact(
    file: UploadFile = File(..., description="فایل پروپوزال"),
    use_llm: bool = True
):
    """
    ارزیابی پروپوزال با گزارش خلاصه (فقط نتایج کلیدی)
    """
    # فراخوانی ارزیابی کامل
    full_result = await evaluate_proposal(file, use_llm, detailed_report=False)
    
    # استخراج نتایج خلاصه
    return CompactEvaluationResponse(
        report_id=full_result.report_id,
        final_score=full_result.final_evaluation.final_score,
        grade=full_result.final_evaluation.grade,
        pass_status=full_result.final_evaluation.pass_status,
        individual_scores=full_result.final_evaluation.individual_scores,
        top_strength=full_result.analysis.strengths[0] if full_result.analysis.strengths else "ندارد",
        top_weakness=full_result.analysis.weaknesses[0] if full_result.analysis.weaknesses else "ندارد",
        generated_at=full_result.generated_at
    )


@app.get(
    "/api/weights",
    tags=["Configuration"],
    summary="دریافت وزن‌های امتیازدهی"
)
async def get_scoring_weights():
    """
    دریافت وزن‌های ثابت امتیازدهی
    """
    return {
        "weights": {
            "writing": 0.25,
            "structure": 0.20,
            "content": 0.35,
            "references": 0.15,
            "originality": 0.05
        },
        "description": {
            "writing": "نگارش: املا، گرامر، خوانایی",
            "structure": "ساختار: وجود بخش‌های الزامی و اختیاری",
            "content": "محتوا: کیفیت علمی، انسجام، روش‌شناسی",
            "references": "منابع: کمیت، کیفیت، تنوع و به‌روز بودن",
            "originality": "اصالت: عدم تقلب و تشابه"
        }
    }


@app.get(
    "/api/supported-formats",
    tags=["Configuration"],
    summary="فرمت‌های پشتیبانی شده"
)
async def get_supported_formats():
    """
    دریافت فرمت‌های فایل پشتیبانی شده
    """
    return {
        "formats": ["pdf", "docx", "doc"],
        "max_file_size_mb": 50,
        "description": "فایل‌های PDF و Microsoft Word پشتیبانی می‌شوند"
    }


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

