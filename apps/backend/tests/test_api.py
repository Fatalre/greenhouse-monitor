def test_health(client):
    assert client.get("/api/v1/health").status_code == 200

def test_ingest_and_duplicate(client, payload):
    headers = {"X-API-Key": "test-key"}
    first = client.post("/api/v1/measurements", json=payload, headers=headers)
    assert first.status_code == 201
    assert first.json()["created"] is True
    second = client.post("/api/v1/measurements", json=payload, headers=headers)
    assert second.status_code == 200
    assert second.json()["created"] is False

def test_null_and_server_timestamp(client, payload):
    payload.pop("timestamp")
    response = client.post(
        "/api/v1/measurements", json=payload, headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 201

def test_bad_keys(client, payload):
    assert client.post("/api/v1/measurements", json=payload).status_code == 401
    assert client.post(
        "/api/v1/measurements", json=payload, headers={"X-API-Key": "bad"}
    ).status_code == 401

def test_too_many_thermocouples(client, payload):
    payload["thermocouples_c"] = [1] * 19
    response = client.post(
        "/api/v1/measurements", json=payload, headers={"X-API-Key": "test-key"}
    )
    assert response.status_code == 422

def test_history_and_csv(client, payload, auth):
    client.post(
        "/api/v1/measurements", json=payload, headers={"X-API-Key": "test-key"}
    )
    history = client.get("/api/v1/measurements?page=1&page_size=10", headers=auth)
    assert history.status_code == 200
    assert history.json()["total"] == 1
    csv_response = client.get("/api/v1/measurements/export.csv", headers=auth)
    assert csv_response.status_code == 200
    assert "TC18" in csv_response.text

def test_experiment_lifecycle(client, auth):
    created = client.post(
        "/api/v1/experiments",
        json={"external_id": "exp-2", "name": "Second"},
        headers=auth,
    )
    item_id = created.json()["id"]
    assert client.post(
        f"/api/v1/experiments/{item_id}/start", headers=auth
    ).json()["is_active"] is True
    assert client.post(
        f"/api/v1/experiments/{item_id}/finish", headers=auth
    ).json()["is_active"] is False
