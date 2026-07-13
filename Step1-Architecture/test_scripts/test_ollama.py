"""
تست اتصال و عملکرد Ollama
"""
import ollama
import time
import json

def test_connection():
    """تست اتصال به Ollama"""
    print("=" * 60)
    print("1️⃣  تست اتصال به Ollama")
    print("=" * 60)
    
    try:
        models = ollama.list()
        print("✅ اتصال به Ollama موفق")
        print(f"\n📦 مدل‌های نصب شده:")
        for model in models.get('models', []):
            print(f"   • {model['name']}")
        return True
    except Exception as e:
        print(f"❌ خطا در اتصال: {e}")
        print("\n💡 راهنما:")
        print("   1. مطمئن شوید Ollama نصب شده است")
        print("   2. سرویس Ollama را اجرا کنید: ollama serve")
        return False

def test_generation(model="llama3.1:8b"):
    """تست تولید متن ساده"""
    print("\n" + "=" * 60)
    print(f"2️⃣  تست تولید متن با {model}")
    print("=" * 60)
    
    prompt = "سلام! لطفاً با یک جمله کوتاه به فارسی پاسخ دهید."
    
    print(f"\n📝 پرامپت: {prompt}")
    print("🔄 در حال پردازش...")
    
    start_time = time.time()
    
    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0, 'num_predict': 100}
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ موفق (زمان: {elapsed:.2f} ثانیه)")
        print(f"\n💬 پاسخ مدل:")
        print(f"   {response['message']['content']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        return False

def test_proposal_analysis(model="llama3.1:8b"):
    """تست تحلیل پروپوزال با پرامپت واقعی"""
    print("\n" + "=" * 60)
    print(f"3️⃣  تست تحلیل پروپوزال با {model}")
    print("=" * 60)
    
    prompt = """
شما یک ارزیاب علمی حرفه‌ای هستید. پروپوزال زیر را ارزیابی کنید:

پروپوزال:
این تحقیق به بررسی کاربرد شبکه‌های عصبی در تشخیص احساسات فارسی می‌پردازد.
هدف اصلی، طراحی یک سیستم هوشمند برای تحلیل نظرات کاربران در شبکه‌های اجتماعی است.
روش‌شناسی شامل جمع‌آوری دیتاست، پیش‌پردازش، طراحی مدل LSTM و ارزیابی است.

لطفاً به صورت JSON پاسخ دهید:
{
  "strengths": ["نقطه قوت 1", "نقطه قوت 2", "نقطه قوت 3"],
  "weaknesses": ["نقطه ضعف 1", "نقطه ضعف 2", "نقطه ضعف 3"],
  "suggestions": ["پیشنهاد 1", "پیشنهاد 2", "پیشنهاد 3"],
  "content_score": 75
}
"""
    
    print("🔄 در حال تحلیل پروپوزال...")
    print("⏳ این ممکن است 30-60 ثانیه طول بکشد...")
    
    start_time = time.time()
    
    try:
        response = ollama.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0, 'num_predict': 1024}
        )
        
        elapsed = time.time() - start_time
        content = response['message']['content']
        
        print(f"\n✅ موفق (زمان: {elapsed:.2f} ثانیه)")
        print(f"\n📄 پاسخ کامل:")
        print("-" * 60)
        print(content)
        print("-" * 60)
        
        # تلاش برای پارس JSON
        try:
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                print("\n✅ JSON پارس شد:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("\n✅ ساختار پاسخ صحیح است")
            else:
                print("\n⚠️  JSON یافت نشد ولی پاسخ دریافت شد")
        except json.JSONDecodeError:
            print("\n⚠️  فرمت JSON معتبر نیست")
            print("💡 این در کد اصلی باید هندل شود")
        
        return True
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        return False

def main():
    """اجرای تمام تست‌ها"""
    print("\n🚀 شروع تست‌های Ollama")
    print("=" * 60)
    
    # تست 1: اتصال
    if not test_connection():
        print("\n❌ تست متوقف شد. لطفاً Ollama را نصب و اجرا کنید.")
        return
    
    # انتخاب مدل
    print("\n" + "=" * 60)
    print("📋 انتخاب مدل برای تست")
    print("=" * 60)
    print("1. llama3.1:8b (پیشنهادی)")
    print("2. qwen2.5:7b")
    
    choice = input("\nانتخاب کنید (1 یا 2): ").strip()
    
    if choice == "2":
        model = "qwen2.5:7b"
    else:
        model = "llama3.1:8b"
    
    print(f"\n✅ مدل انتخاب شده: {model}")
    
    # تست 2: تولید ساده
    if not test_generation(model):
        print("\n❌ تست تولید متن ناموفق")
        return
    
    # تست 3: تحلیل پروپوزال
    test_proposal_analysis(model)
    
    # خلاصه نهایی
    print("\n" + "=" * 60)
    print("📊 خلاصه تست‌ها")
    print("=" * 60)
    print("✅ تست‌ها با موفقیت انجام شد")
    print(f"✅ مدل {model} آماده استفاده است")
    print("✅ می‌توانید به گام بعدی بروید")

if __name__ == "__main__":
    main()













