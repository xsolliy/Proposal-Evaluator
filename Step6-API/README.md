# گام 6: REST API با FastAPI

## 📋 خلاصه

REST API کامل برای سیستم ارزیابی هوشمند پروپوزال‌های فارسی با استفاده از FastAPI.

## 🎯 ویژگی‌ها

- ✅ **آپلود فایل**: پشتیبانی از PDF و DOCX (حداکثر 50MB)
- ✅ **ارزیابی کامل**: تمام معیارها (نگارش، ساختار، محتوا، منابع، اصالت)
- ✅ **گزارش تفصیلی**: JSON ساختاریافته با تمام جزئیات
- ✅ **مدیریت خطا**: Exception handling جامع
- ✅ **مستندسازی خودکار**: Swagger UI و ReDoc
- ✅ **اعتبارسنجی**: Pydantic models برای type safety
- ✅ **Async**: کاملاً async برای عملکرد بهتر
- ✅ **CORS**: پیکربندی شده برای دسترسی cross-origin
- ✅ **Logging**: لاگ‌گیری جامع با loguru

## 📦 نصب

```bash
cd Step6-API
pip install -r requirements.txt
```

## 🚀 راه‌اندازی

### راه‌اندازی ساده

```bash
cd src
python -m api.main
```

یا با uvicorn:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### راه‌اندازی با پیکربندی

```bash
uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --log-level info \
  --workers 1
```

API در آدرس زیر در دسترس خواهد بود:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 📚 Endpoints

### General

#### GET `/`
صفحه اصلی - اطلاعات کلی API

**Response:**
```json
{
  "message": "سیستم ارزیابی هوشمند پروپوزال‌های فارسی",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

#### GET `/health`
بررسی سلامت سیستم

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-12-23T10:30:00",
  "services": {
    "api": true,
    "preprocessing": true,
    "nlp": true,
    "plagiarism": true,
    "llm": false,
    "scoring": true
  }
}
```

### Evaluation

#### POST `/api/evaluate`
ارزیابی کامل پروپوزال

**Parameters:**
- `file` (required): فایل پروپوزال (PDF یا DOCX)
- `use_llm` (optional, default=true): استفاده از LLM
- `detailed_report` (optional, default=true): گزارش تفصیلی

**Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/evaluate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@proposal.pdf" \
  -F "use_llm=true" \
  -F "detailed_report=true"
