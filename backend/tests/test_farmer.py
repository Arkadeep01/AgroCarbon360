def test_farmer_dashboard(client):
    response = client.get("/fpo/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_farmers" in data
    assert "active_farmers" in data
    assert "inactive_farmers" in data
    assert "total_users" in data
    assert "total_revenue" in data

    