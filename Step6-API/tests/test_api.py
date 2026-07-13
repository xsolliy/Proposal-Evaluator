"""
تست‌های API
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from api.main import app


client = TestClient(app)


class TestGeneralEndpoints:
    """تست endpoints عمومی"""
    
    def test_root(self):
        """تست صفحه اصلی"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_health_check(self):
        """تست health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data
        assert "services" in data
    
    def test_get_weights(self):
        """تست دریافت وزن‌ها"""
        response = client.get("/api/weights")
        assert response.status_code == 200
        data = response.json()
        assert "weights" in data
        weights = data["weights"]
        assert sum(weights.values()) == pytest.approx(1.0, 0.001)
    
    def test_get_supported_formats(self):
        """تست فرمت‌های پشتیبانی شده"""
        response = client.get("/api/supported-formats")
        assert response.status_code == 200
        data = response.json()
        assert "formats" in data
        assert "pdf" in data["formats"]
        assert "docx" in data["formats"]


class TestEvaluationEndpoints:
    """تست endpoints ارزیابی"""
    
    def test_evaluate_without_file(self):
        """تست ارزیابی بدون فایل"""
        response = client.post("/api/evaluate")
        assert response.status_code == 422  # Validation error
    
    def test_evaluate_with_invalid_format(self):
        """تست با فرمت نامعتبر"""
        # ایجاد فایل نمونه با فرمت نامعتبر
        files = {
            "file": ("test.txt", b"test content", "text/plain")
        }
        response = client.post("/api/evaluate", files=files)
        assert response.status_code == 400  # Bad request
    
    def test_evaluate_compact_without_file(self):
        """تست ارزیابی خلاصه بدون فایل"""
        response = client.post("/api/evaluate/compact")
        assert response.status_code == 422


class TestDocs:
    """تست مستندات"""
    
    def test_openapi_schema(self):
        """تست دسترسی به OpenAPI schema"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_swagger_ui(self):
        """تست دسترسی به Swagger UI"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc(self):
        """تست دسترسی به ReDoc"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestErrorHandling:
    """تست مدیریت خطاها"""
    
    def test_not_found(self):
        """تست endpoint نامعتبر"""
        response = client.get("/invalid/endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """تست متد نامعتبر"""
        response = client.post("/health")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

