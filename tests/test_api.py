from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_root():
    """Test the root endpoint returns 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "StudyMate API is running"}


def test_ask_empty_question():
    """Test that empty question returns 400."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 400


def test_ask_valid_question():
    """Test that a valid question returns 200 with expected fields."""
    with patch("app.main.retrieve_context", return_value="Machine learning is a subset of AI."), \
         patch("app.main.ask_llm", return_value="Machine learning is a subset of AI."):
        response = client.post("/ask", json={"question": "what is machine learning?"})
        assert response.status_code == 200
        data = response.json()
        assert "question" in data
        assert "answer" in data
        assert "latency_ms" in data


def test_upload_wrong_format():
    """Test that non-PDF upload returns 400."""
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"some content", "text/plain")}
    )
    assert response.status_code == 400


def test_stats():
    """Test the stats endpoint returns 200."""
    response = client.get("/stats")
    assert response.status_code == 200