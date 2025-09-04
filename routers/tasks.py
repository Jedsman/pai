# === routers/tasks.py ===
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

from models.task_models import Task, TaskCreate, TaskUpdate, TaskSummary, TaskStatus, Priority
from services import TaskDatabase, AITaskAnalyzer
from dependencies import get_db, get_ai_analyzer

router = APIRouter()

async def add_ai_suggestion(task: Task, analyzer: AITaskAnalyzer):
    """Background task to add AI suggestion"""
    suggestion = await analyzer.analyze_task(task)
    task.ai_suggestion = suggestion

@router.post("/", response_model=Task)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    db: TaskDatabase = Depends(get_db),
    ai_analyzer: AITaskAnalyzer = Depends(get_ai_analyzer)
):
    """Create a new task with AI analysis"""
    task = db.create_task(task_data)
    background_tasks.add_task(add_ai_suggestion, task, ai_analyzer)
    return task

@router.get("/", response_model=List[Task])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[Priority] = None,
    db: TaskDatabase = Depends(get_db)
):
    """Get all tasks with optional filtering"""
    tasks = db.get_all_tasks()
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    if priority:
        tasks = [t for t in tasks if t.priority == priority]
    
    return tasks

@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: int, db: TaskDatabase = Depends(get_db)):
    """Get a specific task by ID"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    updates: TaskUpdate,
    db: TaskDatabase = Depends(get_db)
):
    """Update a task"""
    task = db.update_task(task_id, updates)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/{task_id}")
async def delete_task(task_id: int, db: TaskDatabase = Depends(get_db)):
    """Delete a task"""
    if not db.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}

@router.get("/{task_id}/ai-suggestion", tags=["AI"])
async def get_ai_suggestion(
    task_id: int,
    model: Optional[str] = None,  # local, cloud, mock
    db: TaskDatabase = Depends(get_db),
    ai_analyzer: AITaskAnalyzer = Depends(get_ai_analyzer)
):
    """Get or generate AI suggestion for a task"""
    task = db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.ai_suggestion or model:
        task.ai_suggestion = await ai_analyzer.analyze_task(task, force_model=model)
    
    return {"suggestion": task.ai_suggestion}

@router.get("/analytics/summary", response_model=TaskSummary, tags=["Analytics"])
async def get_summary(db: TaskDatabase = Depends(get_db)):
    """Get task summary statistics"""
    return db.get_summary()