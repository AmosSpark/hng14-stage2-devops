from unittest.mock import MagicMock, patch
import os

os.environ.setdefault("REDIS_HOST")
os.environ.setdefault("REDIS_PORT")
os.environ.setdefault("REDIS_PASSWORD")

with patch("redis.Redis"):
    from fastapi.testclient import TestClient
    from main import app, r

client = TestClient(app)


@patch("main.r")
def test_health_returns_200_when_redis_ok(mock_redis):
    mock_redis.ping.return_value = True
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("main.r")
def test_health_returns_503_when_redis_down(mock_redis):
    mock_redis.ping.side_effect = Exception("Redis unavailable")
    response = client.get("/health")
    assert response.status_code == 503


@patch("main.r")
def test_create_job_returns_job_id(mock_redis):
    mock_redis.lpush = MagicMock(return_value=1)
    mock_redis.hset = MagicMock(return_value=1)
    response = client.post("/jobs")
    assert response.status_code == 200
    assert "job_id" in response.json()


@patch("main.r")
def test_get_job_returns_status(mock_redis):
    mock_redis.hget = MagicMock(return_value=b"queued")
    response = client.get("/jobs/some-job-id")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


@patch("main.r")
def test_get_job_returns_404_when_not_found(mock_redis):
    mock_redis.hget = MagicMock(return_value=None)
    response = client.get("/jobs/nonexistent-id")
    assert response.status_code == 404