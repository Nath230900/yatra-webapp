def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Discover Nepal with YATRA" in response.data


def test_destinations_page(client):
    response = client.get("/destinations")
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data
