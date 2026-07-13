# گام 5: سیستم امتیازدهی و گزارش‌دهی

## 📋 خلاصه

این ماژول مسئول محاسبه نمرات نهایی و تولید گزارش جامع ارزیابی پروپوزال‌های فارسی است.

## 🎯 معیارهای امتیازدهی

سیستم بر اساس 5 معیار با وزن‌های ثابت امتیازدهی می‌کند:

| معیار      | وزن  | مسئولیت                                            |
| ---------- | ---- | -------------------------------------------------- |
| **نگارش**  | 25%  | املا، گرامر، خوانایی (از ماژول NLP)               |
| **ساختار** | 20%  | وجود بخش‌های الزامی و اختیاری                      |
| **محتوا**  | 35%  | کیفیت علمی، انسجام، روش‌شناسی (از ماژول LLM)      |
| **منابع**  | 15%  | تعداد، کیفیت، تنوع و به‌روز بودن منابع            |
| **اصالت**  | 5%   | عدم تقلب و تشابه با پروپوزال‌های دیگر (از Plagiarism) |

## 📦 ماژول‌ها

### 1. StructureScorer
محاسبه نمره ساختاری بر اساس:
- وجود بخش‌های الزامی (چکیده، مقدمه، روش‌شناسی، منابع)
- وجود بخش‌های اختیاری (پیشینه، اهداف، بحث، ...)
- طول مناسب هر بخش
- تناسب بخش‌ها با یکدیگر

### 2. ReferenceScorer
محاسبه نمره منابع بر اساس:
- **کمیت** (30%): تعداد منابع (حداقل 10، توصیه 20+)
- **به‌روز بودن** (35%): منابع در 3-5 سال اخیر
- **تنوع** (20%): ترکیب فارسی و انگلیسی
- **کیفیت** (15%): فرمت‌نویسی صحیح

### 3. OriginalityScorer
محاسبه نمره اصالت بر اساس:
- بیشترین درصد تشابه با پروپوزال‌های قبلی
- میانگین تشابه با اسناد مشابه
- تعداد اسناد با تشابه بالا

**آستانه‌های تشخیص:**
- تشابه < 30%: اصیل
- تشابه 30-50%: قابل قبول
- تشابه 50-70%: نیاز به بررسی
- تشابه > 70%: احتمال تقلب بالا

### 4. FinalScoreCalculator
تجمیع نمرات با وزن‌های مشخص و محاسبه:
- نمره نهایی (0-100)
- درجه (عالی، خوب، متوسط، ...)
- نقاط قوت و ضعف
- آمار و تحلیل

### 5. ReportGenerator
تولید گزارش JSON کامل شامل:
- خلاصه نتایج
- نمرات تفصیلی هر بخش
- تحلیل نقاط قوت و ضعف
- پیشنهادات بهبود
- هشدارها
- متادیتا

### 6. EvaluationPipeline
یکپارچه‌سازی تمام ماژول‌ها و اجرای خط لوله کامل ارزیابی

## 🚀 نصب

```bash
cd Step5-Scoring
pip install -r requirements.txt
```

## 💻 استفاده

### استفاده اساسی

```python
from scoring.evaluation_pipeline import EvaluationPipeline

# ایجاد خط لوله ارزیابی
pipeline = EvaluationPipeline()

# داده‌های ورودی
sections = {
    'abstract': 'متن چکیده...',
    'introduction': 'متن مقدمه...',
    'methodology': 'متن روش‌شناسی...',
    'references': 'متن منابع...'
}

references = [
    'احمدی، علی (1402). عنوان کتاب. تهران: نشر علم.',
    'Smith, J. (2022). Title. Publisher.',
    # ...
]

plagiarism_result = {
    'originality_score': 85.0,
    'plagiarism_percentage': 15.0,
    'max_similarity': 15.0,
    'similar_documents': [],
    'checked_against': 100
}

# ارزیابی کامل
report = pipeline.evaluate(
    sections=sections,
    references=references,
    plagiarism_result=plagiarism_result,
    writing_score=85.0,  # از ماژول NLP
    content_score=90.0   # از ماژول LLM
)

# نمایش نمره نهایی
print(f"نمره نهایی: {report['final_evaluation']['final_score']:.2f}/100")
print(f"درجه: {report['final_evaluation']['grade']}")
```

### ارزیابی جزئی

```python
# فقط ساختار
structure_result = pipeline.evaluate_structure_only(sections)

# فقط منابع
references_result = pipeline.evaluate_references_only(references)

# فقط اصالت
originality_result = pipeline.evaluate_originality_only(plagiarism_result)
```

### ذخیره گزارش

```python
from scoring.report_generator import ReportGenerator

generator = ReportGenerator()

# ذخیره گزارش کامل
generator.save_to_file(report, 'evaluation_report.json')

# تولید گزارش خلاصه
compact_report = generator.generate_compact(final_score_result)
```

