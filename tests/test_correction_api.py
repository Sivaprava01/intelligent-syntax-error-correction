"""Automated API tests for Phase 2 correction endpoints."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


from unittest.mock import patch
from backend.app.correction.models import CorrectionCandidate, EditOperation, EditType, ValidationStatus


@pytest.fixture(autouse=True)
def mock_agent_propose():
    def fake_propose(source_code, diagnostics):
        if "int a = 10" in source_code:
            idx = source_code.find("int a = 10") + len("int a = 10")
            return [
                CorrectionCandidate(
                    candidate_id="mock_c1",
                    summary="Insert missing semicolon after variable declaration",
                    explanation="C syntax requires a semicolon after variable declarations.",
                    edit_operations=[
                        EditOperation(
                            operation=EditType.INSERT,
                            start_offset=idx,
                            end_offset=idx,
                            replacement=";",
                            expected_text=None,
                        )
                    ],
                    validation_status=ValidationStatus.PROPOSED,
                    related_diagnostics=["E203"],
                    confidence=0.95,
                )
            ]
        elif "int x = 5" in source_code:
            idx = source_code.find("int x = 5") + len("int x = 5")
            return [
                CorrectionCandidate(
                    candidate_id="mock_c2",
                    summary="Insert missing semicolon",
                    explanation="C syntax requires a semicolon.",
                    edit_operations=[
                        EditOperation(
                            operation=EditType.INSERT,
                            start_offset=idx,
                            end_offset=idx,
                            replacement=";",
                            expected_text=None,
                        )
                    ],
                    validation_status=ValidationStatus.PROPOSED,
                    related_diagnostics=["E203"],
                    confidence=0.95,
                )
            ]
        return []

    with patch("backend.app.correction.service.CorrectionService.request_corrections") as mock_req:
        # Instead patch the agent propose_corrections method
        pass
    with patch("backend.app.agents.crew_agent.CrewAICorrectionAgent.propose_corrections", side_effect=fake_propose), \
         patch("backend.app.agents.mock_agent.MockCorrectionAgent.propose_corrections", side_effect=fake_propose):
        yield


def test_post_corrections_valid_program():
    payload = {
        "source_code": "int main() { return 0; }"
    }
    response = client.post("/api/corrections", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_valid"] is True
    assert data["error_count"] == 0
    assert len(data["proposals"]) == 0
    assert "source_version" in data


def test_post_corrections_missing_semicolon():
    payload = {
        "source_code": "int main() {\n    int a = 10\n    return a;\n}"
    }
    response = client.post("/api/corrections", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["is_valid"] is False
    assert data["error_count"] >= 1
    assert len(data["proposals"]) >= 1

    first_proposal = data["proposals"][0]
    assert "candidate_id" in first_proposal
    assert "edit_operations" in first_proposal
    assert "validation_status" in first_proposal
    assert first_proposal["validation_status"] == "syntax_validated"


def test_post_v1_correct_alias():
    payload = {
        "code": "int main() {\n    int x = 5\n    return x;\n}"
    }
    response = client.post("/api/v1/correct", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["proposals"]) >= 1


def test_apply_correction_workflow():
    source = "int main() {\n    int a = 10\n    return a;\n}"
    # 1. Request corrections
    corr_res = client.post("/api/corrections", json={"source_code": source})
    assert corr_res.status_code == 200
    corr_data = corr_res.json()
    source_ver = corr_data["source_version"]
    proposal = corr_data["proposals"][0]

    # 2. Apply proposal
    apply_payload = {
        "source_code": source,
        "expected_source_version": source_ver,
        "proposal": proposal,
    }
    apply_res = client.post("/api/corrections/apply", json=apply_payload)
    assert apply_res.status_code == 200
    apply_data = apply_res.json()

    assert apply_data["success"] is True
    assert apply_data["is_valid"] is True
    assert apply_data["error_count"] == 0
    assert "int a = 10;" in apply_data["updated_source"]
    assert apply_data["error_message"] is None


def test_apply_stale_correction_rejected():
    source = "int main() { return 0; }"
    stale_proposal = {
        "candidate_id": "c_stale",
        "summary": "stale fix",
        "explanation": "",
        "edit_operations": [
            {"operation": "insert", "start_offset": 5, "end_offset": 5, "replacement": ";"}
        ],
        "corrected_source": "int ;main() { return 0; }",
        "validation_status": "proposed",
    }
    apply_payload = {
        "source_code": source,
        "expected_source_version": "incorrect_hash_999",
        "proposal": stale_proposal,
    }
    apply_res = client.post("/api/corrections/apply", json=apply_payload)
    assert apply_res.status_code == 200
    apply_data = apply_res.json()
    assert apply_data["success"] is False
    assert "Stale proposal" in apply_data["error_message"]
    assert apply_data["updated_source"] == source


def test_corrections_source_size_limit():
    large_source = "int x = 1;\n" * 15000
    payload = {"source_code": large_source}
    response = client.post("/api/corrections", json=payload)
    assert response.status_code == 413
