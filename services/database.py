# === services/database.py ===
from datetime import datetime
from typing import List, Optional
from models.task_models import Task, TaskCreate, TaskUpdate, TaskSummary, TaskStatus, Priority

class TaskDatabase:
    def __init__(self):
        self.tasks: dict[int, Task] = {}
        self.next_id = 1

    def create_task(self, task_data: TaskCreate) -> Task:
        task = Task(
            id=self.next_id,
            **task_data.dict(),
            created_at=datetime.now()
        )
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def update_task(self, task_id: int, updates: TaskUpdate) -> Optional[Task]:
        if task_id not in self.tasks:
            return None
        
        task = self.tasks[task_id]
        update_data = updates.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(task, field, value)
        
        return task

    def delete_task(self, task_id: int) -> bool:
        return self.tasks.pop(task_id, None) is not None

    def get_summary(self) -> TaskSummary:
        tasks = list(self.tasks.values())
        now = datetime.now()
        
        return TaskSummary(
            total_tasks=len(tasks),
            by_status={status: sum(1 for t in tasks if t.status == status) for status in TaskStatus},
            by_priority={priority: sum(1 for t in tasks if t.priority == priority) for priority in Priority},
            overdue_count=sum(1 for t in tasks if t.due_date and t.due_date < now and t.status != TaskStatus.DONE)
        )