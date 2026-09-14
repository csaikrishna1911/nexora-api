def test_create_user_success(client):
    payload = {
        "name": "Sai Krishna",
        "email": "sai@example.com",
        "password": "StrongPassword123"
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "Sai Krishna"
    assert data["data"]["email"] == "sai@example.com"
    assert "password" not in data["data"]
    assert "password_hash" not in data["data"]


def test_create_user_duplicate_email(client):
    payload = {
        "name": "Sai Krishna",
        "email": "sai@example.com",
        "password": "StrongPassword123"
    }
    client.post("/api/v1/users", json=payload)
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "USER_EMAIL_EXISTS"


def test_create_user_invalid_email(client):
    payload = {
        "name": "Sai Krishna",
        "email": "invalid-email-format",
        "password": "StrongPassword123"
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_create_user_weak_password(client):
    payload = {
        "name": "Sai Krishna",
        "email": "sai@example.com",
        "password": "short"
    }
    response = client.post("/api/v1/users", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False


def test_get_users_list_and_pagination(client):
    # Create two users
    client.post("/api/v1/users", json={"name": "User One", "email": "one@example.com", "password": "Password123"})
    client.post("/api/v1/users", json={"name": "User Two", "email": "two@example.com", "password": "Password123"})

    response = client.get("/api/v1/users?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    items = data["data"]["items"]
    assert len(items) == 2
    assert data["data"]["pagination"]["total"] == 2


def test_get_user_by_id_success(client):
    res_create = client.post("/api/v1/users", json={"name": "Alice", "email": "alice@example.com", "password": "Password123"})
    user_id = res_create.json()["data"]["id"]

    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "Alice"


def test_get_user_missing(client):
    response = client.get("/api/v1/users/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "USER_NOT_FOUND"


def test_update_user_success(client):
    res_create = client.post("/api/v1/users", json={"name": "Bob", "email": "bob@example.com", "password": "Password123"})
    user_id = res_create.json()["data"]["id"]

    update_payload = {"name": "Bob Updated", "email": "bob.updated@example.com"}
    response = client.patch(f"/api/v1/users/{user_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["name"] == "Bob Updated"
    assert data["data"]["email"] == "bob.updated@example.com"


def test_delete_user_success(client):
    res_create = client.post("/api/v1/users", json={"name": "Charlie", "email": "charlie@example.com", "password": "Password123"})
    user_id = res_create.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/users/{user_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 404


def test_update_user_duplicate_email_conflict(client):
    client.post("/api/v1/users", json={"name": "User One", "email": "user1@example.com", "password": "Password123"})
    u2 = client.post("/api/v1/users", json={"name": "User Two", "email": "user2@example.com", "password": "Password123"})
    u2_id = u2.json()["data"]["id"]

    response = client.patch(f"/api/v1/users/{u2_id}", json={"email": "user1@example.com"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "USER_EMAIL_EXISTS"


def test_get_users_invalid_pagination(client):
    response = client.get("/api/v1/users?page=0")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"

