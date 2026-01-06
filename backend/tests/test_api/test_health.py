"""Tests for health check endpoint."""


def test_health_endpoint_returns_status(client):
    """Health endpoint should return a valid response structure."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "qdrant" in data
    assert "sessions" in data
    assert "tracing" in data


def test_health_endpoint_tracing_disabled_by_default(client):
    """Tracing should be disabled when not configured."""
    response = client.get("/health")
    data = response.json()
    assert data["tracing"] == "disabled"


def test_health_endpoint_qdrant_not_configured(client):
    """Qdrant should show as not_configured until VectorStoreService is implemented."""
    response = client.get("/health")
    data = response.json()
    assert data["qdrant"] == "not_configured"


def test_health_endpoint_sessions_zero(client):
    """Sessions should be 0 until SessionManager is implemented."""
    response = client.get("/health")
    data = response.json()
    assert data["sessions"] == 0


def test_health_endpoint_database_status(client):
    """Database status should be either 'ok' or 'error'."""
    response = client.get("/health")
    data = response.json()
    # Database status depends on whether connection succeeds
    assert data["database"] in ["ok", "error"]


def test_health_endpoint_status_logic(client):
    """Overall status should be degraded when DB is OK (Qdrant not configured)."""
    response = client.get("/health")
    data = response.json()
    # Status should be:
    # - "error" if database fails
    # - "degraded" if database OK but Qdrant not configured
    if data["database"] == "ok":
        assert data["status"] == "degraded"
    else:
        assert data["status"] == "error"
