def test_audit_api(client):
    response = client.get("/verifications/audit/1")
    assert response.status_code in (200, 404)
