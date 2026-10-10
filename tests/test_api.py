"""Automated tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.config import settings

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == settings.VERSION
    assert "phase" in data


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["analysis_endpoint"] == "/api/analyze"


def test_analyze_valid_c_program():
    payload = {
        "source_code": """
        int add(int a, int b) {
            return a + b;
        }
        int main() {
            int x = add(5, 10);
            return 0;
        }
        """
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_valid"] is True
    assert data["error_count"] == 0
    assert len(data["diagnostics"]) == 0
    assert len(data["tokens"]) > 0
    assert data["ast"] is not None
    assert data["ast"]["node_type"] == "Program"


def test_analyze_syntax_error():
    payload = {
        "source_code": """
        int main() {
            int a = 10
            return a;
        }
        """
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_valid"] is False
    assert data["error_count"] >= 1
    assert len(data["diagnostics"]) >= 1

    first_diag = data["diagnostics"][0]
    assert "code" in first_diag
    assert "message" in first_diag
    assert "line" in first_diag
    assert "column" in first_diag
    assert "start_offset" in first_diag
    assert "end_offset" in first_diag
    assert first_diag["severity"] == "error"


def test_analyze_code_alias_field():
    payload = {
        "code": "int x = 42;"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["error_count"] == 0


def test_analyze_empty_input():
    payload = {"source_code": ""}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_valid"] is True
    assert data["error_count"] == 0
    assert data["ast"]["declarations"] == []


def test_analyze_malformed_json():
    response = client.post(
        "/api/analyze",
        content="not a json",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 422


def test_analyze_source_size_limit():
    large_source = "int x = 1;\n" * 15000  # ~165 KB, exceeds 100 KB limit
    payload = {"source_code": large_source}
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 413
    assert "exceeds maximum allowed size" in response.json()["detail"]
