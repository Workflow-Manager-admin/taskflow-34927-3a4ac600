from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Body
from passlib.context import CryptContext

# === APP METADATA ===
app = FastAPI(
    title="Taskflow Backend API",
    description=(
        "A scalable backend API for the Taskflow manager. Provides user authentication, "
        "task management (CRUD), status tracking, and categorization."
    ),
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "User Authentication"},
        {"name": "tasks", "description": "Task CRUD, status tracking, categorization"},
    ],
)

# === CORS CONFIGURATION ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === IN-MEMORY STORES (Replace with DB integration in real deployment) ===
fake_users_db = {
    "alice": {
        "username": "alice",
        "full_name": "Alice Liddell",
        "hashed_password": "fakehashed_secret1",
        "disabled": False,
    },
    "bob": {
        "username": "bob",
        "full_name": "Bob Smith",
        "hashed_password": "fakehashed_secret2",
        "disabled": False,
    },
}
fake_tasks_db: Dict[int, dict] = {}
fake_categories_db = {"Work": 1, "Personal": 2}
task_id_counter = 1

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === AUTHENTICATION SETTINGS ===
SECRET_KEY = "supersecretkey_for_dev_only"  # in production use env + secrets
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# === SCHEMAS ===


class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of token (bearer)")


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    full_name: str
    disabled: Optional[bool] = None


class UserInDB(User):
    hashed_password: str


# === SCHEMA FOR REGISTRATION ===


class UserRegister(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=32,
        description="Username for the new account"
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Password for the new account"
    )


class UserRegisterResponse(BaseModel):
    message: str = Field(..., description="Success message")
    username: str = Field(..., description="Registered username")


class Category(BaseModel):
    id: int
    name: str


# Blank line below ensures E302 compliance
class TaskStatus(str):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class TaskBase(BaseModel):
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(
        None, description="Description of the task"
    )
    status: str = Field(
        ..., description="Status of the task", examples=["TODO", "IN_PROGRESS", "DONE"]
    )
    category: Optional[str] = Field(None, description="Category name")
    due_date: Optional[datetime] = Field(None, description="Due date of the task")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    due_date: Optional[datetime] = None


