import uuid

from fastapi import FastAPI, Response, Request
from contextlib import asynccontextmanager
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
from fastapi import Depends
from users.models import UserModel
from auth.jwt_auth import get_authenticated_user
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware



tags_metadata = [
    {
        'name': 'Tasks',
        'description': 'Operations related to task management',
        'externalDocs': {
            'description': 'more about tasks',
            'url': 'https://fastapi.tiangolo.com/tutorial/tasks/',
        }
    },
    {
        'name': 'Users',
        'description': 'Operations related to user like login or register'
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

app.include_router(tasks_routes)
app.include_router(users_routes)

# header_schema = APIKeyHeader(name='x-key')
# security = HTTPBearer(scheme_name='Token')


@app.get('/private')
async def private_route(
    auth_user: UserModel = Depends(get_authenticated_user)
):
    return {}


@app.post('/set-cookie')
def cookie_response(response: Response):
    response.set_cookie(key='token', value=str(uuid.uuid4()))
    return {'message': 'Cookie set'}


@app.post('/get-cookie')
def cookie_response(request: Request):
    return {'message': f'Cookie get {request.cookies.get("token")}'}
# @app.get('/private')
# async def private_route(
#     auth_user: UserModel = Depends(get_authenticated_user)
# ):
#     print(auth_user)
#     return auth_user


from starlette.middleware.base import BaseHTTPMiddleware
from time import time


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        process_time = time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time()  # زمان شروع پردازش درخواست
#     response = await call_next(request)  # پردازش درخواست توسط FastAPI
#     process_time = time() - start_time  # مدت زمان پردازش محاسبه شود
#     response.headers["X-Process-Time"] = str(process_time)  # اضافه کردن هدر به پاسخ
#     return response

origins = [
    "http://localhost",
    "http://localhost:5050",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
