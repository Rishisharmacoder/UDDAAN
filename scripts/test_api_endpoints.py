"""Verification script to test all FastAPI endpoints."""
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_all_endpoints():
    print("[API VERIFICATION] Testing all APIx endpoints...")

    # 1. GET /
    res = client.get("/")
    assert res.status_code == 200, f"Failed GET /: {res.status_code}"
    print("  [OK] GET / (Dashboard HTML)")

    # 2. GET /api/summary
    res = client.get("/api/summary")
    assert res.status_code == 200, f"Failed GET /api/summary: {res.status_code}"
    data = res.json()
    assert "latest_apix" in data
    print(f"  [OK] GET /api/summary (Latest APIx: {data['latest_apix']})")

    # 3. GET /api/datasource (Provenance)
    res = client.get("/api/datasource")
    assert res.status_code == 200
    data = res.json()
    assert "active" in data
    print(f"  [OK] GET /api/datasource (Active: {data['active']})")

    # 4. GET /api/index (monthly, weekly, daily)
    for freq in ["monthly", "weekly", "daily"]:
        res = client.get(f"/api/index?frequency={freq}")
        assert res.status_code == 200, f"Failed GET /api/index?frequency={freq}"
        assert len(res.json()["values"]) > 0
        print(f"  [OK] GET /api/index?frequency={freq}")

    # 5. GET /api/routes
    res = client.get("/api/routes")
    assert res.status_code == 200
    assert len(res.json()) >= 6
    print(f"  [OK] GET /api/routes ({len(res.json())} routes)")

    # 6. GET /api/fares/recent
    res = client.get("/api/fares/recent?limit=5")
    assert res.status_code == 200
    assert len(res.json()) > 0
    print(f"  [OK] GET /api/fares/recent ({len(res.json())} rows)")

    # 7. GET /api/fares
    res = client.get("/api/fares?route=DEL-BOM&window=T+7&limit=10")
    assert res.status_code == 200
    print("  [OK] GET /api/fares (filtered query)")

    # 8. GET /api/sources/health
    res = client.get("/api/sources/health")
    assert res.status_code == 200
    assert len(res.json()) >= 7
    print(f"  [OK] GET /api/sources/health ({len(res.json())} sources tracked)")

    # 9. GET /api/health
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    print("  [OK] GET /api/health (System status: ok)")

    # 10. GET /api/anomalies
    res = client.get("/api/anomalies?days=7")
    assert res.status_code == 200
    print("  [OK] GET /api/anomalies (Data quality report)")

    # 11. Test 422 on invalid frequency
    res = client.get("/api/index?frequency=hourly")
    assert res.status_code == 422
    print("  [OK] GET /api/index?frequency=hourly returns 422 Unprocessable Entity as expected")

    print("\nALL API ENDPOINTS FUNCTIONING WITH 100% SUCCESS!\n")


if __name__ == "__main__":
    test_all_endpoints()
