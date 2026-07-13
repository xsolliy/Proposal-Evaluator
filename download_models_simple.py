#!/usr/bin/env python3
"""
دانلود مدل‌های مورد نیاز برای سیستم ارزیابی پروپوزال
"""

import os
from pathlib import Path
import subprocess
import sys

def install_package(package):
    """نصب پکیج با pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} نصب شد")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ خطا در نصب {package}")
        return False

def download_huggingface_model(model_name, save_path=None):
    """دانلود مدل از Hugging Face"""
    try:
        from transformers import AutoTokenizer, AutoModel
        print(f"📥 در حال دانلود مدل: {model_name}")
        
        if save_path:
            tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=save_path)
            model = AutoModel.from_pretrained(model_name, cache_dir=save_path)
        else:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModel.from_pretrained(model_name)
        
        print(f"✅ مدل {model_name} با موفقیت دانلود شد")
        return True
    except Exception as e:
        print(f"❌ خطا در دانلود {model_name}: {e}")
        return False

def download_sentence_transformer(model_name):
    """دانلود Sentence Transformer"""
    try:
        from sentence_transformers import SentenceTransformer
        print(f"📥 در حال دانلود Sentence Transformer: {model_name}")
        
        model = SentenceTransformer(model_name)
        print(f"✅ مدل {model_name} با موفقیت دانلود شد")
        return True
    except Exception as e:
        print(f"❌ خطا در دانلود {model_name}: {e}")
        return False

def main():
    """تابع اصلی"""
    print("=" * 60)
    print("🤖 دانلود مدل‌های مورد نیاز سیستم ارزیابی پروپوزال")
    print("=" * 60)
    
    # ایجاد پوشه مدل‌ها
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    # نصب پکیج‌های مورد نیاز
    print("\n📦 نصب پکیج‌های مورد نیاز...")
    packages = [
        "transformers",
        "sentence-transformers", 
        "torch",
        "numpy",
        "scikit-learn"
    ]
    
    for package in packages:
        install_package(package)
    
    # دانلود مدل‌ها
    print("\n🧠 دانلود مدل‌های NLP...")
    
    models_to_download = [
        {
            "name": "ParsBERT (تحلیل زبان فارسی)",
            "model": "HooshvareLab/bert-fa-base-uncased",
            "type": "huggingface"
        },
        {
            "name": "Sentence-BERT (تشخیص تشابه)",
            "model": "paraphrase-multilingual-MiniLM-L12-v2",
            "type": "sentence_transformer"
        },
        {
            "name": "ParsBERT Distilled (سبک‌تر)",
            "model": "HooshvareLab/bert-fa-zwnj-base",
            "type": "huggingface"
        }
    ]
    
    success_count = 0
    total_count = len(models_to_download)
    
    for model_info in models_to_download:
        print(f"\n📥 {model_info['name']}")
        
        if model_info["type"] == "huggingface":
            if download_huggingface_model(model_info["model"], str(models_dir)):
                success_count += 1
        elif model_info["type"] == "sentence_transformer":
            if download_sentence_transformer(model_info["model"]):
                success_count += 1
    
    # خلاصه
    print("\n" + "=" * 60)
    print(f"📊 خلاصه دانلود: {success_count}/{total_count} مدل با موفقیت دانلود شد")
    
    if success_count == total_count:
        print("✅ تمام مدل‌ها با موفقیت دانلود شدند!")
        print("🎉 سیستم آماده استفاده است")
    else:
        print("⚠️ برخی مدل‌ها دانلود نشدند")
        print("🔄 لطفاً خطاها را بررسی و دوباره تلاش کنید")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
