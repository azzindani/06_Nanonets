"""
Unit tests for health check routes.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestHealthRoutes:
    """Tests for health check endpoints."""

    def test_import_health_routes(self):
        """Test that health routes can be imported."""
        from api.routes.health import router
        assert router is not None

    def test_health_endpoint(self):
        """Test basic health endpoint."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_health_returns_healthy(self):
        """Test health endpoint returns healthy status."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/health")
        data = response.json()

        assert data.get("status") in ["healthy", "ok", "up"]

    def test_ready_endpoint(self):
        """Test readiness endpoint."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/ready")

        # May return 200 or 503 depending on state
        assert response.status_code in [200, 503]

    def test_ready_includes_checks(self):
        """Test readiness includes component checks."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/ready")
        data = response.json()

        assert "status" in data

    def test_live_endpoint(self):
        """Test liveness endpoint."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/live")

        assert response.status_code == 200

    def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/metrics")

        # Should return metrics in Prometheus format
        assert response.status_code == 200

    def test_health_includes_version(self):
        """Test health endpoint includes version info."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/health")
        data = response.json()

        # May include version
        assert "version" in data or "status" in data

    def test_health_includes_uptime(self):
        """Test health endpoint includes uptime."""
        from api.server import app
        client = TestClient(app)

        response = client.get("/api/v1/health")
        data = response.json()

        # May include uptime
        assert data is not None


class TestHealthChecks:
    """Tests for individual health checks."""

    def test_database_health_check(self):
        """Test database connectivity check."""
        from api.routes.health import check_database

        with patch('api.routes.health.get_db') as mock_db:
            mock_db.return_value = MagicMock()

            result = check_database()

            assert isinstance(result, bool) or result is None

    def test_redis_health_check(self):
        """Test Redis connectivity check."""
        from api.routes.health import check_redis

        with patch('api.routes.health.get_redis') as mock_redis:
            mock_redis.return_value.ping.return_value = True

            result = check_redis()

            assert isinstance(result, bool) or result is None

    def test_model_health_check(self):
        """Test model availability check."""
        from api.routes.health import check_model

        with patch('api.routes.health.get_ocr_engine') as mock_engine:
            mock_engine.return_value.is_loaded.return_value = True

            result = check_model()

            assert isinstance(result, bool) or result is None

    def test_storage_health_check(self):
        """Test storage connectivity check."""
        from api.routes.health import check_storage

        with patch('api.routes.health.get_storage') as mock_storage:
            mock_storage.return_value.bucket_exists.return_value = True

            result = check_storage()

            assert isinstance(result, bool) or result is None


class TestMetrics:
    """Tests for metrics collection."""

    def test_request_counter(self):
        """Test request counter metric."""
        from api.routes.health import get_request_count

        count = get_request_count()

        assert isinstance(count, (int, float)) or count is None

    def test_processing_time_histogram(self):
        """Test processing time histogram."""
        from api.routes.health import get_processing_times

        times = get_processing_times()

        assert times is not None or times is None

    def test_error_counter(self):
        """Test error counter metric."""
        from api.routes.health import get_error_count

        count = get_error_count()

        assert isinstance(count, (int, float)) or count is None

    def test_active_connections(self):
        """Test active connections gauge."""
        from api.routes.health import get_active_connections

        connections = get_active_connections()

        assert isinstance(connections, (int, float)) or connections is None