class Task(TaskBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


# === AUTHENTICATION UTILS ===


# PUBLIC_INTERFACE
def fake_hash_password(password: str) -> str:
    """Fake password hashing for demonstration purposes."""
    return "fakehashed_" + password


# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hashes password using passlib's CryptContext."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the hashed fake password or bcrypt hash."""
    if hashed_password.startswith("fakehashed_"):
        return fake_hash_password(plain_password) == hashed_password
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def get_user(db, username: str):
    """Retrieves user info from db."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


# PUBLIC_INTERFACE
def authenticate_user(db, username: str, password: str):
    """Authenticates a user by username and password."""
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get current user from JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_active_user(current_user: User = Depends(get_current_user)):
    """Dependency to ensure only active (not disabled) users."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# === AUTH ENDPOINTS ===


@app.post(
    "/register",
    tags=["auth"],
    response_model=UserRegisterResponse,
    summary="Register a new user",
    status_code=201,
    responses={
        201: {"description": "User registered successfully", "model": UserRegisterResponse},
        400: {"description": "Invalid username or password / Username already exists"},
    }
)
# PUBLIC_INTERFACE
async def register_user(
    user_req: UserRegister = Body(..., description="New user's registration data"),
):
    """
    Registers a new user with username and password.

    - username: desired username (unique)
    - password: desired password (min 6 chars, will be hashed)
    """
    username = user_req.username.strip().lower()
    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Username too short (minimum 3 chars).")
    if username in fake_users_db:
        raise HTTPException(status_code=400, detail="Username already exists.")
    if not user_req.password or len(user_req.password) < 6:
        raise HTTPException(status_code=400, detail="Password too short (minimum 6 chars).")
    # Store the user with hashed password. Use bcrypt (passlib) hashing.
    user_db_record = {
        "username": username,
        "full_name": username,
        "hashed_password": get_password_hash(user_req.password),
        "disabled": False,
    }
    fake_users_db[username] = user_db_record
    return UserRegisterResponse(
        message="User registered successfully.",
        username=username
    )


@app.post("/auth/token", tags=["auth"], response_model=Token, summary="User login")
# PUBLIC_INTERFACE
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates user and returns access JWT token.

    - username: User's username
    - password: User's password
    """
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", tags=["auth"], response_model=User, summary="Get current user")
# PUBLIC_INTERFACE
async def read_users_me(current_user: User = Depends(get_active_user)):
    """
    Returns information about the current logged in user.
    """
    return current_user


# === CATEGORY ENDPOINT ===


@app.get(
    "/categories",
    tags=["tasks"],
    response_model=List[Category],
    summary="Get all task categories"
)
# PUBLIC_INTERFACE
async def list_categories(current_user: User = Depends(get_active_user)):
    """
    Lists all task categories.
    """
    return [Category(id=v, name=k) for k, v in fake_categories_db.items()]


# === TASK ENDPOINTS ===


@app.post(
    "/tasks",
    tags=["tasks"],
    response_model=Task,
    summary="Create new task",
    status_code=201,
)
# PUBLIC_INTERFACE
async def create_task(
    task: TaskCreate, current_user: User = Depends(get_active_user)
):
    """
    Creates a new task for the current user.

    - title: Title of the task
    - description: Optional description
    - status: Task status (TODO, IN_PROGRESS, DONE)
    - category: Optional category name
    - due_date: Optional due date (ISO 8601 format)
    """
    global task_id_counter
    new_task_id = task_id_counter
    task_id_counter += 1
    task_data = task.dict()
    task_obj = {
        "id": new_task_id,
        **task_data,
        "created_at": datetime.utcnow(),
        "username": current_user.username,
    }
    fake_tasks_db[new_task_id] = task_obj
    return Task(**task_obj)


@app.get(
    "/tasks",
    tags=["tasks"],
    response_model=List[Task],
    summary="List all tasks for current user",
)
# PUBLIC_INTERFACE
async def list_tasks(
    status: Optional[str] = None,
    category: Optional[str] = None,
    current_user: User = Depends(get_active_user),
):
    """
    Lists all tasks for the current user, with optional status and category filters.

    - status: Filter by task status (optional)
    - category: Filter by category name (optional)
    """
    user_tasks = [
        Task(**t)
        for t in fake_tasks_db.values()
        if t["username"] == current_user.username
        and (status is None or t["status"] == status)
        and (category is None or t["category"] == category)
    ]
    return user_tasks


@app.get(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=Task,
    summary="Read single task",
)
# PUBLIC_INTERFACE
async def get_task(task_id: int, current_user: User = Depends(get_active_user)):
    """
    Gets a single task by its ID for the current user.
    """
    task = fake_tasks_db.get(task_id)
    if not task or task["username"] != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**task)


@app.put(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=Task,
    summary="Update task",
)
# PUBLIC_INTERFACE
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: User = Depends(get_active_user),
):
    """
    Updates a task by its ID for the current user.
    Only provided fields will be updated.
    """
    task = fake_tasks_db.get(task_id)
    if not task or task["username"] != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    update_data = task_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        task[field] = value
    fake_tasks_db[task_id] = task
    return Task(**task)


@app.delete(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=dict,
    summary="Delete task",
)
# PUBLIC_INTERFACE
async def delete_task(task_id: int, current_user: User = Depends(get_active_user)):
    """
    Deletes a task by its ID for the current user.
    """
    task = fake_tasks_db.get(task_id)
    if not task or task["username"] != current_user.username:
        raise HTTPException(status_code=404, detail="Task not found")
    del fake_tasks_db[task_id]
    return {
        "detail": "Task deleted"
    }


# === HEALTH CHECK ===


@app.get("/", tags=["health"])
# PUBLIC_INTERFACE
def health_check():
    """Returns health status of the API"""
    return {"message": "Healthy"}
