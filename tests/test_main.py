from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_version_endpoint():
    resp = client.get("/version")
    assert resp.status_code == 200
    assert "version" in resp.json()


def test_create_and_get_item():
    resp = client.post("/items", params={"name": "widget"})
    assert resp.status_code == 200
    item_id = resp.json()["id"]

    resp2 = client.get(f"/items/{item_id}")
    assert resp2.status_code == 200
    assert resp2.json()["name"] == "widget"


def test_create_item_invalid_name():
    resp = client.post("/items", params={"name": ""})
    assert resp.status_code == 400


def test_get_missing_item_returns_404():
    resp = client.get("/items/999999")
    assert resp.status_code == 404
