# 📑 گزارش جامع گام سوم: توسعه ماژول‌های NLP و تشخیص تقلب

## مشخصات پروژه

| **عنوان پروژه** | سیستم ارزیابی هوشمند پروپوزال‌های فارسی |
|-----------------|------------------------------------------|
| **گام** | گام 3: توسعه ماژول‌های NLP و تشخیص تقلب |
| **تاریخ شروع** | 7 آذر 1404 |
| **تاریخ اتمام** | 27 آذر 1404 |
| **مدت** | 180 ساعت |
| **وضعیت** | ✅ تکمیل شده |

---

## 📋 فهرست مطالب

1. [خلاصه اجرایی](#1-خلاصه-اجرایی)
2. [اهداف و تعهدات](#2-اهداف-و-تعهدات)
3. [معماری ماژول‌ها](#3-معماری-ماژولها)
4. [پیاده‌سازی NLP](#4-پیادهسازی-nlp)
5. [پیاده‌سازی تشخیص تقلب](#5-پیادهسازی-تشخیص-تقلب)
6. [ارزیابی و نتیجه‌گیری](#6-ارزیابی-و-نتیجهگیری)

---

## 1. خلاصه اجرایی

### 1.1 مقدمه

در این گام، دو ماژول اصلی پیاده‌سازی شد:
- **ماژول NLP**: بررسی نگارشی، استخراج کلیدواژه، خلاصه‌سازی و محاسبه نمره نگارشی (25%)
- **ماژول تشخیص تقلب**: تبدیل به embedding، محاسبه شباهت و نمره اصالت (5%)

### 1.2 دستاوردهای کلیدی

| بخش | ماژول | وضعیت | توضیح |
|-----|-------|--------|-------|
| **NLP** | GrammarChecker | ✅ | بررسی املا و گرامر فارسی |
| **NLP** | KeywordExtractor | ✅ | استخراج کلیدواژه با KeyBERT |
| **NLP** | TextSummarizer | ✅ | خلاصه‌سازی extractive |
| **NLP** | TextStatistics | ✅ | آمار متنی پیشرفته |
| **NLP** | WritingScorer | ✅ | محاسبه نمره نگارشی (25%) |
| **Plagiarism** | TextEmbedder | ✅ | تبدیل به embedding |
| **Plagiarism** | SimilarityChecker | ✅ | محاسبه شباهت |
| **Plagiarism** | PlagiarismDetector | ✅ | تشخیص یکپارچه تقلب |

### 1.3 ساختار خروجی

```
Step3-NLP-Plagiarism/
├── STEP3_REPORT.md               ← این گزارش
├── requirements.txt
└── src/
    ├── nlp/
    │   ├── __init__.py
    │   ├── grammar_checker.py    ← بررسی املا و گرامر (340 خط)
    │   ├── keyword_extractor.py  ← استخراج کلیدواژه (330 خط)
    │   ├── summarizer.py         ← خلاصه‌سازی (310 خط)
    │   ├── text_statistics.py    ← آمار متنی (290 خط)
    │   └── writing_scorer.py     ← نمره نگارشی (280 خط)
    └── plagiarism/
        ├── __init__.py
        ├── embedder.py           ← تبدیل به embedding (270 خط)
        ├── similarity_checker.py ← بررسی شباهت (320 خط)
        └── plagiarism_detector.py← تشخیص تقلب (300 خط)
```

**کل خطوط کد**: ~2,440 خط

---

## 2. اهداف و تعهدات

### 2.1 تعهدات گام سوم (طبق پروپوزال)

| # | فعالیت | وضعیت | جزئیات |
|---|--------|--------|--------|
| **بخش A** | بررسی نگارشی (60 ساعت) | ✅ | |
| A.1 | بررسی املا و گرامر | ✅ | GrammarChecker |
| A.2 | تحلیل‌های آماری | ✅ | TextStatistics |
| A.3 | محاسبه نمره نگارشی | ✅ | WritingScorer (25%) |
| **بخش B** | استخراج اطلاعات (60 ساعت) | ✅ | |
| B.1 | استخراج کلمات کلیدی | ✅ | KeywordExtractor + KeyBERT |
| B.2 | خلاصه‌سازی متن | ✅ | TextSummarizer |
| **بخش C** | تشخیص تقلب (60 ساعت) | ✅ | |
| C.1 | تبدیل به Embeddings | ✅ | TextEmbedder + Sentence-BERT |
| C.2 | محاسبه Cosine Similarity | ✅ | SimilarityChecker |
| C.3 | ذخیره در Database | ✅ | PlagiarismDetector |

### 2.2 خروجی‌های مورد انتظار

طبق پروپوزال، خروجی این گام باید ساختار زیر باشد:

```python
# خروجی مورد انتظار
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

**وضعیت**: ✅ همه موارد پیاده‌سازی شد

### 2.3 معیارهای موفقیت

| معیار | هدف | نتیجه | وضعیت |
|-------|------|-------|--------|
| تشخیص تشابه بالای 80% | با دقت | ✅ Cosine Similarity | ✅ |
| استخراج 10 کلیدواژه | حداقل 10 | 15 کلیدواژه | ✅ |
| نمره نگارشی | 25% از کل | محاسبه شد | ✅ |
| نمره اصالت | 5% از کل | محاسبه شد | ✅ |

---

## 3. معماری ماژول‌ها

### 3.1 دیاگرام کلی

```
┌───────────────────────────────────────────────────────────────┐
│                     Preprocessed Text                         │
│                   (از گام 2)                                  │
└─────────────────────────┬─────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│     NLP Module      │         │  Plagiarism Module  │
│       (25%)         │         │       (5%)          │
├─────────────────────┤         ├─────────────────────┤
│ • GrammarChecker    │         │ • TextEmbedder      │
│ • KeywordExtractor  │         │ • SimilarityChecker │
│ • TextSummarizer    │         │ • PlagiarismDetector│
│ • TextStatistics    │         │                     │
│ • WritingScorer     │         │                     │
└─────────┬───────────┘         └─────────┬───────────┘
          │                               │
          ▼                               ▼
┌─────────────────────┐         ┌─────────────────────┐
│   Writing Score     │         │  Originality Score  │
│     (0-100)         │         │      (0-100)        │
│    Weight: 25%      │         │     Weight: 5%      │
└─────────────────────┘         └─────────────────────┘
```

### 3.2 جریان داده NLP

```
[Normalized Text]
      │
      ├─────────────────────────────────────────┐
      │                                         │
      ▼                                         ▼
┌─────────────┐                         ┌─────────────┐
│ Grammar     │                         │ Keyword     │
│ Checker     │                         │ Extractor   │
├─────────────┤                         ├─────────────┤
│ • Spelling  │                         │ • KeyBERT   │
│ • Grammar   │                         │ • TF-IDF    │
│ • Half-space│                         │             │
└──────┬──────┘                         └──────┬──────┘
       │                                       │
       ▼                                       ▼
┌─────────────┐                         ┌─────────────┐
│ Text Stats  │                         │ Summarizer  │
├─────────────┤                         ├─────────────┤
│ • Word count│                         │ • Extractive│
│ • Diversity │                         │ • Scoring   │
│ • Readability                         │ • Top N     │
└──────┬──────┘                         └──────┬──────┘
       │                                       │
       └───────────────┬───────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Writing Scorer  │
              ├─────────────────┤
              │ Spelling: 40%   │
              │ Grammar: 30%    │
              │ Readability: 30%│
              └────────┬────────┘
                       │
                       ▼
              [Writing Score: 0-100]
                 (Weight: 25%)
```

### 3.3 جریان داده تشخیص تقلب

```
[Normalized Text]
      │
      ▼
┌─────────────────────┐
│   TextEmbedder      │
│ (Sentence-BERT)     │
├─────────────────────┤
│ Input: Text         │
│ Output: Vector(768) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ SimilarityChecker   │
│ (Cosine Similarity) │
├─────────────────────┤
│ Compare with DB     │
│ Find similar docs   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ PlagiarismDetector  │
├─────────────────────┤
│ Max similarity      │
│ Similar documents   │
│ Originality score   │
│ Store in database   │
└──────────┬──────────┘
           │
           ▼
[Originality Score: 0-100]
     (Weight: 5%)
```

---

## 4. پیاده‌سازی NLP

### 4.1 GrammarChecker (بررسی املا و گرامر)

**فایل**: `grammar_checker.py` (340 خط)

#### قابلیت‌ها:

```python
class GrammarChecker:
    def check(self, text: str) -> Dict:
        """بررسی کامل متن"""
    
    def correct_text(self, text: str) -> str:
        """اصلاح خودکار خطاها"""
```

#### اشتباهات رایج شناسایی شده:

| نادرست | صحیح | نوع |
|--------|------|-----|
| میشود | می‌شود | نیم‌فاصله |
| بعلت | به علت | فاصله |
| همانطور | همان‌طور | نیم‌فاصله |
| ك | ک | عربی به فارسی |
| ي | ی | عربی به فارسی |

#### خروجی نمونه:

```python
{
    'spelling_errors': [
        {'word': 'میشود', 'suggestion': 'می‌شود', 'position': 45}
    ],
    'grammar_errors': [
        {'text': ' ،', 'message': 'فاصله اضافی قبل از علامت'}
    ],
    'half_space_errors': [...],
    'spelling_error_count': 5,
    'grammar_error_count': 3,
    'spelling_accuracy': 97.5,
    'grammar_score': 85.0,
    'suggestions': ['تعداد 5 خطای املایی یافت شد...']
}
```

### 4.2 KeywordExtractor (استخراج کلیدواژه)

**فایل**: `keyword_extractor.py` (330 خط)

#### قابلیت‌ها:

```python
class KeywordExtractor:
    def extract(self, text: str, top_n: int = 15) -> Dict:
        """استخراج کلیدواژه‌های برتر"""
    
    def extract_from_sections(self, sections: Dict) -> Dict:
        """استخراج از هر بخش جداگانه"""
    
    def get_combined_keywords(self, section_keywords: Dict) -> List:
        """ترکیب با وزن‌دهی"""
```

#### روش‌های استخراج:

1. **KeyBERT** (پیش‌فرض): با مدل فارسی Sentence-BERT
2. **Statistical**: روش TF برای زمانی که KeyBERT در دسترس نیست

#### خروجی نمونه:

```python
{
    'keywords': [
        ('یادگیری ماشین', 0.92),
        ('پردازش زبان طبیعی', 0.88),
        ('شبکه عصبی', 0.85),
        ('تحلیل احساسات', 0.82),
        ...
    ],
    'top_keywords': ['یادگیری ماشین', 'پردازش زبان طبیعی', ...],
    'method': 'KeyBERT',
    'keyword_count': 15
}
```

### 4.3 TextSummarizer (خلاصه‌سازی)

**فایل**: `summarizer.py` (310 خط)

#### قابلیت‌ها:

```python
class TextSummarizer:
    def summarize(self, text: str, num_sentences: int = 5) -> Dict:
        """خلاصه‌سازی extractive"""
    
    def summarize_sections(self, sections: Dict) -> Dict:
        """خلاصه‌سازی هر بخش"""
```

#### الگوریتم امتیازدهی جملات:

| معیار | وزن | توضیح |
|-------|-----|-------|
| فراوانی کلمات (TF) | 30% | جملات با کلمات پرتکرار |
| موقعیت | 20% | جملات اول و آخر مهم‌ترند |
| طول جمله | 15% | 10-30 کلمه ایده‌آل |
| کلمات سیگنال | 25% | نتیجه، مهم، اصلی، ... |
| حضور اعداد | 10% | آمار و ارقام |

#### خروجی نمونه:

```python
{
    'summary': 'خلاصه متن...',
    'sentences': ['جمله 1', 'جمله 2', 'جمله 3'],
    'sentence_scores': [(جمله, امتیاز), ...],
    'compression_ratio': 0.35,
    'original_sentences': 15,
    'summary_sentences': 5
}
```

### 4.4 TextStatistics (آمار متنی)

**فایل**: `text_statistics.py` (290 خط)

#### آمارهای محاسبه شده:

| دسته | آمار |
|------|------|
| **پایه** | تعداد کاراکتر، کلمه، جمله، پاراگراف |
| **میانگین** | طول کلمات، طول جملات |
| **تنوع واژگانی** | TTR، Hapax Legomena، تراکم محتوا |
| **خوانایی** | نمره و سطح خوانایی |
| **توزیع** | کلمات پرتکرار، توزیع طول جملات |

#### محاسبه خوانایی (فرمول سفارشی فارسی):

```python
word_penalty = abs(avg_word_length - 4.5) * 5
sentence_penalty = abs(avg_sentence_length - 17) * 2
std_bonus = min(sentence_length_std * 2, 10)

readability_score = 100 - word_penalty - sentence_penalty + std_bonus
```

**سطح‌بندی**:
- ≥80: بسیار آسان
- ≥60: آسان
- ≥40: متوسط
- ≥20: سخت
- <20: بسیار سخت

### 4.5 WritingScorer (نمره نگارشی)

**فایل**: `writing_scorer.py` (280 خط)

#### فرمول نمره نگارشی:

```python
writing_score = (
    spelling_score * 0.40 +    # 40%
    grammar_score * 0.30 +     # 30%
    readability_score * 0.30   # 30%
)

# نمره نهایی در کل پروپوزال
final_contribution = writing_score * 0.25  # 25% از کل
```

#### درجه‌بندی:

| نمره | درجه |
|------|------|
| ≥95 | عالی |
| ≥80 | خوب |
| ≥60 | متوسط |
| ≥40 | ضعیف |
| <40 | نیاز به بازنگری |

#### خروجی کامل:

```python
{
    'final_score': 85.5,
    'grade': 'خوب',
    'spelling_score': 90.0,
    'grammar_score': 82.0,
    'readability_score': 78.0,
    'weights': {'spelling': 0.4, 'grammar': 0.3, 'readability': 0.3},
    'details': {
        'spelling_errors': 5,
        'grammar_errors': 3,
        'half_space_errors': 8,
        'readability_level': 'آسان',
        'lexical_diversity': 0.35,
        'avg_sentence_length': 18.5
    },
    'feedback': [
        '✅ املای متن بسیار خوب است.',
        '⚠️ 8 مورد استفاده نادرست از نیم‌فاصله.',
        '✅ خوانایی متن آسان است.'
    ]
}
```

---

## 5. پیاده‌سازی تشخیص تقلب

### 5.1 TextEmbedder (تبدیل به Embedding)

**فایل**: `embedder.py` (270 خط)

#### مدل:

```python
model = 'm3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens'
dimension = 768
```

#### قابلیت‌ها:

```python
class TextEmbedder:
    def embed(self, text: str) -> Dict:
        """تبدیل یک متن"""
    
    def embed_batch(self, texts: List[str]) -> Dict:
        """تبدیل دسته‌ای"""
    
    def embed_sections(self, sections: Dict) -> Dict:
        """embedding هر بخش"""
    
    def get_combined_embedding(self, sections: Dict) -> np.ndarray:
        """ترکیب با وزن‌دهی"""
```

#### خروجی:

```python
{
    'embedding': numpy.ndarray(768,),  # بردار 768 بعدی
    'dimension': 768,
    'text_hash': 'sha256...',
    'model': 'bert-fa-...',
    'success': True
}
```

### 5.2 SimilarityChecker (محاسبه شباهت)

**فایل**: `similarity_checker.py` (320 خط)

#### روش:

```python
# Cosine Similarity
from sklearn.metrics.pairwise import cosine_similarity

similarity = cosine_similarity(vec1, vec2)
```

#### آستانه‌ها:

| سطح | درصد | توضیح |
|-----|------|-------|
| یکسان | ≥95% | تقریباً کپی |
| بالا | ≥80% | مشکوک به تقلب |
| متوسط | ≥60% | موضوعات مشترک |
| کم | ≥40% | شباهت جزئی |
| بسیار کم | <40% | متفاوت |

#### قابلیت‌ها:

```python
class SimilarityChecker:
    def compare(self, text1: str, text2: str) -> Dict:
        """مقایسه دو متن"""
    
    def compare_with_database(self, text: str, database: List) -> Dict:
        """مقایسه با پایگاه داده"""
    
    def compare_sections(self, sections1: Dict, sections2: Dict) -> Dict:
        """مقایسه بخش به بخش"""
    
    def find_similar_passages(self, text1: str, text2: str) -> List:
        """یافتن بخش‌های مشابه"""
```

### 5.3 PlagiarismDetector (تشخیص یکپارچه)

**فایل**: `plagiarism_detector.py` (300 خط)

#### قابلیت‌ها:

```python
class PlagiarismDetector:
    def check(self, text: str) -> Dict:
        """بررسی تقلب"""
    
    def check_and_store(self, text: str, proposal_id: str) -> Dict:
        """بررسی و ذخیره"""
    
    def add_to_database(self, text: str, proposal_id: str) -> bool:
        """افزودن به پایگاه داده"""
    
    def get_originality_score_weighted(self, score: float) -> float:
        """تبدیل به نمره 5%"""
```

#### محاسبه نمره اصالت:

```python
# نمره اصالت = 100 - حداکثر شباهت
originality_score = 100 - max_similarity

# سهم در نمره کل
final_contribution = originality_score * 0.05  # 5%
```

#### خروجی کامل:

```python
{
    'originality_score': 88.5,
    'plagiarism_percentage': 11.5,
    'is_original': True,
    'max_similarity': 11.5,
    'similar_documents': [
        {'id': 'PROP-001', 'similarity': 11.5, 'level': 'بسیار کم'}
    ],
    'checked_against': 50,
    'warning': None,
    'details': {
        'text_hash': 'abc123...',
        'threshold': 70,
        'checked_at': '2025-12-23T...'
    }
}
```

---

## 6. ارزیابی و نتیجه‌گیری

### 6.1 خلاصه پیاده‌سازی

| ماژول | کلاس | خطوط | وضعیت |
|-------|------|------|--------|
| **NLP** | | | |
| | GrammarChecker | 340 | ✅ |
| | KeywordExtractor | 330 | ✅ |
| | TextSummarizer | 310 | ✅ |
| | TextStatistics | 290 | ✅ |
| | WritingScorer | 280 | ✅ |
| **Plagiarism** | | | |
| | TextEmbedder | 270 | ✅ |
| | SimilarityChecker | 320 | ✅ |
| | PlagiarismDetector | 300 | ✅ |
| **مجموع** | **8 کلاس** | **2,440** | ✅ |

### 6.2 تحقق اهداف

| هدف | وضعیت | توضیح |
|-----|--------|-------|
| بررسی املا و گرامر | ✅ | شناسایی خطاها + اصلاح خودکار |
| استخراج 10+ کلیدواژه | ✅ | KeyBERT + روش آماری |
| خلاصه‌سازی | ✅ | Extractive با امتیازدهی |
| نمره نگارشی 25% | ✅ | فرمول وزنی (40-30-30) |
| تشخیص تقلب با embedding | ✅ | Sentence-BERT فارسی |
| نمره اصالت 5% | ✅ | 100 - max_similarity |

### 6.3 نقاط قوت

1. ✅ **پشتیبانی کامل فارسی**: همه ماژول‌ها برای فارسی بهینه شده‌اند
2. ✅ **مدل‌های آفلاین**: Sentence-BERT فارسی، بدون نیاز به اینترنت
3. ✅ **Fallback هوشمند**: اگر KeyBERT نباشد، روش آماری
4. ✅ **خروجی استاندارد**: همه ماژول‌ها Dict برمی‌گردانند
5. ✅ **بازخورد کاربردی**: پیشنهادات بهبود واضح
6. ✅ **مستندات کامل**: Docstrings + مثال‌ها

### 6.4 وابستگی‌ها

```
hazm==0.7.0
keybert==0.8.3
sentence-transformers==2.2.2
transformers==4.35.0
torch>=2.0.0
scikit-learn==1.3.2
numpy==1.24.3
```

### 6.5 نحوه استفاده

```python
# NLP - نمره نگارشی
from src.nlp import WritingScorer

scorer = WritingScorer()
result = scorer.score(text)
print(f"نمره نگارش: {result['final_score']}/100")
print(f"سهم در کل: {result['final_score'] * 0.25:.2f}/25")

# تشخیص تقلب
from src.plagiarism import PlagiarismDetector

detector = PlagiarismDetector(threshold=70)
result = detector.check(text)
print(f"نمره اصالت: {result['originality_score']}/100")
print(f"سهم در کل: {result['originality_score'] * 0.05:.2f}/5")
```

### 6.6 آمادگی برای گام 4

این ماژول‌ها خروجی استاندارد تولید می‌کنند که مستقیماً در گام 4 (LLM) و گام 5 (Scoring) استفاده می‌شوند:

```python
# خروجی گام 3 → ورودی گام 5
{
    'writing_score': 85.5,      # → Weight: 25%
    'originality_score': 92.0,  # → Weight: 5%
    'keywords': [...],          # → برای LLM
    'summary': '...'            # → برای گزارش
}
```

---

## 7. نتیجه‌گیری نهایی

گام سوم پروژه با موفقیت کامل شد. 8 کلاس در 2,440 خط کد Python پیاده‌سازی شد که شامل:

### ماژول NLP (30% از نمره کل):
- ✅ نمره نگارشی (25%)
- ✅ استخراج کلیدواژه
- ✅ خلاصه‌سازی
- ✅ آمار متنی

### ماژول تشخیص تقلب (5% از نمره کل):
- ✅ تبدیل به embedding
- ✅ محاسبه شباهت
- ✅ مدیریت پایگاه داده

### خلاصه نمرات:

```
نمره نهایی = (نگارش × 0.25) + (ساختار × 0.20) + (محتوا × 0.35) + 
             (منابع × 0.15) + (اصالت × 0.05)

گام 3 پوشش داد:
  ✅ نگارش: 25%
  ✅ اصالت: 5%
  ───────────────
  جمع: 30% از نمره کل
```

**آماده شروع گام 4** (یکپارچه‌سازی LLM) ✅

---

**پایان گزارش گام سوم** ✅

**تاریخ**: 23 دسامبر 2025  
**خطوط کد**: 2,440  
**کلاس‌ها**: 8  
**وضعیت**: 🟢 تکمیل و آماده استفاده

