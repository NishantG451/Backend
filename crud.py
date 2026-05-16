from sqlalchemy.orm import Session
from models import Task


def create_task(db: Session, title, description, assigned_to):

    task = Task(
        title=title,
        description=description,
        assigned_to=assigned_to
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_tasks(db: Session):
    return db.query(Task).all()


def get_user_tasks(db: Session, user_id: int):
    return db.query(Task).filter(Task.assigned_to == user_id).all()


def update_task(db: Session, task_id, data):

    task = db.query(Task).filter(Task.id == task_id).first()

    for key, value in data.items():
        setattr(task, key, value)

    db.commit()

    return task


def delete_task(db: Session, task_id):

    task = db.query(Task).filter(Task.id == task_id).first()

    db.delete(task)
    db.commit()