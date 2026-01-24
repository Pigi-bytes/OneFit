def test_index_route(client):
    """
    Teste que la route racine retourne un code 200 ainsi que la bonne
    """
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()
    assert "Hello" in data
    assert data["Hello"] is not None
    assert data["Hello"] == "world"


def test_index_alias_route(client):
    """
    Teste que l'alias /index fonctionne également.
    """
    response = client.get("/index")
    assert response.status_code == 200

    data1 = response.get_json()

    response = client.get("/")
    assert response.status_code == 200

    data2 = response.get_json()

    assert data1 == data2
