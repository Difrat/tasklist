from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
 
import models
from database import get_db
from dependencies import get_current_user
from repositories.tasks import TaskRepository
from schemas import Task, TaskCreate, TaskUpdate
from services.tasks import TaskService
 
router = APIRouter(prefix="/tasks", tags=["tasks"])
 
 
def get_task_repository(db: Session = Depends(get_db)) -> TaskRepository:
  return TaskRepository(db)
 
 
def get_task_service(
  repo: TaskRepository = Depends(get_task_repository),
) -> TaskService:
  return TaskService(repo)
 
 
@router.get("", response_model=list[Task])
def get_tasks(
  done: bool | None = None,
  limit: int = Query(default=10, ge=1, le=100),
  offset: int = Query(default=0, ge=0),
  service: TaskService = Depends(get_task_service),
  current_user: models.User = Depends(get_current_user),
):
  return service.list(user_id=current_user.id, done=done, limit=limit, offset=offset)
 
 
@router.get("/{task_id}", response_model=Task)
def get_task(
  task_id: int,
  service: TaskService = Depends(get_task_service),
  current_user: models.User = Depends(get_current_user),
):
  return service.get_or_404(task_id, current_user.id)
 
 
@router.post("", response_model=Task, status_code=201)
def create_task(
  payload: TaskCreate,
  service: TaskService = Depends(get_task_service),
  current_user: models.User = Depends(get_current_user),
):
  return service.create(payload, current_user.id)
 
 
@router.patch("/{task_id}", response_model=Task)
def update_task(
  task_id: int,
  payload: TaskUpdate,
  service: TaskService = Depends(get_task_service),
  current_user: models.User = Depends(get_current_user),
):
  return service.update(task_id, payload, current_user.id)
 
@router.delete("/completed", status_code=200)
def delete_completed(
  service:TaskService = Depends(get_task_service),
  current_user: models.User = Depends(get_current_user),
):
  deleted_count = service.delete_completed(current_user.id)
  
  return {"deleted_count": deleted_count}

@router.delete("/{task_id}", status_code=204)
def delete_task(
  task_id: int,
  service: TaskService = Depends(get_task_service),
  current_user: models.User = Depends(get_current_user),
):
  service.delete(task_id, current_user.id)