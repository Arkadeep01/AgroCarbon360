def test_register_and_login(client):
    # Test user registration
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "testcase@example.com",
        "password": "testpassword",
        "is_active": True,
        "is_superuser": False,
        "role_id": 1
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "tester"

    response = client.post("/auth/login", data={
        "emain": "testcase@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"