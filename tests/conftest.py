import pytest
from fastapi.testclient import TestClient
from main import app
from dependencies import db

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def clean_db():
    """Reset database before each test"""
    db.tasks.clear()
    db.next_id = 1
    yield db

# === tests/test_tasks.py ===
import pytest
from datetime import datetime, timedelta
from models.task_models import Priority, TaskStatus

class TestTaskAPI:
    def test_create_task(self, client, clean_db):
        task_data = {
            "title": "Test Task",
            "description": "Test description",
            "priority": "high"
        }
        response = client.post("/tasks/", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == "high"
        assert data["status"] == "todo"
        assert "id" in data

    def test_get_tasks(self, client, clean_db):
        # Create a task first
        client.post("/tasks/", json={"title": "Task 1"})
        client.post("/tasks/", json={"title": "Task 2", "priority": "high"})
        
        # Get all tasks
        response = client.get("/tasks/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_get_task_by_id(self, client, clean_db):
        # Create task
        create_response = client.post("/tasks/", json={"title": "Test Task"})
        task_id = create_response.json()["id"]
        
        # Get task
        response = client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["title"] == "Test Task"

    def test_get_nonexistent_task(self, client, clean_db):
        response = client.get("/tasks/999")
        assert response.status_code == 404

    def test_update_task(self, client, clean_db):
        # Create task
        create_response = client.post("/tasks/", json={"title": "Original"})
        task_id = create_response.json()["id"]
        
        # Update task
        update_data = {"title": "Updated", "status": "in_progress"}
        response = client.put(f"/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["status"] == "in_progress"

    def test_delete_task(self, client, clean_db):
        # Create task
        create_response = client.post("/tasks/", json={"title": "To Delete"})
        task_id = create_response.json()["id"]
        
        # Delete task
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_filter_tasks_by_status(self, client, clean_db):
        # Create tasks with different statuses
        client.post("/tasks/", json={"title": "Task 1"})
        task2_response = client.post("/tasks/", json={"title": "Task 2"})
        task2_id = task2_response.json()["id"]
        
        # Update one task status
        client.put(f"/tasks/{task2_id}", json={"status": "done"})
        
        # Filter by status
        response = client.get("/tasks/?status=done")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["status"] == "done"