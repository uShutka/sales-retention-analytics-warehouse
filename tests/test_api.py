from fastapi.testclient import TestClient

from sales_retention_analytics_warehouse.api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_summary_endpoint_returns_revenue():
    response = client.get("/analytics/summary")
    assert response.status_code == 200
    assert response.json()["revenue"] > 0


def test_daily_revenue_endpoint_returns_rows():
    response = client.get("/marts/daily-revenue")
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_cohort_endpoint_returns_periods():
    response = client.get("/marts/cohort-retention")
    assert response.status_code == 200
    assert "period_number" in response.json()[0]


def test_rfm_endpoint_returns_segments():
    response = client.get("/marts/rfm-segments")
    assert response.status_code == 200
    assert "segment" in response.json()[0]


def test_recommendations_endpoint_returns_actions():
    response = client.get("/analytics/recommendations")
    assert response.status_code == 200
    assert "action" in response.json()[0]