```

**Response:**
```json
{
  "report_id": "EVAL-A1B2C3D4E5F6",
  "version": "1.0.0",
  "generated_at": "2024-12-23T10:30:00",
  "status": "completed",
  "summary": "پروپوزال با نمره 85.5 (خوب) کیفیت خوبی دارد...",
  "final_evaluation": {
    "final_score": 85.5,
    "grade": "خوب",
    "level": "B",
    "pass": true,
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
  "proposal_metadata": {
    "file_name": "proposal.pdf",
    "file_type": "pdf",
    "file_size_mb": 1.5,
    "word_count": 5000,
    "page_count": 15
  },
  "evaluation_info": {
    "actual_time": "3.45 seconds"
  }
}
```

#### POST `/api/evaluate/compact`
ارزیابی خلاصه (فقط نتایج کلیدی)

**Parameters:**
- `file` (required): فایل پروپوزال
- `use_llm` (optional, default=true): استفاده از LLM

**Response:**
```json
{
  "report_id": "EVAL-A1B2C3D4E5F6",
  "final_score": 85.5,
  "grade": "خوب",
  "pass": true,
  "individual_scores": {
    "writing": 85.0,
    "structure": 82.0,
    "content": 90.0,
    "references": 78.0,
    "originality": 92.0
  },
  "top_strength": "محتوای علمی عالی است",
  "top_weakness": "منابع نیاز به تکمیل دارند",
  "generated_at": "2024-12-23T10:30:00"
}
```

### Configuration

#### GET `/api/weights`
دریافت وزن‌های امتیازدهی

**Response:**
```json
{
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
```

#### GET `/api/supported-formats`
فرمت‌های فایل پشتیبانی شده

**Response:**
```json
{
  "formats": ["pdf", "docx", "doc"],
  "max_file_size_mb": 50,
  "description": "فایل‌های PDF و Microsoft Word پشتیبانی می‌شوند"
}
```

## 🧪 تست

```bash
# اجرای تمام تست‌ها
pytest tests/ -v

# تست با coverage
pytest tests/ --cov=src/api --cov-report=html

# تست یک فایل خاص
pytest tests/test_api.py -v
```

## 📝 استفاده با Python

```python
import requests

# آپلود و ارزیابی
url = "http://localhost:8000/api/evaluate"
files = {"file": open("proposal.pdf", "rb")}
params = {"use_llm": True, "detailed_report": True}

response = requests.post(url, files=files, params=params)
result = response.json()

print(f"نمره نهایی: {result['final_evaluation']['final_score']}")
print(f"درجه: {result['final_evaluation']['grade']}")
```

## 🐛 مدیریت خطا

API خطاهای زیر را مدیریت می‌کند:

| کد | خطا | توضیح |
|----|-----|-------|
| 400 | Bad Request | فایل نامعتبر یا پارامترهای اشتباه |
| 404 | Not Found | Endpoint پیدا نشد |
| 422 | Unprocessable Entity | خطا در پردازش فایل |
| 500 | Internal Server Error | خطای داخلی سرور |
| 503 | Service Unavailable | سرویس در دسترس نیست |

**نمونه پاسخ خطا:**
```json
{
  "error": "UnsupportedFileFormatError",
  "message": "فرمت فایل 'txt' پشتیبانی نمی‌شود",
  "detail": null,
  "timestamp": "2024-12-23T10:30:00"
}
```

## 📊 لاگ‌ها

لاگ‌ها در فایل `api.log` ذخیره می‌شوند:

```
2024-12-23 10:30:00 | INFO | Received evaluation request for file: proposal.pdf
2024-12-23 10:30:01 | INFO | File saved to: /tmp/proposal_uploads/proposal.pdf
2024-12-23 10:30:03 | INFO | Evaluation completed successfully: EVAL-A1B2C3D4E5F6
2024-12-23 10:30:03 | INFO | File cleaned up: /tmp/proposal_uploads/proposal.pdf
```

## 🔒 امنیت

- ✅ اعتبارسنجی فرمت فایل
- ✅ محدودیت حجم فایل (50MB)
- ✅ پاکسازی خودکار فایل‌های موقت
- ✅ Validation با Pydantic
- ✅ Exception handling جامع

## 🌐 CORS

CORS به صورت پیش‌فرض برای تمام origins فعال است. برای محیط production، پیکربندی کنید:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📦 ساختار پروژه

```
Step6-API/
├── src/
│   └── api/
│       ├── __init__.py
│       ├── main.py          # FastAPI app اصلی
│       ├── models.py        # Pydantic models
│       ├── exceptions.py    # Custom exceptions
│       └── utils.py         # توابع کمکی
├── tests/
│   └── test_api.py         # تست‌های API
├── requirements.txt        # وابستگی‌ها
├── README.md              # این فایل
└── STEP6_REPORT.md        # گزارش کامل

```

## 🔧 پیکربندی

### متغیرهای محیطی (اختیاری)

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export MAX_FILE_SIZE_MB=50
export LOG_LEVEL=INFO
```

### فایل پیکربندی

در حال حاضر پیکربندی در کد است. می‌توانید از `pydantic-settings` استفاده کنید:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    max_file_size_mb: int = 50
    
    class Config:
        env_file = ".env"
```

## 📚 مستندات بیشتر

- [STEP6_REPORT.md](STEP6_REPORT.md) - گزارش کامل گام 6
- [Swagger UI](http://localhost:8000/docs) - مستندات تعاملی
- [ReDoc](http://localhost:8000/redoc) - مستندات خواناتر

## ⚠️ نکات مهم

1. **فایل‌های موقت**: فایل‌های آپلود شده پس از ارزیابی حذف می‌شوند
2. **حجم فایل**: حداکثر 50MB
3. **فرمت‌ها**: فقط PDF و DOCX
4. **Async**: تمام endpoints به صورت async هستند
5. **یکپارچه‌سازی**: در حال حاضر از داده‌های نمونه استفاده می‌شود. برای عملکرد کامل، باید با ماژول‌های قبلی یکپارچه شود.

## 🚧 TODO

- [ ] یکپارچه‌سازی کامل با ماژول‌های گام‌های 2، 3، 4 و 5
- [ ] پیاده‌سازی پایگاه داده برای ذخیره نتایج
- [ ] افزودن authentication و authorization
- [ ] پیاده‌سازی rate limiting
- [ ] افزودن caching
- [ ] پیاده‌سازی background tasks برای ارزیابی‌های طولانی
- [ ] افزودن WebSocket برای نمایش پیشرفت

## 📄 مجوز

این پروژه بخشی از سیستم ارزیابی هوشمند پروپوزال‌های فارسی است.

---

**نسخه**: 1.0.0  
**تاریخ**: دی 1404  
**تیم**: رایا هوش فانوس

