"""
ماژول تبدیل متن به Embedding
============================

این ماژول متن را به بردار عددی (embedding) تبدیل می‌کند.

Classes:
    TextEmbedder: تبدیل‌کننده متن به embedding

Example:
    >>> embedder = TextEmbedder()
    >>> embedding = embedder.embed("متن نمونه")
    >>> print(embedding.shape)  # (768,)
"""

import hashlib
from typing import Dict, List, Optional, Union
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextEmbedder:
    """
    کلاس تبدیل متن به Embedding
    
    این کلاس از مدل Persian Sentence-BERT برای تولید embedding استفاده می‌کند.
    
    Attributes:
        model_name (str): نام مدل
        model: مدل Sentence-BERT
        dimension (int): ابعاد embedding
        
    Example:
        >>> embedder = TextEmbedder()
        >>> result = embedder.embed("این یک متن تست است")
        >>> print(result['embedding'].shape)
    """
    
    # مدل پیش‌فرض فارسی
    DEFAULT_MODEL = 'm3hrdadfi/bert-fa-base-uncased-wikinli-mean-tokens'
    EMBEDDING_DIM = 768
    
    def __init__(self, model_name: str = None, use_gpu: bool = False):
        """
        مقداردهی اولیه TextEmbedder
        
        Args:
            model_name: نام مدل (پیش‌فرض: مدل فارسی)
            use_gpu: استفاده از GPU
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self.use_gpu = use_gpu
        self.model = None
        self.dimension = self.EMBEDDING_DIM
        
        self._load_model()
    
    def _load_model(self) -> None:
        """بارگذاری مدل Sentence-BERT"""
        try:
            from sentence_transformers import SentenceTransformer
            
            device = 'cuda' if self.use_gpu else 'cpu'
            logger.info(f"بارگذاری مدل: {self.model_name}")
            
            self.model = SentenceTransformer(self.model_name, device=device)
            
            # تست ابعاد
            test_embedding = self.model.encode("تست")
            self.dimension = len(test_embedding)
            
            logger.info(f"مدل با موفقیت بارگذاری شد (dim={self.dimension})")
            
        except ImportError:
            logger.error("sentence-transformers نصب نیست!")
            logger.info("نصب کنید: pip install sentence-transformers")
            self.model = None
        except Exception as e:
            logger.error(f"خطا در بارگذاری مدل: {e}")
            self.model = None
    
    def embed(self, text: str) -> Dict:
        """
        تبدیل یک متن به embedding
        
        Args:
            text: متن ورودی
            
        Returns:
            dict: شامل embedding و متادیتا
            {
                'embedding': numpy.ndarray,
                'dimension': int,
                'text_hash': str,
                'model': str,
                'success': bool
            }
        """
        if not text or not text.strip():
            return self._empty_result()
        
        if self.model is None:
            logger.error("مدل بارگذاری نشده است")
            return self._empty_result(error="مدل در دسترس نیست")
        
        try:
            # تولید embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # محاسبه hash متن برای شناسایی تکراری
            text_hash = self._hash_text(text)
            
            return {
                'embedding': embedding,
                'dimension': len(embedding),
                'text_hash': text_hash,
                'model': self.model_name,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"خطا در تولید embedding: {e}")
            return self._empty_result(error=str(e))
    
    def embed_batch(self, texts: List[str], batch_size: int = 32) -> Dict:
        """
        تبدیل دسته‌ای متون به embedding
        
        Args:
            texts: لیست متون
            batch_size: اندازه هر دسته
            
        Returns:
            dict: شامل لیست embeddings
        """
        if not texts:
            return {'embeddings': [], 'success': False}
        
        if self.model is None:
            return {'embeddings': [], 'success': False, 'error': 'مدل در دسترس نیست'}
        
        try:
            embeddings = self.model.encode(
                texts, 
                batch_size=batch_size,
                convert_to_numpy=True,
                show_progress_bar=len(texts) > 10
            )
            
            # محاسبه hash برای هر متن
            text_hashes = [self._hash_text(t) for t in texts]
            
            return {
                'embeddings': embeddings,
                'text_hashes': text_hashes,
                'count': len(embeddings),
                'dimension': self.dimension,
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"خطا در تولید embedding دسته‌ای: {e}")
            return {'embeddings': [], 'success': False, 'error': str(e)}
    
    def embed_sections(self, sections: Dict[str, str]) -> Dict[str, np.ndarray]:
        """
        تولید embedding برای هر بخش پروپوزال
        
        Args:
            sections: دیکشنری بخش‌ها
            
        Returns:
            dict: embedding هر بخش
        """
        section_embeddings = {}
        
        for section_name, content in sections.items():
            if content and len(content.strip()) > 10:
                result = self.embed(content)
                if result['success']:
                    section_embeddings[section_name] = result['embedding']
        
        return section_embeddings
    
    def get_combined_embedding(
        self, 
        sections: Dict[str, str],
        weights: Dict[str, float] = None
    ) -> np.ndarray:
        """
        ترکیب embedding بخش‌ها با وزن‌دهی
        
        Args:
            sections: دیکشنری بخش‌ها
            weights: وزن هر بخش
            
        Returns:
            numpy.ndarray: embedding ترکیبی
        """
        if weights is None:
            weights = {
                'abstract': 2.0,
                'introduction': 1.5,
                'methodology': 1.5,
                'objectives': 1.8,
                'literature_review': 1.2,
                'findings': 1.3,
                'discussion': 1.0,
                'references': 0.5
            }
        
        section_embeddings = self.embed_sections(sections)
        
        if not section_embeddings:
            return np.zeros(self.dimension)
        
        weighted_sum = np.zeros(self.dimension)
        total_weight = 0
        
        for section, embedding in section_embeddings.items():
            weight = weights.get(section, 1.0)
            weighted_sum += embedding * weight
            total_weight += weight
        
        if total_weight > 0:
            combined = weighted_sum / total_weight
        else:
            combined = np.zeros(self.dimension)
        
        # نرمال‌سازی
        norm = np.linalg.norm(combined)
        if norm > 0:
            combined = combined / norm
        
        return combined
    
    def _hash_text(self, text: str) -> str:
        """
        محاسبه hash متن
        
        Args:
            text: متن ورودی
            
        Returns:
            str: SHA-256 hash
        """
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _empty_result(self, error: str = None) -> Dict:
        """ساختار خروجی خالی"""
        return {
            'embedding': np.zeros(self.dimension),
            'dimension': self.dimension,
            'text_hash': '',
            'model': self.model_name,
            'success': False,
            'error': error or 'متن خالی است'
        }
    
    def is_ready(self) -> bool:
        """بررسی آماده بودن مدل"""
        return self.model is not None


# تست ماژول
if __name__ == "__main__":
    embedder = TextEmbedder()
    
    if embedder.is_ready():
        test_texts = [
            "این پژوهش به بررسی یادگیری ماشین می‌پردازد",
            "این تحقیق درباره هوش مصنوعی است",
            "من امروز به فروشگاه رفتم"
        ]
        
        print("=" * 60)
        print("🔢 تست تبدیل به Embedding")
        print("=" * 60)
        
        # تست تکی
        result = embedder.embed(test_texts[0])
        print(f"\n✅ Embedding تولید شد")
        print(f"   ابعاد: {result['dimension']}")
        print(f"   Hash: {result['text_hash'][:16]}...")
        
        # تست دسته‌ای
        batch_result = embedder.embed_batch(test_texts)
        print(f"\n✅ Embedding دسته‌ای تولید شد")
        print(f"   تعداد: {batch_result['count']}")
    else:
        print("❌ مدل بارگذاری نشده است")
        print("   pip install sentence-transformers")

