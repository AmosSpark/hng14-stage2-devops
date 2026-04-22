from unittest.mock import MagicMock, patch
import os

os.environ.setdefault("REDIS_HOST", "")
os.environ.setdefault("REDIS_PORT", "0")
os.environ.setdefault("REDIS_PASSWORD", "")


def test_health_returns_200_when_redis_ok():
    with patch("redis.Redis") as mock_redis_class:
        mock_redis_class.return_value.ping.return_value = True
        import importlib
        import main
        importlib.reload(main)
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


def test_health_returns_503_when_redis_down():
    with patch("redis.Redis") as mock_redis_class:
        mock_redis_class.return_value.ping.side_effect = Exception("Redis down")
        import importlib
        import main
        importlib.reload(main)
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.get("/health")
        assert response.status_code == 503


def test_create_job_returns_job_id():
    with patch("redis.Redis") as mock_redis_class:
        mock_instance = MagicMock()
        mock_redis_class.return_value = mock_instance
        import importlib
        import main
        importlib.reload(main)
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.post("/jobs")
        assert response.status_code == 200
        assert "job_id" in response.json()


def test_get_job_returns_status():
    with patch("redis.Redis") as mock_redis_class:
        mock_instance = MagicMock()
        mock_instance.hget.return_value = b"queued"
        mock_redis_class.return_value = mock_instance
        import importlib
        import main
        importlib.reload(main)
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.get("/jobs/some-job-id")
        assert response.status_code == 200
        assert response.json()["status"] == "queued"


def test_get_job_returns_404_when_not_found():
    with patch("redis.Redis") as mock_redis_class:
        mock_instance = MagicMock()
        mock_instance.hget.return_value = None
        mock_redis_class.return_value = mock_instance
        import importlib
        import main
        importlib.reload(main)
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        response = client.get("/jobs/nonexistent-id")
        assert response.status_code == 404