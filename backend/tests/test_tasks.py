from datetime import date, timedelta


def make_task(client, **overrides):
    payload = {"title": "Write tests", "description": "cover the API", **overrides}
    res = client.post("/api/tasks", json=payload)
    assert res.status_code == 201, res.text
    return res.json()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_get_task(client):
    task = make_task(client, priority="high")
    assert task["status"] == "todo"
    assert task["priority"] == "high"

    res = client.get(f"/api/tasks/{task['id']}")
    assert res.status_code == 200
    assert res.json()["title"] == "Write tests"


def test_create_rejects_empty_title(client):
    res = client.post("/api/tasks", json={"title": ""})
    assert res.status_code == 422


def test_filter_by_status_and_search(client):
    make_task(client, title="Fix login bug")
    make_task(client, title="Deploy to AWS", status="in_progress")

    in_progress = client.get("/api/tasks", params={"status": "in_progress"}).json()
    assert [t["title"] for t in in_progress] == ["Deploy to AWS"]

    found = client.get("/api/tasks", params={"search": "login"}).json()
    assert [t["title"] for t in found] == ["Fix login bug"]


def test_partial_update(client):
    task = make_task(client)
    res = client.patch(f"/api/tasks/{task['id']}", json={"status": "done"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "done"
    assert body["title"] == "Write tests"  # untouched field kept


def test_delete_task(client):
    task = make_task(client)
    assert client.delete(f"/api/tasks/{task['id']}").status_code == 204
    assert client.get(f"/api/tasks/{task['id']}").status_code == 404


def test_missing_task_returns_404(client):
    assert client.patch("/api/tasks/999", json={"title": "x"}).status_code == 404


def test_stats_counts_overdue(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    make_task(client, title="Late", due_date=yesterday)
    make_task(client, title="Late but done", due_date=yesterday, status="done")
    make_task(client, title="No date")

    stats = client.get("/api/tasks/stats").json()
    assert stats["total"] == 3
    assert stats["by_status"] == {"todo": 2, "in_progress": 0, "done": 1}
    assert stats["overdue"] == 1
