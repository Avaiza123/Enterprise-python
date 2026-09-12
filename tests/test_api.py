"""
Black-box API regression tests, run by the pipeline AFTER a deploy
(against DEV/UAT review app URL), not against the source code directly.

Usage in CI:
    API_BASE_URL=https://dev.example.com pytest tests/test_api.py
"""
import os
import requests
import pytest

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


@pytest.mark.regression
def test_health_endpoint_live():
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.regression
def test_version_matches_expected_commit():
    resp = requests.get(f"{BASE_URL}/version", timeout=10)
    assert resp.status_code == 200
    body = resp.json()
    expected_sha = os.getenv("CI_COMMIT_SHORT_SHA")
    if expected_sha:
        assert body["commit"] == expected_sha, "Deployed build does not match pipeline commit"


@pytest.mark.regression
def test_items_crud_flow_live():
    create = requests.post(f"{BASE_URL}/items", params={"name": "regression-item"}, timeout=10)
    assert create.status_code == 200
    item_id = create.json()["id"]

    fetched = requests.get(f"{BASE_URL}/items/{item_id}", timeout=10)
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "regression-item"
