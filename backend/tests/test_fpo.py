def test_fpo_dashboard(client):
    response = client.get("/fpo/dashboard/1")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "location" in data
        assert "farmers" in data
        assert isinstance(data["farmers"], list)
        for farmer in data["farmers"]:
            assert "id" in farmer
            assert "name" in farmer
            assert "status" in farmer
            assert "farm_name" in farmer
            assert "farm_location" in farmer
            assert "crop_type" in farmer
            assert "irrigation_type" in farmer
            assert "soil_type" in farmer        
            assert "created_at" in farmer
            assert "updated_at" in farmer
            assert "identification_number" in farmer
            assert "profile_picture" in farmer
            assert "address" in farmer
            assert "phone_number" in farmer
            assert "email" in farmer
            assert "notes" in farmer
            assert "farm_size" in farmer
    else:
        assert response.json() == {"detail": "FPO not found"}