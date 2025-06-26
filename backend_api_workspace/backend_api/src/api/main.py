from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import get_db, Base, engine
from .models import User as UserModel, Category as CategoryModel, Task as TaskModel

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

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# === AUTHENTICATION SETTINGS ===
SECRET_KEY = "supersecretkey_for_dev_only"  # in production use env + secrets
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# --- DB INIT (ensure tables)
Base.metadata.create_all(bind=engine)


# === PYDANTIC SCHEMAS ===
class Token(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(..., description="Type of token (bearer)")


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    username: str
    full_name: str
    disabled: Optional[bool] = None

    class Config:
        orm_mode = True


class UserRegister(BaseModel):
    username: str = Field(
        ..., min_length=3, max_length=32, description="Username for the new account"
    )
    password: str = Field(
        ..., min_length=6, max_length=128, description="Password for the new account"
    )


class UserRegisterResponse(BaseModel):
    message: str = Field(..., description="Success message")
    username: str = Field(..., description="Registered username")


class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TaskBase(BaseModel):
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = Field(None, description="Description of the task")
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


# === AUTHENTICATION UTILS (DB) ===

# PUBLIC_INTERFACE
def get_password_hash(password: str) -> str:
    """Hashes password using passlib's CryptContext."""
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# PUBLIC_INTERFACE
def db_get_user(db: Session, username: str):
    """Fetch user SQLAlchemy ORM by username (case-insensitive)."""
    return db.query(UserModel).filter(UserModel.username == username).first()


# PUBLIC_INTERFACE
def db_authenticate_user(db: Session, username: str, password: str):
    """Authenticate user via DB and password hash."""
    user = db_get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
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


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
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
    user = db_get_user(db, token_data.username)
    if user is None:
        raise credentials_exception
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_active_user(
    current_user: User = Depends(get_current_user),
):
    """Dependency to ensure only active (not disabled) users."""
    return current_user


# === AUTH ENDPOINTS (DB) ===

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
    db: Session = Depends(get_db)
):
    """
    Registers a new user with username and password (persisted).

    - username: desired username (unique)
    - password: desired password (min 6 chars, will be hashed)
    """
    username = user_req.username.strip().lower()
    if not username or len(username) < 3:
        raise HTTPException(status_code=400, detail="Username too short (minimum 3 chars).")
    existing = db.query(UserModel).filter(UserModel.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists.")
    if not user_req.password or len(user_req.password) < 6:
        raise HTTPException(status_code=400, detail="Password too short (minimum 6 chars).")
    user = UserModel(
        username=username,
        full_name=username,
        hashed_password=get_password_hash(user_req.password),
        disabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserRegisterResponse(
        message="User registered successfully.",
        username=username
    )


@app.post("/auth/token", tags=["auth"], response_model=Token, summary="User login")
# PUBLIC_INTERFACE
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticates user and returns access JWT token (with DB).
    - username: User's username
    - password: User's password
    """
    user = db_authenticate_user(db, form_data.username, form_data.password)
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


# === CATEGORY ENDPOINT (DB) ===

@app.get(
    "/categories",
    tags=["tasks"],
    response_model=List[Category],
    summary="Get all task categories"
)
# PUBLIC_INTERFACE
async def list_categories(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_active_user)
):
    """
    Lists all task categories from DB.
    """
    cats = db.query(CategoryModel).all()
    return [Category(id=c.id, name=c.name) for c in cats]


# === TASK ENDPOINTS (DB) ===

@app.post(
    "/tasks",
    tags=["tasks"],
    response_model=Task,
    summary="Create new task",
    status_code=201,
)
# PUBLIC_INTERFACE
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_active_user)
):
    """
    Creates a new task for the current user; category can be created on-the-fly if new.
    """
    # Find or create category if specified
    category_id = None
    if task.category:
        cat = db.query(CategoryModel).filter(CategoryModel.name == task.category.strip()).first()
        if not cat:
            cat = CategoryModel(name=task.category.strip())
            db.add(cat)
            db.commit()
            db.refresh(cat)
        category_id = cat.id

    new_task = TaskModel(
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=datetime.utcnow(),
        due_date=task.due_date,
        owner_id=current_user.id,
        category_id=category_id,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    out_category = None
    if new_task.category:
        out_category = new_task.category.name
    return Task(
        id=new_task.id,
        title=new_task.title,
        description=new_task.description,
        status=new_task.status,
        created_at=new_task.created_at,
        due_date=new_task.due_date,
        category=out_category
    )


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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_active_user),
):
    """
    Lists all tasks for the current user, with optional status and category filters.
    """
    query = db.query(TaskModel).filter(TaskModel.owner_id == current_user.id)
    if status:
        query = query.filter(TaskModel.status == status)
    if category:
        cat = db.query(CategoryModel).filter(CategoryModel.name == category.strip()).first()
        if cat:
            query = query.filter(TaskModel.category_id == cat.id)
        else:
            return []
    results = query.all()
    tasks = []
    for t in results:
        cat_name = t.category.name if t.category else None
        tasks.append(
            Task(
                id=t.id,
                title=t.title,
                description=t.description,
                status=t.status,
                created_at=t.created_at,
                due_date=t.due_date,
                category=cat_name
            )
        )
    return tasks


@app.get(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=Task,
    summary="Read single task",
)
# PUBLIC_INTERFACE
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_active_user)
):
    """
    Gets a single task by its ID for the current user.
    """
    t = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.owner_id == current_user.id
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    cat_name = t.category.name if t.category else None
    return Task(
        id=t.id,
        title=t.title,
        description=t.description,
        status=t.status,
        created_at=t.created_at,
        due_date=t.due_date,
        category=cat_name,
    )


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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_active_user)
):
    """
    Updates a task by its ID for the current user; only provided fields will be updated.
    """
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.due_date is not None:
        task.due_date = task_update.due_date
    if task_update.category is not None:
        cat = db.query(CategoryModel).filter(
            CategoryModel.name == task_update.category.strip()
        ).first()
        if not cat:
            cat = CategoryModel(name=task_update.category.strip())
            db.add(cat)
            db.commit()
            db.refresh(cat)
        task.category_id = cat.id
    db.commit()
    db.refresh(task)
    cat_name = task.category.name if task.category else None
    return Task(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        due_date=task.due_date,
        category=cat_name,
    )


@app.delete(
    "/tasks/{task_id}",
    tags=["tasks"],
    response_model=dict,
    summary="Delete task",
)
# PUBLIC_INTERFACE
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_active_user)
):
    """
    Deletes a task by its ID for the current user.
    """
    task = db.query(TaskModel).filter(
        TaskModel.id == task_id, TaskModel.owner_id == current_user.id
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}


# === HEALTH CHECK ===

@app.get("/", tags=["health"])
# PUBLIC_INTERFACE
def health_check():
    """Returns health status of the API"""
    return {"message": "Healthy"}


@app.get(
    "/health/db",
    tags=["health"],
    summary="Check database connectivity",
    response_model=dict,
    responses={
        200: {"description": "Database connection is healthy"},
        503: {"description": "Failed to connect to the database"},
    },
)
# PUBLIC_INTERFACE
def db_health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint for the SQLite database connection.

    Attempts a simple query ('SELECT 1') using a SQLAlchemy session.

    - Returns: {"db_connection": "ok"} if successful,
      or {"db_connection": "error", "detail": <error>} if not.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"db_connection": "ok"}
    except Exception as e:
        return {"db_connection": "error", "detail": str(e)}


# === FIRST LAUNCH DB SEED: default categories ===


def seed_initial_categories():
    db = next(get_db())
    if db.query(CategoryModel).count() == 0:
        db.add_all([
            CategoryModel(name="Work"),
            CategoryModel(name="Personal"),
        ])
        db.commit()


try:
    seed_initial_categories()
except Exception:
    pass  # In container build: tables may not be ready yet, so fail softly here
