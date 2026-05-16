from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import engine, Base
from deps import get_db, get_current_user
from models import User
from schemas import UserCreate, UserLogin, TaskCreate, TaskUpdate
from auth import hash_password, verify_password, create_token
import crud


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Role Based Task Manager")


# -----------------------------
# CORS CONFIGURATION
# -----------------------------

origins = [
    "http://localhost:5173",  # Vite
    "http://localhost:3000",  # React
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://frontend-two-coral-61.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # allowed frontend URLs
    allow_credentials=True,
    allow_methods=["*"],        # allow GET, POST, PUT, DELETE, OPTIONS
    allow_headers=["*"],        # allow all headers
)


# -----------------------------
# SIGNUP
# -----------------------------

@app.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):

    existing = db.query(User).filter(User.username == user.username).first()

    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully"}


# -----------------------------
# LOGIN
# -----------------------------

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({
        "id": db_user.id,
        "role": db_user.role
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -----------------------------
# CREATE TASK
# -----------------------------

@app.post("/tasks")
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return crud.create_task(
        db,
        task.title,
        task.description,
        task.assigned_to
    )


# -----------------------------
# GET TASKS
# -----------------------------

@app.get("/tasks")
def get_tasks(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.role in ["admin", "manager"]:
        return crud.get_tasks(db)

    return crud.get_user_tasks(db, user.id)


# -----------------------------
# UPDATE TASK
# -----------------------------

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.role not in ["admin", "manager", "user"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return crud.update_task(db, task_id, data.dict())


# -----------------------------
# DELETE TASK
# -----------------------------

@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete tasks")

    crud.delete_task(db, task_id)

    return {"message": "Task deleted successfully"}