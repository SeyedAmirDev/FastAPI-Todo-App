from fastapi import APIRouter, Path, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db

from .schemas import *
from .models import *

router = APIRouter(tags=["Tasks"])


@router.get("/tasks/", response_model=List[TaskResponseSchema])
async def retrieve_task_list(
        completed: bool = Query(None, description="filter tasks based on being completed or not"),
        limit: int = Query(10, gt=0, le=50, description="limiting the number of items to retrieve"),
        offset: int = Query(0, ge=0, description="used for paginating based on passed items"),
        db: Session = Depends(get_db)
):
    query = db.query(TaskModel)
    if completed is not None:
        query = query.filter_by(is_completed=completed)

    return query.limit(limit).offset(offset).all()


@router.post("/tasks/", response_model=TaskResponseSchema)
async def create_task(request: TaskCreateSchema, db: Session = Depends(get_db)):
    task = TaskModel(
        title=request.title,
        description=request.description,
        is_completed=request.is_completed,
    )

    db.add(task)
    db.commit()

    return task


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_task_detail(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(request: TaskUpdateSchema, task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    for key, value in request.model_dump().items():
        setattr(task, key, value)

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int = Path(..., gt=0), db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter_by(id=task_id).one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")

    db.delete(task)
    db.commit()
