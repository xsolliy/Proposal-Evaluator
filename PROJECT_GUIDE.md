# 🎯 راهنمای کامل پیاده‌سازی: سیستم ارزیابی هوشمند پروپوزال

## 📌 خلاصه پروژه

**هدف**: ساخت سیستم هسته (Core System) ارزیابی خودکار و هوشمند پروپوزال‌های فارسی با استفاده از LLM و تکنیک‌های NLP، به صورت کاملاً آفلاین.

**مدت**: 5 ماه (800 ساعت - 2 نفره)  
**تاریخ**: 10 آبان 1404 تا 11 بهمن 1404

---

## ⚠️ الزامات حیاتی (باید رعایت شود)

### 1. آفلاین بودن کامل
- تمام مدل‌ها باید local اجرا شوند
- هیچ API خارجی استفاده نشود
- LLM باید با Ollama یا llama.cpp اجرا شود

### 2. پشتیبانی کامل فارسی
- تمام پردازش‌ها باید فارسی را پشتیبانی کنند
- مدل‌های فارسی: ParsBERT, Sentence-BERT فارسی
- ابزارها: Hazm, Persian-LanguageTool

### 3. معیارهای امتیازدهی (ثابت)
- **نگارش**: 25%
- **ساختار**: 20%
- **محتوا**: 35%
- **منابع**: 15%
- **اصالت** (عدم تقلب): 5%

### 4. خروجی نهایی
- REST API با FastAPI
- گزارش JSON کامل
- رابط تست Streamlit (ساده، نه حرفه‌ای)
- مستندات کامل

---

## 🏗️ معماری کلی

```
proposal-evaluation-system/
├── src/
│   ├── preprocessing/      # استخراج و پیش‌پردازش
│   ├── nlp/               # بررسی نگارشی و NLP
│   ├── plagiarism/        # تشخیص تقلب
│   ├── llm/               # تحلیل عمیق با LLM
│   ├── scoring/           # امتیازدهی
│   └── api/               # FastAPI
├── models/                # مدل‌های دانلود شده
├── database/              # پایگاه داده پروپوزال‌ها
├── tests/                 # تست‌ها
├── streamlit_app/         # رابط تست
├── docs/                  # مستندات
└── requirements.txt       # وابستگی‌ها
```

---

## 📦 تکنولوژی‌های اصلی

