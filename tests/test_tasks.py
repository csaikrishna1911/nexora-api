def setup_project_and_user(client):
    u_res = client.post("/api/v1/users", json={"name": "Task Assignee", "email": "assignee@example.com", "password": "Password123"})
    user_id = u_res.json()["data"]["id"]

    p_res = client.post("/api/v1/projects", json={"name": "Task Parent Project", "owner_id": user_id})
    project_id = p_res.json()["data"]["id"]
    return user_id, project_id


def test_create_task_success(client):
    user_id, project_id = setup_project_and_user(client)

    payload = {
        "title": "Build resume parser",
        "description": "Implement parsing pipeline",
        "project_id": project_id,
        "assignee_id": user_id,
        "status": "todo",
        "priority": "high",
        "due_date": "2026-09-30"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert data["data"]["title"] == "Build resume parser"
    assert data["data"]["status"] == "todo"
    assert data["data"]["priority"] == "high"
    assert data["data"]["project_id"] == project_id
    assert data["data"]["assignee_id"] == user_id


def test_create_task_invalid_project(client):
    payload = {
        "title": "Orphan Task",
        "project_id": 9999
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "PROJECT_NOT_FOUND"


def test_create_task_invalid_assignee(client):
    _, project_id = setup_project_and_user(client)
    payload = {
        "title": "Task with missing assignee",
        "project_id": project_id,
        "assignee_id": 9999
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "ASSIGNEE_NOT_FOUND"


def test_get_tasks_filtering(client):
    user_id, project_id = setup_project_and_user(client)

    client.post("/api/v1/tasks", json={"title": "Task One", "project_id": project_id, "status": "todo", "priority": "low"})
    client.post("/api/v1/tasks", json={"title": "Task Two", "project_id": project_id, "status": "in-progress", "priority": "high"})
    client.post("/api/v1/tasks", json={"title": "Task Three", "project_id": project_id, "status": "done", "priority": "high"})

    # Filter by status
    res_status = client.get(f"/api/v1/tasks?status=in-progress")
    assert res_status.status_code == 200
    assert len(res_status.json()["data"]["items"]) == 1
    assert res_status.json()["data"]["items"][0]["title"] == "Task Two"

    # Filter by priority
    res_priority = client.get(f"/api/v1/tasks?priority=high")
    assert res_priority.status_code == 200
    assert len(res_priority.json()["data"]["items"]) == 2

    # Filter by project_id
    res_project = client.get(f"/api/v1/tasks?project_id={project_id}")
    assert res_project.status_code == 200
    assert len(res_project.json()["data"]["items"]) == 3


def test_get_task_by_id_success(client):
    _, project_id = setup_project_and_user(client)
    t_res = client.post("/api/v1/tasks", json={"title": "Single Task", "project_id": project_id})
    task_id = t_res.json()["data"]["id"]

    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Single Task"


def test_get_task_missing(client):
    response = client.get("/api/v1/tasks/9999")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"


def test_update_task_details(client):
    _, project_id = setup_project_and_user(client)
    t_res = client.post("/api/v1/tasks", json={"title": "Task to Update", "project_id": project_id})
    task_id = t_res.json()["data"]["id"]

    update_payload = {"title": "Updated Title", "priority": "high", "due_date": "2026-10-15"}
    response = client.patch(f"/api/v1/tasks/{task_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["title"] == "Updated Title"
    assert data["data"]["priority"] == "high"


def test_update_task_status_endpoint_success(client):
    _, project_id = setup_project_and_user(client)
    t_res = client.post("/api/v1/tasks", json={"title": "Task for Status Shift", "project_id": project_id, "status": "todo"})
    task_id = t_res.json()["data"]["id"]

    # Shift to in-progress
    shift_res = client.patch(f"/api/v1/tasks/{task_id}/status", json={"status": "in-progress"})
    assert shift_res.status_code == 200
    assert shift_res.json()["data"]["status"] == "in-progress"

    # Shift to done
    done_res = client.patch(f"/api/v1/tasks/{task_id}/status", json={"status": "done"})
    assert done_res.status_code == 200
    assert done_res.json()["data"]["status"] == "done"


def test_update_task_status_invalid_enum(client):
    _, project_id = setup_project_and_user(client)
    t_res = client.post("/api/v1/tasks", json={"title": "Task for Invalid Status", "project_id": project_id})
    task_id = t_res.json()["data"]["id"]

    response = client.patch(f"/api/v1/tasks/{task_id}/status", json={"status": "invalid-status-value"})
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_delete_task_success(client):
    _, project_id = setup_project_and_user(client)
    t_res = client.post("/api/v1/tasks", json={"title": "Task to Delete", "project_id": project_id})
    task_id = t_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/tasks/{task_id}")
    assert get_res.status_code == 404


def test_create_task_invalid_priority(client):
    _, project_id = setup_project_and_user(client)
    payload = {
        "title": "Task Invalid Priority",
        "project_id": project_id,
        "priority": "super-critical"
    }
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_get_tasks_search(client):
    _, project_id = setup_project_and_user(client)
    client.post("/api/v1/tasks", json={"title": "Parse PDF Resume", "description": "PyMuPDF extraction", "project_id": project_id})
    client.post("/api/v1/tasks", json={"title": "Frontend Layout", "description": "React components", "project_id": project_id})

    res = client.get("/api/v1/tasks?search=PyMuPDF")
    assert res.status_code == 200
    assert len(res.json()["data"]["items"]) == 1
    assert res.json()["data"]["items"][0]["title"] == "Parse PDF Resume"

