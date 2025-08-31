def test_create_audit_report(client):
    # Test creating an audit report
    response = client.post("/auditor/reports/", json={
        "auditor_id": 1,
        "farmer_id": 1,
        "findings": "Sample findings",
        "recommendations": "Sample recommendations",
        "status": "pending",
        "entity_type": "farmer"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["findings"] == "Sample findings"
    assert data["status"] == "pending"