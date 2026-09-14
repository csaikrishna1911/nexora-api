def test_create_project_success(client):
    # First create owner user
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    payload = {
        "name": "AI Resume Analyzer",
        "description": "An AI-powered resume analysis platform",
        "owner_id": owner_id
    }
    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["name"] == "AI Resume Analyzer"
    assert data["data"]["owner_id"] == owner_id


def test_create_project_invalid_owner(client):
    payload = {
        "name": "Orphan Project",
        "description": "Project with non-existent owner",
        "owner_id": 9999
    }
    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "OWNER_NOT_FOUND"


def test_get_projects_list_and_filter(client):
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner2@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    client.post("/api/v1/projects", json={"name": "Project Alpha", "owner_id": owner_id})
    client.post("/api/v1/projects", json={"name": "Project Beta", "owner_id": owner_id})

    response = client.get(f"/api/v1/projects?owner_id={owner_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]["items"]) == 2


def test_get_project_by_id_with_task_stats(client):
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner3@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    p_res = client.post("/api/v1/projects", json={"name": "Project Gamma", "owner_id": owner_id})
    project_id = p_res.json()["data"]["id"]

    # Create 3 tasks under project
    client.post("/api/v1/tasks", json={"title": "Task 1", "project_id": project_id, "status": "todo"})
    client.post("/api/v1/tasks", json={"title": "Task 2", "project_id": project_id, "status": "in-progress"})
    client.post("/api/v1/tasks", json={"title": "Task 3", "project_id": project_id, "status": "done"})

    response = client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    stats = data["data"]["task_stats"]
    assert stats["total_tasks"] == 3
    assert stats["todo"] == 1
    assert stats["in_progress"] == 1
    assert stats["done"] == 1


def test_get_project_missing(client):
    response = client.get("/api/v1/projects/9999")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "PROJECT_NOT_FOUND"


def test_update_project_success(client):
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner4@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    p_res = client.post("/api/v1/projects", json={"name": "Initial Name", "owner_id": owner_id})
    project_id = p_res.json()["data"]["id"]

    update_res = client.patch(f"/api/v1/projects/{project_id}", json={"name": "Updated Name", "description": "New description"})
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["data"]["name"] == "Updated Name"
    assert data["data"]["description"] == "New description"


def test_delete_project_success(client):
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner5@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    p_res = client.post("/api/v1/projects", json={"name": "To Be Deleted", "owner_id": owner_id})
    project_id = p_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/projects/{project_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/projects/{project_id}")
    assert get_res.status_code == 404


def test_get_projects_search_and_sort(client):
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner6@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    client.post("/api/v1/projects", json={"name": "Zebra Project", "description": "Animal tracking", "owner_id": owner_id})
    client.post("/api/v1/projects", json={"name": "Apple Project", "description": "Fruit management", "owner_id": owner_id})

    # Search
    search_res = client.get("/api/v1/projects?search=Animal")
    assert search_res.status_code == 200
    assert len(search_res.json()["data"]["items"]) == 1
    assert search_res.json()["data"]["items"][0]["name"] == "Zebra Project"

    # Sort descending by name
    sort_res = client.get("/api/v1/projects?sort=-name")
    assert sort_res.status_code == 200
    items = sort_res.json()["data"]["items"]
    assert items[0]["name"] == "Zebra Project"
    assert items[1]["name"] == "Apple Project"


def test_delete_project_cascades_tasks(client):
    u_res = client.post("/api/v1/users", json={"name": "Owner User", "email": "owner7@example.com", "password": "Password123"})
    owner_id = u_res.json()["data"]["id"]

    p_res = client.post("/api/v1/projects", json={"name": "Cascade Parent", "owner_id": owner_id})
    project_id = p_res.json()["data"]["id"]

    t_res = client.post("/api/v1/tasks", json={"title": "Cascade Child Task", "project_id": project_id})
    task_id = t_res.json()["data"]["id"]

    client.delete(f"/api/v1/projects/{project_id}")

    # Task should be deleted
    assert client.get(f"/api/v1/tasks/{task_id}").status_code == 404

