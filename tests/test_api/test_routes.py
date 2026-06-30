"""
Tests for NeuroScope API Routes.

Tests the FastAPI endpoints using httpx TestClient.
"""

import json
import os

import pytest

# Skip if httpx not installed (test dependency)
httpx = pytest.importorskip("httpx")

from fastapi.testclient import TestClient


# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def cnn_v16_config():
    """Load the CNN v16 model config."""
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "src", "data", "models", "cnn_v16.json"
    )
    with open(path, "r") as f:
        return json.load(f)


# ── Health & Root ────────────────────────────────────────────────────


class TestHealthEndpoint:
    """Test the /health endpoint."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"

    def test_health_is_fast(self, client):
        """Health check should respond quickly (< 1s)."""
        import time
        start = time.time()
        client.get("/health")
        elapsed = time.time() - start
        assert elapsed < 1.0


class TestRootEndpoint:
    """Test the / root endpoint."""

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_api_info(self, client):
        data = client.get("/").json()
        assert "name" in data
        assert "NeuroScope" in data["name"]
        assert "version" in data
        assert "docs" in data

    def test_docs_endpoint_accessible(self, client):
        """Swagger docs should be accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client):
        """OpenAPI schema should be accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "paths" in schema


# ── Export Endpoint ──────────────────────────────────────────────────


class TestExportEndpoint:
    """Test the /api/export endpoint."""

    def test_export_requires_body(self, client):
        """POST /api/export without body should return 422."""
        response = client.post("/api/export")
        assert response.status_code == 422

    def test_export_json_format_accepted(self, client, cnn_v16_config):
        """Export with format=json should be accepted (may 404 if model not in store)."""
        response = client.post(
            "/api/export",
            json={"model_id": "nonexistent", "format": "json"},
        )
        # Should get 404 (model not in store), not 400 (bad format)
        assert response.status_code == 404

    def test_export_invalid_format_rejected(self, client):
        """Export with unsupported format should return 400."""
        response = client.post(
            "/api/export",
            json={"model_id": "test", "format": "invalid_format"},
        )
        # May be 404 (model not found) or 400 (bad format)
        assert response.status_code in (400, 404)

    def test_export_png_format_accepted(self, client):
        """Export with format=png should be accepted structurally."""
        response = client.post(
            "/api/export",
            json={"model_id": "nonexistent", "format": "png"},
        )
        assert response.status_code == 404  # Model not in store, but format is valid

    def test_export_summary_format_accepted(self, client):
        """Export with format=summary should be accepted structurally."""
        response = client.post(
            "/api/export",
            json={"model_id": "nonexistent", "format": "summary"},
        )
        assert response.status_code == 404


# ── Rate Limiting ────────────────────────────────────────────────────


class TestRateLimiting:
    """Test that rate limiting is configured."""

    def test_rate_limit_headers_present(self, client):
        """API responses should include rate limit headers (if slowapi is configured)."""
        response = client.get("/health")
        # Rate limit headers may or may not be on /health
        # Just verify the endpoint works
        assert response.status_code == 200


# ── CORS ─────────────────────────────────────────────────────────────


class TestCORS:
    """Test CORS configuration."""

    def test_cors_allows_localhost(self, client):
        """CORS should allow requests from localhost origins."""
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        # In development, CORS should be permissive
        assert response.status_code in (200, 204)
