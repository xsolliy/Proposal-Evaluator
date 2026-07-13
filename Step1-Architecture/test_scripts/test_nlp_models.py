"""
تست مدل‌های NLP فارسی
"""
import time
import numpy as np

def test_sentence_bert():
    """تست Persian Sentence-BERT"""
    print("=" * 60)
    print("1️⃣  تست Persian Sentence-BERT")
    print("=" * 60)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        print("\n🔄 بارگذاری مدل...")
        start_time = time.time()
        
        model = SentenceTransformer('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
        
        load_time = time.time() - start_time
        print(f"✅ مدل بارگذاری شد (زمان: {load_time:.2f} ثانیه)")
        
        # تست embedding
        texts = [
            "این پروپوزال درباره یادگیری ماشین است",
            "این تحقیق به هوش مصنوعی می‌پردازد",
            "من امروز به فروشگاه رفتم"
        ]
        
        print("\n📝 متن‌های تست:")
        for i, text in enumerate(texts, 1):
            print(f"   {i}. {text}")
        
        print("\n🔄 محاسبه embeddings...")
        embeddings = model.encode(texts)
        
        print(f"✅ Embeddings محاسبه شد")
        print(f"   Shape: {embeddings.shape}")
        print(f"   Expected: (3, 768) ✅" if embeddings.shape == (3, 768) else "   ⚠️  Shape غیرمنتظره")
        
        # محاسبه شباهت
        print("\n📊 محاسبه شباهت‌ها:")
        similarity_matrix = cosine_similarity(embeddings)
        
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                sim = similarity_matrix[i][j] * 100
                print(f"   متن {i+1} و متن {j+1}: {sim:.2f}%")
        
        print("\n✅ تست Sentence-BERT موفق")
        return True
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        print("\n💡 راهنما:")
        print("   pip install sentence-transformers")
        return False

def test_keybert():
    """تست KeyBERT برای استخراج کلمات کلیدی"""
    print("\n" + "=" * 60)
    print("2️⃣  تست KeyBERT")
    print("=" * 60)
    
    try:
        from keybert import KeyBERT
        
        print("\n🔄 بارگذاری مدل...")
        kw_model = KeyBERT('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
        print("✅ مدل بارگذاری شد")
        
        text = """
        این پژوهش به بررسی کاربرد یادگیری عمیق در پردازش زبان طبیعی فارسی می‌پردازد.
        هدف اصلی، طراحی یک سیستم هوشمند برای تحلیل احساسات متون فارسی است.
        روش‌شناسی شامل استفاده از شبکه‌های عصبی پیچشی و شبکه‌های بازگشتی است.
        """
        
        print("\n📝 متن تست:")
        print(text.strip())
        
        print("\n🔄 استخراج کلمات کلیدی...")
        keywords = kw_model.extract_keywords(
            text, 
            keyphrase_ngram_range=(1, 2),
            top_n=10
        )
        
        print("\n🔑 کلمات کلیدی استخراج شده:")
        for i, (keyword, score) in enumerate(keywords, 1):
            print(f"   {i:2}. {keyword:40} (امتیاز: {score:.4f})")
        
        print("\n✅ تست KeyBERT موفق")
        return True
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        print("\n💡 راهنما:")
        print("   pip install keybert")
        return False

def test_hazm():
    """تست Hazm برای پردازش فارسی"""
    print("\n" + "=" * 60)
    print("3️⃣  تست Hazm")
    print("=" * 60)
    
    try:
        from hazm import Normalizer, word_tokenize, sent_tokenize
        
        text = """
        اين متن براي تست است. ما مي خواهيم آن را نرمال كنيم.
        حتماً باید نیم‌فاصله ها هم درست شود.
        """
        
        print("\n📝 متن اصلی:")
        print(text.strip())
        
        # نرمال‌سازی
        print("\n🔄 نرمال‌سازی...")
        normalizer = Normalizer()
        normalized = normalizer.normalize(text)
        
        print("✅ متن نرمال شده:")
        print(normalized.strip())
        
        # توکن‌سازی کلمه
        print("\n🔄 توکن‌سازی کلمات...")
        words = word_tokenize(normalized)
        print(f"✅ تعداد کلمات: {len(words)}")
        print(f"   نمونه: {words[:15]}")
        
        # توکن‌سازی جمله
        print("\n🔄 توکن‌سازی جملات...")
        sentences = sent_tokenize(normalized)
        print(f"✅ تعداد جملات: {len(sentences)}")
        for i, sent in enumerate(sentences, 1):
            print(f"   {i}. {sent.strip()}")
        
        print("\n✅ تست Hazm موفق")
        return True
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        print("\n💡 راهنما:")
        print("   pip install hazm")
        return False

def test_plagiarism_simulation():
    """شبیه‌سازی تشخیص تقلب"""
    print("\n" + "=" * 60)
    print("4️⃣  شبیه‌سازی تشخیص تقلب")
    print("=" * 60)
    
    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.metrics.pairwise import cosine_similarity
        
        print("\n🔄 بارگذاری مدل...")
        model = SentenceTransformer('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
        
        # پروپوزال جدید
        new_proposal = "این پژوهش به بررسی یادگیری ماشین در پردازش زبان فارسی می‌پردازد"
        
        # پروپوزال‌های موجود در دیتابیس (فرضی)
        existing_proposals = [
            "تحقیق درباره یادگیری عمیق و پردازش زبان طبیعی فارسی",
            "کاربرد هوش مصنوعی در تحلیل داده‌های بزرگ",
            "بررسی معماری میکروسرویس در سیستم‌های توزیع شده"
        ]
        
        print("\n📝 پروپوزال جدید:")
        print(f"   {new_proposal}")
        
        print("\n📚 پروپوزال‌های موجود:")
        for i, prop in enumerate(existing_proposals, 1):
            print(f"   {i}. {prop}")
        
        print("\n🔄 محاسبه embeddings...")
        new_embedding = model.encode([new_proposal])
        existing_embeddings = model.encode(existing_proposals)
        
        print("\n🔄 محاسبه شباهت...")
        similarities = cosine_similarity(new_embedding, existing_embeddings)[0]
        
        print("\n📊 نتایج:")
        for i, sim in enumerate(similarities, 1):
            sim_percent = sim * 100
            status = "⚠️  مشکوک" if sim_percent > 70 else "✅ قابل قبول"
            print(f"   پروپوزال {i}: {sim_percent:.2f}% {status}")
        
        max_similarity = max(similarities) * 100
        print(f"\n📈 بیشترین شباهت: {max_similarity:.2f}%")
        
        originality = 100 - max_similarity
        print(f"🎯 نمره اصالت: {originality:.2f}/100")
        
        print("\n✅ شبیه‌سازی تشخیص تقلب موفق")
        return True
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        return False

def main():
    """اجرای تمام تست‌ها"""
    print("\n🚀 شروع تست‌های مدل‌های NLP فارسی")
    print("=" * 60)
    
    results = {
        "Sentence-BERT": False,
        "KeyBERT": False,
        "Hazm": False,
        "Plagiarism": False
    }
    
    # تست‌ها
    results["Sentence-BERT"] = test_sentence_bert()
    results["KeyBERT"] = test_keybert()
    results["Hazm"] = test_hazm()
    results["Plagiarism"] = test_plagiarism_simulation()
    
    # خلاصه
    print("\n" + "=" * 60)
    print("📊 خلاصه نتایج")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✅ موفق" if success else "❌ ناموفق"
        print(f"   {name:20} {status}")
    
    all_success = all(results.values())
    
    if all_success:
        print("\n✅ تمام تست‌ها موفق بودند!")
        print("✅ مدل‌های NLP آماده استفاده هستند")
        print("✅ می‌توانید به پیاده‌سازی بروید")
    else:
        print("\n⚠️  برخی تست‌ها ناموفق بودند")
        print("💡 لطفاً مدل‌های ناموفق را نصب کنید")

if __name__ == "__main__":
    main()













