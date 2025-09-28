from fastapi import FastAPI
from contextlib import asynccontextmanager
from tasks.routes import router as task_route


tags_metadata = [
    {
        'name': 'Tasks',
        'description': 'Operations related to task management',
        'externalDocs': {
            'description': 'more about tasks',
            'url': 'https://fastapi.tiangolo.com/tutorial/tasks/',
        }
    }
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('application startup')
    yield
    print('application shutdown')

app = FastAPI(
    title="To-Do App",
    description=(
        "A simple, lightweight To-Do API built with FastAPI. "
        "Provides async CRUD operations for managing tasks, input validation via Pydantic,"
        "and interactive API documentation (Swagger UI & ReDoc). "
    ),
    summary="Lightweight To-Do API — async CRUD for tasks",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Seyed Amir Mahdi Mousavi",
        "url": "https://seyedamir.dev/",
        "email": "sayed1384mahdi@gmail.com",
    },
    license_info={
        "name": "BSD 3-Clause License",
        "url": "https://opensource.org/licenses/BSD-3-Clause",
    },
    lifespan=lifespan,
    openapi_tags=tags_metadata
)

app.include_router(task_route)
