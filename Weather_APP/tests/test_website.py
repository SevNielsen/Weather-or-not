def test_weatherMap(client):
    response = client.get("/")
    assert b"<title>Home</title>" in response.data

