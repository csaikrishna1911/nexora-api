def test_health_check_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "Nexora API"


def test_dashboard_summary_empty(client):
    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    summary = data["data"]
    assert summary["users"] == 0
    assert summary["projects"] == 0
    assert summary["tasks"] == 0
    assert summary["tasks_by_status"]["todo"] == 0
    assert summary["tasks_by_status"]["in-progress"] == 0
    assert summary["tasks_by_status"]["done"] == 0


def test_dashboard_summary_populated(client):
    # Create 1 user, 1 project, 3 tasks (1 todo, 1 in-progress, 1 done)
    u_res = client.post("/api/v1/users", json={"name": "Dash User", "email": "dash@example.com", "password": "Password123"})
    user_id = u_res.json()["data"]["id"]

    p_res = client.post("/api/v1/projects", json={"name": "Dash Project", "owner_id": user_id})
    project_id = p_res.json()["data"]["id"]

    client.post("/api/v1/tasks", json={"title": "T1", "project_id": project_id, "status": "todo", "priority": "low"})
    client.post("/api/v1/tasks", json={"title": "T2", "project_id": project_id, "status": "in-progress", "priority": "medium"})
    client.post("/api/v1/tasks", json={"title": "T3", "project_id": project_id, "status": "done", "priority": "high"})

    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    summary = data["data"]
    assert summary["users"] == 1
    assert summary["projects"] == 1
    assert summary["tasks"] == 3
    assert summary["tasks_by_status"]["todo"] == 1
    assert summary["tasks_by_status"]["in-progress"] == 1
    assert summary["tasks_by_status"]["done"] == 1
    assert summary["tasks_by_priority"]["low"] == 1
    assert summary["tasks_by_priority"]["medium"] == 1
    assert summary["tasks_by_priority"]["high"] == 1
