"""
دانلود و آماده‌سازی تمام مدل‌های NLP
"""
import os

def download_sentence_bert():
    """دانلود Persian Sentence-BERT"""
    print("=" * 60)
    print("1️⃣  دانلود Persian Sentence-BERT")
    print("=" * 60)
    
    try:
        from sentence_transformers import SentenceTransformer
        
        print("\n🔄 در حال دانلود...")
        print("⏳ این ممکن است چند دقیقه طول بکشد...")
        
        model = SentenceTransformer('m3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens')
        
        print("✅ دانلود موفق")
        print(f"📁 محل ذخیره: {os.path.expanduser('~/.cache/huggingface')}")
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def download_parsbert():
    """دانلود ParsBERT"""
    print("\n" + "=" * 60)
    print("2️⃣  دانلود ParsBERT")
    print("=" * 60)
    
    try:
        from transformers import AutoTokenizer, AutoModel
        
        print("\n🔄 در حال دانلود...")
        
        tokenizer = AutoTokenizer.from_pretrained("HooshvareLab/bert-fa-base-uncased")
        model = AutoModel.from_pretrained("HooshvareLab/bert-fa-base-uncased")
        
        print("✅ دانلود موفق")
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return False

def check_ollama_models():
    """بررسی مدل‌های Ollama"""
    print("\n" + "=" * 60)
    print("3️⃣  بررسی مدل‌های Ollama")
    print("=" * 60)
    
    try:
        import ollama
        
        models = ollama.list()
        installed = [m['name'] for m in models.get('models', [])]
        
        print("\n📦 مدل‌های نصب شده:")
        if installed:
            for m in installed:
                print(f"   ✅ {m}")
        else:
            print("   ⚠️  هیچ مدلی نصب نشده")
        
        # بررسی مدل‌های پیشنهادی
        print("\n📋 مدل‌های پیشنهادی:")
        recommended = ['llama3.1:8b', 'qwen2.5:7b']
        
        for rec in recommended:
            if any(rec in m for m in installed):
                print(f"   ✅ {rec} - نصب شده")
            else:
                print(f"   ⚠️  {rec} - نصب نشده")
                print(f"      دانلود: ollama pull {rec}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        print("\n💡 Ollama نصب نشده است")
        print("   دانلود از: https://ollama.ai")
        return False

def main():
    """دانلود تمام مدل‌ها"""
    print("\n🚀 دانلود مدل‌های NLP فارسی")
    print("=" * 60)
    
    print("\n⚠️  توجه:")
    print("   • حجم دانلود: ~2-3 GB")
    print("   • زمان: 10-30 دقیقه (بسته به سرعت اینترنت)")
    print("   • فضای دیسک: حداقل 5 GB آزاد")
    
    response = input("\n❓ ادامه می‌دهید؟ (y/n): ")
    
    if response.lower() != 'y':
        print("❌ لغو شد")
        return
    
    # دانلود مدل‌ها
    results = {}
    
    results['Sentence-BERT'] = download_sentence_bert()
    results['ParsBERT'] = download_parsbert()
    results['Ollama'] = check_ollama_models()
    
    # خلاصه
    print("\n" + "=" * 60)
    print("📊 خلاصه دانلود")
    print("=" * 60)
    
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
    
    if all(results.values()):
        print("\n✅ تمام مدل‌ها آماده هستند!")
    else:
        print("\n⚠️  برخی مدل‌ها نصب نشدند")
        print("💡 دستورات نصب را دنبال کنید")
    
    # راهنمای نصب Ollama
    if not results['Ollama']:
        print("\n" + "=" * 60)
        print("📝 راهنمای نصب Ollama")
        print("=" * 60)
        print("\nWindows:")
        print("   https://ollama.ai/download/windows")
        print("\nLinux:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("\nmacOS:")
        print("   https://ollama.ai/download/mac")
        print("\nبعد از نصب:")
        print("   ollama pull llama3.1:8b")

if __name__ == "__main__":
    main()













