def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Meeting Room Booking API is running",
    }


def test_get_rooms(client):
    response = client.get("/rooms")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Ocean"