### Python Packages
```
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
pydantic==2.4.2

# NLP فارسی
hazm==0.7.0
parsivar==0.2.3
sentence-transformers==2.2.2
transformers==4.35.0

# LLM
ollama  # برای اجرای local

# استخراج متن
PyPDF2==3.0.1
python-docx==1.1.0
pdfplumber==0.10.3

# تحلیل
keybert==0.8.3
yake==0.4.8
scikit-learn==1.3.2
numpy==1.24.3

# رابط کاربری
streamlit==1.28.0

# دیتابیس
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

### مدل‌های مورد نیاز
- **ParsBERT**: `HooshvareLab/bert-fa-base-uncased`
- **Sentence-BERT فارسی**: `m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens`
- **LLM آفلاین**: `llama3.1:8b` یا `qwen2.5:7b` از Ollama

---

## 📅 گام‌های پیاده‌سازی (8 گام)

---

### **گام 0: راه‌اندازی اولیه پروژه (40 ساعت)**
**تاریخ**: 10 آبان - 15 آبان

#### فعالیت‌ها:
1. ایجاد ساختار پروژه
2. نصب Python 3.10+ و ابزارهای توسعه
3. ایجاد virtual environment
4. نصب پکیج‌های اولیه
5. راه‌اندازی Git repository
6. تست اولیه ابزارها

#### خروجی:
- محیط توسعه کامل و آماده
- ساختار پروژه ایجاد شده
- `requirements.txt` کامل

#### چک‌لیست:
- [ ] Python 3.10+ نصب شده
- [ ] Virtual env فعال است
- [ ] تمام پکیج‌ها بدون خطا نصب شدند
- [ ] ساختار فولدرها ایجاد شد

---

### **گام 1: تحلیل نیازمندی‌ها و طراحی معماری (60 ساعت)**
**تاریخ**: 16 آبان - 22 آبان

#### فعالیت‌ها:
1. طراحی معماری کلی (Flow Diagram)
2. تعریف API endpoints
3. طراحی مدل داده (Database Schema)
4. تست و انتخاب مدل‌های NLP
5. نصب و تست Ollama + مدل LLM
6. نوشتن سند معماری

#### خروجی:
- سند معماری (Architecture.md)
- دیاگرام جریان داده
- مدل دیتابیس طراحی شده
- LLM نصب و تست شده

#### نکات مهم:
- مدل LLM باید حداقل 7B parameters داشته باشد
- تست کن که روی سخت‌افزار موجود اجرا می‌شود
- معماری باید modular باشد

---

### **گام 2: پیاده‌سازی ماژول پیش‌پردازش و استخراج متن (120 ساعت)**
**تاریخ**: 23 آبان - 6 آذر

#### فعالیت‌ها:
1. **استخراج متن از PDF** (PyPDF2 + pdfplumber)
   - خواندن فایل PDF
   - استخراج متن فارسی
   - حفظ ساختار

2. **استخراج متن از Word** (python-docx)
   - خواندن فایل‌های .docx
   - استخراج متن و فرمت‌بندی

3. **پیش‌پردازش با Hazm**:
   ```python
   from hazm import Normalizer, word_tokenize, sent_tokenize
   
   normalizer = Normalizer()
   text = normalizer.normalize(raw_text)
   sentences = sent_tokenize(text)
   words = word_tokenize(text)
   ```

4. **شناسایی بخش‌های پروپوزال**:
   - چکیده (Abstract)
   - مقدمه (Introduction)
   - روش‌شناسی (Methodology)
   - منابع (References)
   - استفاده از regex و keyword matching

#### خروجی:
```python
{
    "raw_text": "...",
    "normalized_text": "...",
    "sections": {
        "abstract": "...",
        "introduction": "...",
        "methodology": "...",
        "references": [...]
    },
    "metadata": {
        "word_count": 5000,
        "page_count": 15
    }
}
```

#### معیار موفقیت:
- استخراج از PDF/Word با موفقیت 95%+
- شناسایی حداقل 3 بخش اصلی

---

### **گام 3: توسعه ماژول‌های NLP و تشخیص تقلب (180 ساعت)**
**تاریخ**: 7 آذر - 27 آذر

#### بخش A: بررسی نگارشی (60 ساعت)

1. **بررسی املا و گرامر**:
   - استفاده از Persian-LanguageTool
   - شناسایی خطاهای املایی
   - محاسبه درصد صحت

2. **تحلیل‌های آماری**:
   ```python
   stats = {
       "total_words": len(words),
       "total_sentences": len(sentences),
       "avg_sentence_length": total_words / total_sentences,
       "unique_words": len(set(words)),
       "lexical_diversity": unique_words / total_words
   }
   ```

3. **محاسبه نمره نگارشی (25%)**:
   - املا: 40%
   - گرامر: 30%
   - خوانایی: 30%

#### بخش B: استخراج اطلاعات (60 ساعت)

1. **استخراج کلمات کلیدی**:
   ```python
   from keybert import KeyBERT
   
   model = KeyBERT('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
   keywords = model.extract_keywords(text, keyphrase_ngram_range=(1, 2), top_n=10)
   ```

2. **خلاصه‌سازی متن**:
   - استفاده از extractive summarization
   - انتخاب مهم‌ترین جملات

#### بخش C: تشخیص تقلب (60 ساعت)

1. **تبدیل به Embeddings**:
   ```python
   from sentence_transformers import SentenceTransformer
   
   model = SentenceTransformer('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
   embedding = model.encode(text)
   ```

2. **محاسبه Cosine Similarity**:
   ```python
   from sklearn.metrics.pairwise import cosine_similarity
   
   similarity = cosine_similarity([new_embedding], database_embeddings)
   max_similarity = similarity.max()
   plagiarism_percentage = max_similarity * 100
   ```

3. **ذخیره در Database**:
   - هر پروپوزال جدید به پایگاه داده اضافه شود

#### خروجی:
```python
{
    "writing_score": 85,  # از 100
    "writing_details": {
        "spelling_errors": 5,
        "grammar_errors": 3,
        "readability": 80
    },
    "keywords": ["یادگیری ماشین", "پردازش زبان", ...],
    "summary": "خلاصه پروپوزال...",
    "plagiarism": {
        "percentage": 12,
        "similar_documents": [...]
    }
}
```

#### معیار موفقیت:
- تشخیص تشابه بالای 80% با دقت
- استخراج حداقل 10 کلیدواژه مرتبط

---

### **گام 4: یکپارچه‌سازی و راه‌اندازی LLM آفلاین (160 ساعت)**
**تاریخ**: 28 آذر - 17 دی

#### فعالیت‌ها:

1. **نصب و پیکربندی Ollama**:
   ```bash
   # نصب Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # دانلود مدل
   ollama pull llama3.1:8b
   # یا
   ollama pull qwen2.5:7b
   ```

2. **طراحی Prompt برای تحلیل پروپوزال**:
   ```python
   prompt = f"""
   شما یک ارزیاب علمی حرفه‌ای هستید. پروپوزال زیر را از نظر کیفیت محتوا، 
   انسجام، روش‌شناسی و تناسب اهداف با روش‌ها ارزیابی کنید.
   
   پروپوزال:
   {proposal_text}
   
   لطفاً موارد زیر را ارائه دهید:
   1. نقاط قوت (حداقل 3 مورد)
   2. نقاط ضعف (حداقل 3 مورد)
   3. پیشنهادات بهبود (حداقل 3 مورد)
   4. نمره کیفیت محتوا از 100
   
   پاسخ را به صورت JSON برگردانید.
   """
   ```

3. **فراخوانی LLM**:
   ```python
   import ollama
   
   response = ollama.chat(
       model='llama3.1:8b',
       messages=[{'role': 'user', 'content': prompt}],
       options={'temperature': 0}  # برای یکنواختی
   )
   
   result = response['message']['content']
   ```

4. **استخراج و پردازش نتیجه**:
   - Parse کردن JSON
   - اعتبارسنجی خروجی
   - محاسبه نمره محتوا (35%)

#### خروجی:
```python
{
    "content_score": 75,  # از 100 (وزن 35%)
    "strengths": [
        "روش‌شناسی دقیق و کاربردی",
        "اهداف واضح و قابل سنجش",
        "منابع معتبر و به‌روز"
    ],
    "weaknesses": [
        "بخش مقدمه کوتاه است",
        "محدودیت‌های پژوهش مشخص نشده"
    ],
    "suggestions": [
        "مقدمه را گسترش دهید",
        "محدودیت‌ها را اضافه کنید"
    ]
}
```

#### معیار موفقیت:
- LLM پاسخ‌های معنادار و مرتبط تولید کند
- زمان پاسخ کمتر از 2 دقیقه باشد

---

### **گام 5: پیاده‌سازی سیستم امتیازدهی و گزارش‌دهی (100 ساعت)**
**تاریخ**: 18 دی - 29 دی

#### فعالیت‌ها:

1. **محاسبه نمره ساختاری (20%)**:
   ```python
   structure_score = 0
   required_sections = ['abstract', 'introduction', 'methodology', 'references']
   
   for section in required_sections:
       if section in proposal_sections:
           structure_score += 25  # هر بخش 25 امتیاز
   ```

2. **محاسبه نمره منابع (15%)**:
   ```python
   references_count = len(proposal['sections']['references'])
   
   if references_count >= 20:
       references_score = 100
   elif references_count >= 10:
       references_score = 70
   else:
       references_score = references_count * 5
   ```

3. **محاسبه نمره اصالت (5%)**:
   ```python
   plagiarism_percentage = proposal['plagiarism']['percentage']
   originality_score = max(0, 100 - plagiarism_percentage)
   ```

4. **تجمیع نمره نهایی**:
   ```python
   final_score = (
       writing_score * 0.25 +      # 25%
       structure_score * 0.20 +     # 20%
       content_score * 0.35 +       # 35%
       references_score * 0.15 +    # 15%
       originality_score * 0.05     # 5%
   )
   ```

5. **تولید گزارش JSON**:
   ```python
   report = {
       "final_score": round(final_score, 2),
       "scores": {
           "writing": writing_score,
           "structure": structure_score,
           "content": content_score,
           "references": references_score,
           "originality": originality_score
       },
       "details": {
           "writing": {...},
           "plagiarism": {...},
           "keywords": [...],
           "summary": "...",
           "strengths": [...],
           "weaknesses": [...],
           "suggestions": [...]
       },
       "metadata": {
           "evaluated_at": "2024-...",
           "evaluation_time": "120s"
       }
   }
   ```

#### خروجی:
- گزارش JSON کامل و ساختاریافته
- نمره نهایی با تفکیک هر بخش

---

### **گام 6: توسعه REST API با FastAPI (100 ساعت)**
**تاریخ**: 30 دی - 5 بهمن

#### فعالیت‌ها:

1. **ساختار API**:
   ```python
   from fastapi import FastAPI, UploadFile, File
   from fastapi.responses import JSONResponse
   
   app = FastAPI(title="Proposal Evaluation API", version="1.0")
   
   @app.post("/api/evaluate")
   async def evaluate_proposal(file: UploadFile = File(...)):
       # 1. ذخیره فایل موقت
       # 2. استخراج متن
       # 3. پیش‌پردازش
       # 4. ارزیابی NLP
       # 5. تشخیص تقلب
       # 6. تحلیل LLM
       # 7. امتیازدهی
       # 8. برگرداندن گزارش
       
       return JSONResponse(content=report)
   
   @app.get("/api/health")
   async def health_check():
       return {"status": "healthy"}
   ```

2. **مدیریت خطاها**:
   ```python
   from fastapi import HTTPException
   
   try:
       result = process_proposal(file)
   except Exception as e:
       raise HTTPException(status_code=500, detail=str(e))
   ```

3. **مستندسازی خودکار**:
   - Swagger UI در `/docs`
   - ReDoc در `/redoc`

#### خروجی:
- API کامل و کاربردی
- مستندات Swagger

#### تست API:
```bash
curl -X POST "http://localhost:8000/api/evaluate" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@proposal.pdf"
```

---

### **گام 7: تست، یکپارچگی و بهینه‌سازی عملکرد (100 ساعت)**
**تاریخ**: 6 بهمن - 9 بهمن (کوتاه‌تر شده)

#### فعالیت‌ها:

1. **ساخت رابط Streamlit**:
   ```python
   import streamlit as st
   
   st.title("🎯 ارزیابی هوشمند پروپوزال")
   
   uploaded_file = st.file_uploader("فایل پروپوزال را آپلود کنید", 
                                     type=['pdf', 'docx'])
   
   if uploaded_file and st.button("ارزیابی"):
       with st.spinner('در حال ارزیابی...'):
           result = evaluate_proposal(uploaded_file)
       
       st.metric("نمره کل", f"{result['final_score']}/100")
       
       col1, col2, col3 = st.columns(3)
       col1.metric("نگارش", result['scores']['writing'])
       col2.metric("محتوا", result['scores']['content'])
       col3.metric("ساختار", result['scores']['structure'])
       
       st.success("✅ نقاط قوت")
       for strength in result['details']['strengths']:
           st.write(f"- {strength}")
       
       st.warning("⚠️ نقاط ضعف")
       for weakness in result['details']['weaknesses']:
           st.write(f"- {weakness}")
   ```

2. **تست واحد (Unit Tests)**:
   ```python
   import pytest
   
   def test_text_extraction():
       result = extract_text_from_pdf("test.pdf")
       assert len(result) > 0
   
   def test_plagiarism_detection():
       similarity = detect_plagiarism("test text")
       assert 0 <= similarity <= 100
   ```

3. **بهینه‌سازی**:
   - Caching نتایج مدل‌ها
   - Quantization مدل LLM برای سرعت بیشتر
   - پردازش موازی در جاهای ممکن

#### خروجی:
- رابط Streamlit کاربردی
- تست‌های پاس شده
- سرعت بهینه

---

### **گام 8: مستندسازی کامل و تحویل نهایی (40 ساعت)**
**تاریخ**: 10 بهمن - 11 بهمن

#### فعالیت‌ها:

1. **مستندات فنی** (`docs/TECHNICAL.md`):
   - معماری کامل
   - توضیح هر ماژول
   - نمودارهای جریان

2. **راهنمای نصب** (`docs/INSTALLATION.md`):
   ```markdown
   # نصب و راه‌اندازی
   
   ## پیش‌نیازها
   - Python 3.10+
   - 16GB RAM
   - GPU (اختیاری)
   
   ## مراحل نصب
   1. Clone کردن repository
   2. ایجاد virtual environment
   3. نصب dependencies
   4. نصب Ollama و دانلود مدل
   5. راه‌اندازی دیتابیس
   6. اجرای سیستم
   ```

3. **راهنمای کاربر** (`docs/USER_GUIDE.md`):
   - نحوه استفاده از API
   - نحوه استفاده از Streamlit
   - نمونه‌های کاربردی

4. **README.md اصلی**:
   - معرفی پروژه
   - ویژگی‌ها
   - نصب سریع
   - نمونه استفاده

#### خروجی:
- مستندات کامل
- کد تمیز و commented
- پروژه آماده تحویل

---

## ✅ چک‌لیست نهایی

قبل از تحویل، مطمئن شو:

### عملکرد
- [ ] استخراج از PDF/Word کار می‌کند
- [ ] تمام ماژول‌های NLP عملکرد صحیح دارند
- [ ] تشخیص تقلب دقیق کار می‌کند
- [ ] LLM پاسخ‌های معنادار می‌دهد
- [ ] امتیازدهی طبق وزن‌های تعیین شده است (25-20-35-15-5)
- [ ] API بدون خطا کار می‌کند
- [ ] Streamlit قابل استفاده است

### کیفیت کد
- [ ] کد clean و readable است
- [ ] توضیحات (comments) کافی دارد
- [ ] تست‌های واحد نوشته شده
- [ ] خطاها مدیریت می‌شوند

### آفلاین بودن
- [ ] هیچ API خارجی استفاده نشده
- [ ] LLM به صورت local اجرا می‌شود
- [ ] تمام مدل‌ها دانلود و ذخیره شده‌اند

### مستندات
- [ ] README کامل است
- [ ] راهنمای نصب دقیق است
- [ ] مستندات فنی جامع است
- [ ] API documentation (Swagger) کامل است

---

## 🎯 معیارهای موفقیت کلی

1. **دقت ارزیابی**: نمرات تولید شده منطقی و قابل دفاع باشند
2. **سرعت**: ارزیابی یک پروپوزال 20 صفحه‌ای کمتر از 3 دقیقه
3. **پایداری**: سیستم بدون خطا 100 پروپوزال را ارزیابی کند
4. **فارسی**: تمام قابلیت‌ها روی متن فارسی کار کنند
5. **آفلاین**: بدون اتصال اینترنت کار کند

---

## 🚨 نکات حیاتی برای پیاده‌سازی

1. **از همان ابتدا modular بنویس** - هر ماژول مستقل باشد
2. **همیشه تست کن** - بعد از هر گام تست کامل انجام بده
3. **مستندسازی همزمان** - همزمان با کدنویسی، مستند بنویس
4. **نمونه داده داشته باش** - حداقل 10 پروپوزال نمونه برای تست
5. **وزن‌های امتیازدهی ثابت است** - 25-20-35-15-5 تغییر نکند
6. **خروجی JSON باید ساختار ثابت داشته باشد**
7. **LLM باید temperature=0 داشته باشد** برای یکنواختی

---

## 📚 منابع مفید

- [Hazm Documentation](https://github.com/roshan-research/hazm)
- [ParsBERT Model](https://huggingface.co/HooshvareLab/bert-fa-base-uncased)
- [Ollama Documentation](https://ollama.ai/docs)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 📞 در صورت مشکل

اگر در هر گام به مشکل خوردی:
1. ابتدا لاگ‌ها را بررسی کن
2. مطمئن شو تمام dependency‌ها نصب شده‌اند
3. ورژن‌های Python و پکیج‌ها را چک کن
4. مدل‌های LLM را دوباره دانلود کن
5. دیتابیس را reset کن و دوباره بساز

**موفق باشید! 🚀**

