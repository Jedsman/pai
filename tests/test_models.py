import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from models.task_models import TaskCreate, TaskUpdate

class TestTaskModels:
    def test_task_create_valid(self):
        task = TaskCreate(
            title="Valid Task",
            description="Valid description",
            priority="high"
        )
        assert task.title == "Valid Task"
        assert task.priority == "high"

    def test_task_create_empty_title(self):
        with pytest.raises(ValidationError):
            TaskCreate(title="")

    def test_task_due_date_validation(self):
        # Past date should fail
        past_date = datetime.now() - timedelta(days=1)
        with pytest.raises(ValidationError):
            TaskCreate(title="Test", due_date=past_date)
        
        # Future date should pass
        future_date = datetime.now() + timedelta(days=1)
        task = TaskCreate(title="Test", due_date=future_date)
        assert task.due_date == future_date

    def test_task_update_partial(self):
        # Should allow partial updates
        update = TaskUpdate(title="New Title")
        assert update.title == "New Title"
        assert update.status is None