## 🧪 تست

```bash
# اجرای تمام تست‌ها
pytest tests/ -v

# اجرای یک تست خاص
pytest tests/test_evaluation.py::TestEvaluationPipeline -v

# اجرا با coverage
pytest tests/ --cov=src/scoring --cov-report=html
```

## 📊 ساختار خروجی

### گزارش کامل JSON

```json
{
  "report_id": "EVAL-A1B2C3D4E5F6",
  "version": "1.0.0",
  "generated_at": "2024-12-23T10:30:00",
  "status": "success",
  
  "summary": "خلاصه متنی نتایج...",
  
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
  
  "detailed_results": {
    "writing": {...},
    "structure": {...},
    "content": {...},
    "references": {...},
    "originality": {...}
  },
  
  "analysis": {
    "strengths": [
      "محتوای علمی در سطح عالی است",
      "اصالت پروپوزال بسیار خوب است"
    ],
    "weaknesses": [
      "منابع نیاز به تکمیل دارند"
    ],
    "dominant_criterion": "محتوا (90.0)",
    "weakest_criterion": "منابع (78.0)",
    "statistics": {
      "min_score": 78.0,
      "max_score": 92.0,
      "average_score": 85.4,
      "consistency": "یکنواخت"
    }
  },
  
  "recommendations": {
    "general": [
      "پروپوزال خوب است. با رفع نواقص جزئی، آماده ارائه خواهد بود."
    ],
    "specific": {
      "references": [
        "حداقل 5 منبع دیگر اضافه کنید",
        "منابع جدیدتر (5 سال اخیر) اضافه کنید"
      ]
    }
  },
  
  "warnings": [
    {
      "type": "structure",
      "severity": "medium",
      "message": "بخش‌های الزامی ناقص: objectives"
    }
  ],
  
  "proposal_metadata": {
    "file_name": "proposal.pdf",
    "word_count": 5000,
    "page_count": 15
  },
  
  "evaluation_info": {
    "actual_time": "3.45 seconds",
    "criteria_count": 5,
    "passed_criteria": 5
  }
}
```

## 📈 درجه‌بندی

| نمره      | درجه                  | سطح | وضعیت          |
| --------- | --------------------- | --- | -------------- |
| 90-100    | عالی                  | A   | قبول با تقدیر  |
| 85-89     | خیلی خوب              | A-  | قبول با تقدیر  |
| 80-84     | خوب                   | B+  | قبول           |
| 75-79     | بالاتر از متوسط       | B   | قبول           |
| 70-74     | متوسط                 | C+  | قبول           |
| 60-69     | قابل قبول             | C   | قبول مشروط     |
| 50-59     | ضعیف                  | D   | نیاز به بازنگری |
| 40-49     | بسیار ضعیف            | F   | رد             |
| 0-39      | نیاز به بازنویسی کامل | F   | رد             |

## 🔧 پیکربندی

### تغییر وزن‌ها (توصیه نمی‌شود)

وزن‌ها در کلاس `FinalScoreCalculator` به صورت ثابت تعریف شده‌اند:

```python
WEIGHTS = {
    'writing': 0.25,
    'structure': 0.20,
    'content': 0.35,
    'references': 0.15,
    'originality': 0.05
}
```

### تغییر آستانه‌های تشخیص

در `OriginalityScorer`:

```python
THRESHOLDS = {
    'very_high': 90,
    'high': 70,
    'moderate': 50,
    'low': 30,
    'minimal': 15
}
```

## 📝 لاگ‌ها

سیستم از `loguru` برای لاگ‌گیری استفاده می‌کند:

```python
from loguru import logger

# فعال‌سازی لاگ در فایل
logger.add("evaluation.log", rotation="10 MB")
```

## 🤝 یکپارچگی با گام‌های قبل

این ماژول نیاز به خروجی گام‌های قبل دارد:

- **گام 2** (Preprocessing): sections, metadata
- **گام 3** (NLP): writing_score
- **گام 3** (Plagiarism): plagiarism_result
- **گام 4** (LLM): content_score

## ⚠️ نکات مهم

1. **مجموع وزن‌ها باید 1 باشد** - سیستم خودکار اعتبارسنجی می‌کند
2. **نمرات ورودی باید بین 0-100 باشند**
3. **گزارش‌ها به صورت UTF-8 ذخیره می‌شوند**
4. **آستانه قبولی: 60 نمره**

## 📚 مستندات بیشتر

- [STEP5_REPORT.md](STEP5_REPORT.md) - گزارش کامل گام 5
- [tests/test_evaluation.py](tests/test_evaluation.py) - نمونه‌های کاربردی

## 📄 مجوز

این پروژه بخشی از سیستم ارزیابی هوشمند پروپوزال‌های فارسی است.

---

**نسخه**: 1.0.0  
**تاریخ**: دی 1404  
**تیم**: رایا هوش فانوس

