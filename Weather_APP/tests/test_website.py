def test_welcome(client):
    response = client.get("/")
    assert b"<title>Welcome</title>" in response.data

