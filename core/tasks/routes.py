from fastapi import APIRouter


router = APIRouter(tags=["Tasks"])


@router.get("/tasks/")
async def retrieve_task_list():
    return []


@router.get("/tasks/{task_id}")
async def retrieve_task_detail(task_id: int):
    return {}
