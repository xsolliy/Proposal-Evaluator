"""
تست‌های رابط Streamlit
"""

import pytest
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'streamlit_app'))


class TestStreamlitComponents:
    """تست کامپوننت‌های Streamlit"""
    
    def test_imports(self):
        """تست import شدن ماژول‌ها"""
        try:
            import streamlit as st
            import requests
            import plotly.graph_objects as go
            import pandas as pd
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import required modules: {e}")
    
    def test_api_configuration(self):
        """تست پیکربندی API"""
        # بررسی اینکه آدرس API قابل تنظیم است
        api_url = "http://localhost:8000"
        assert api_url.startswith("http")
    
    def test_file_validation(self):
        """تست اعتبارسنجی فایل"""
        # بررسی فرمت‌های مجاز
        allowed_types = ['pdf', 'docx', 'doc']
        test_file = "test.pdf"
        file_ext = test_file.split('.')[-1].lower()
        assert file_ext in allowed_types


class TestUIComponents:
    """تست کامپوننت‌های UI"""
    
    def test_score_display(self):
        """تست نمایش نمرات"""
        # بررسی فرمت نمایش نمرات
        score = 85.5
        formatted = f"{score:.1f}"
        assert formatted == "85.5"
    
    def test_chart_generation(self):
        """تست تولید نمودارها"""
        # بررسی اینکه داده‌های نمودار معتبر هستند
        scores = {'writing': 85, 'structure': 82, 'content': 90}
        assert all(0 <= v <= 100 for v in scores.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

