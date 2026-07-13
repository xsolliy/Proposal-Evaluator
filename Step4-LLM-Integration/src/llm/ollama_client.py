"""
کلاینت Ollama - ارتباط با سرور LLM آفلاین
==========================================

این ماژول ارتباط با سرور Ollama را مدیریت می‌کند.

Classes:
    OllamaClient: کلاینت ارتباط با Ollama

Example:
    >>> client = OllamaClient()
    >>> response = client.generate("سلام")
    >>> print(response)
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Generator
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """تنظیمات Ollama"""
    host: str = "http://localhost"
    port: int = 11434
    model: str = "llama3.1:8b"
    timeout: int = 120
    temperature: float = 0.0  # برای نتایج یکنواخت
    max_tokens: int = 2000
    

class OllamaClient:
    """
    کلاینت ارتباط با سرور Ollama
    
    این کلاس ارتباط HTTP با سرور Ollama را مدیریت می‌کند.
    
    Attributes:
        config (OllamaConfig): تنظیمات اتصال
        base_url (str): آدرس پایه API
        cache (dict): کش پاسخ‌ها
        
    Example:
        >>> client = OllamaClient()
        >>> if client.is_available():
        ...     response = client.generate("تحلیل کن: ...")
        ...     print(response['content'])
    """
    
    # مدل‌های پشتیبانی شده
    SUPPORTED_MODELS = [
        'llama3.1:8b',
        'llama3.1:70b',
        'qwen2.5:7b',
        'qwen2.5:14b',
        'mistral:7b',
        'gemma2:9b'
    ]
    
    def __init__(self, config: OllamaConfig = None):
        """
        مقداردهی اولیه OllamaClient
        
        Args:
            config: تنظیمات Ollama (اختیاری)
        """
        self.config = config or OllamaConfig()
        self.base_url = f"{self.config.host}:{self.config.port}"
        self.cache = {}
        self._session = None
        self._init_session()
    
    def _init_session(self) -> None:
        """راه‌اندازی session HTTP"""
        try:
            import requests
            self._session = requests.Session()
            self._session.headers.update({
                'Content-Type': 'application/json'
            })
            logger.info(f"Session HTTP ایجاد شد: {self.base_url}")
        except ImportError:
            logger.error("requests نصب نیست!")
            self._session = None
    
    def is_available(self) -> bool:
        """
        بررسی در دسترس بودن سرور Ollama
        
        Returns:
            bool: True اگر سرور در دسترس باشد
        """
        if not self._session:
            return False
        
        try:
            response = self._session.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"سرور Ollama در دسترس نیست: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        لیست مدل‌های موجود در سرور
        
        Returns:
            list: لیست نام مدل‌ها
        """
        if not self._session:
            return []
        
        try:
            response = self._session.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                return models
            return []
            
        except Exception as e:
            logger.error(f"خطا در دریافت لیست مدل‌ها: {e}")
            return []
    
    def is_model_available(self, model: str = None) -> bool:
        """
        بررسی موجود بودن مدل
        
        Args:
            model: نام مدل (پیش‌فرض: مدل تنظیمات)
            
        Returns:
            bool: True اگر مدل موجود باشد
        """
        model = model or self.config.model
        available_models = self.list_models()
        
        # بررسی با نام کامل یا جزئی
        for m in available_models:
            if model in m or m in model:
                return True
        
        return False
    
    def generate(
        self, 
        prompt: str,
        system_prompt: str = None,
        temperature: float = None,
        max_tokens: int = None,
        use_cache: bool = True
    ) -> Dict:
        """
        تولید پاسخ از LLM
        
        Args:
            prompt: پرامپت اصلی
            system_prompt: پرامپت سیستم
            temperature: دمای تولید
            max_tokens: حداکثر توکن
            use_cache: استفاده از کش
            
        Returns:
            dict: پاسخ LLM
            {
                'content': str,
                'model': str,
                'tokens': int,
                'duration': float,
                'success': bool,
                'cached': bool
            }
        """
        if not self._session:
            return self._error_response("Session HTTP موجود نیست")
        
        # بررسی کش
        cache_key = self._get_cache_key(prompt, system_prompt)
        if use_cache and cache_key in self.cache:
            logger.info("پاسخ از کش برگردانده شد")
            cached = self.cache[cache_key].copy()
            cached['cached'] = True
            return cached
        
        # ساخت payload
        payload = {
            'model': self.config.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': temperature or self.config.temperature,
                'num_predict': max_tokens or self.config.max_tokens
            }
        }
        
        if system_prompt:
            payload['system'] = system_prompt
        
        try:
            start_time = time.time()
            
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.config.timeout
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    'content': data.get('response', ''),
                    'model': data.get('model', self.config.model),
                    'tokens': data.get('eval_count', 0),
                    'duration': round(duration, 2),
                    'success': True,
                    'cached': False,
                    'error': None
                }
                
                # ذخیره در کش
                if use_cache:
                    self.cache[cache_key] = result
                
                return result
            else:
                return self._error_response(
                    f"HTTP Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"خطا در تولید پاسخ: {e}")
            return self._error_response(str(e))
    
    def generate_stream(
        self, 
        prompt: str,
        system_prompt: str = None
    ) -> Generator[str, None, None]:
        """
        تولید پاسخ به صورت streaming
        
        Args:
            prompt: پرامپت
            system_prompt: پرامپت سیستم
            
        Yields:
            str: هر بخش از پاسخ
        """
        if not self._session:
            yield "[Error: Session not available]"
            return
        
        payload = {
            'model': self.config.model,
            'prompt': prompt,
            'stream': True,
            'options': {
                'temperature': self.config.temperature,
                'num_predict': self.config.max_tokens
            }
        }
        
        if system_prompt:
            payload['system'] = system_prompt
        
        try:
            response = self._session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                stream=True,
                timeout=self.config.timeout
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if 'response' in data:
                        yield data['response']
                    if data.get('done', False):
                        break
                        
        except Exception as e:
            logger.error(f"خطا در streaming: {e}")
            yield f"[Error: {e}]"
    
    def chat(
        self, 
        messages: List[Dict[str, str]],
        temperature: float = None
    ) -> Dict:
        """
        مکالمه با LLM
        
        Args:
            messages: لیست پیام‌ها [{'role': 'user', 'content': '...'}]
            temperature: دمای تولید
            
        Returns:
            dict: پاسخ LLM
        """
        if not self._session:
            return self._error_response("Session HTTP موجود نیست")
        
        payload = {
            'model': self.config.model,
            'messages': messages,
            'stream': False,
            'options': {
                'temperature': temperature or self.config.temperature
            }
        }
        
        try:
            start_time = time.time()
            
            response = self._session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.config.timeout
            )
            
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                message = data.get('message', {})
                
                return {
                    'content': message.get('content', ''),
                    'role': message.get('role', 'assistant'),
                    'model': data.get('model', self.config.model),
                    'duration': round(duration, 2),
                    'success': True,
                    'error': None
                }
            else:
                return self._error_response(
                    f"HTTP Error: {response.status_code}"
                )
                
        except Exception as e:
            logger.error(f"خطا در chat: {e}")
            return self._error_response(str(e))
    
    def _get_cache_key(self, prompt: str, system_prompt: str = None) -> str:
        """تولید کلید کش"""
        content = f"{self.config.model}:{system_prompt or ''}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _error_response(self, error: str) -> Dict:
        """ساختار پاسخ خطا"""
        return {
            'content': '',
            'model': self.config.model,
            'tokens': 0,
            'duration': 0,
            'success': False,
            'cached': False,
            'error': error
        }
    
    def clear_cache(self) -> int:
        """پاک کردن کش"""
        count = len(self.cache)
        self.cache.clear()
        return count
    
    def get_stats(self) -> Dict:
        """آمار کلاینت"""
        return {
            'base_url': self.base_url,
            'model': self.config.model,
            'cache_size': len(self.cache),
            'is_available': self.is_available()
        }


# تست ماژول
if __name__ == "__main__":
    client = OllamaClient()
    
    print("=" * 60)
    print("🤖 تست اتصال به Ollama")
    print("=" * 60)
    
    # بررسی دسترسی
    if client.is_available():
        print(f"\n✅ سرور Ollama در دسترس است: {client.base_url}")
        
        # لیست مدل‌ها
        models = client.list_models()
        print(f"\n📋 مدل‌های موجود: {models}")
        
        # تست تولید
        if client.is_model_available():
            print(f"\n🧠 تست تولید با مدل {client.config.model}...")
            
            response = client.generate(
                prompt="سلام! یک جمله کوتاه فارسی بگو.",
                system_prompt="تو یک دستیار فارسی هستی."
            )
            
            if response['success']:
                print(f"\n💬 پاسخ: {response['content']}")
                print(f"⏱️ زمان: {response['duration']}s")
                print(f"📊 توکن: {response['tokens']}")
            else:
                print(f"\n❌ خطا: {response['error']}")
        else:
            print(f"\n⚠️ مدل {client.config.model} موجود نیست")
    else:
        print("\n❌ سرور Ollama در دسترس نیست!")
        print("   لطفاً Ollama را نصب و اجرا کنید:")
        print("   1. دانلود از: https://ollama.ai")
        print("   2. اجرا: ollama serve")
        print("   3. دانلود مدل: ollama pull llama3.1:8b")

