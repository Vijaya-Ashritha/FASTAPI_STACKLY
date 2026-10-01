from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.schemas import TaskCreate, TaskResponse


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# CREATE TASK
@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate):
    connection = get_connection()

    existing_task = connection.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task.task_id,),
    ).fetchone()

    if existing_task:
        connection.close()
        raise HTTPException(
            status_code=400,
            detail="Task ID already exists",
        )

    created_date = datetime.now()

    connection.execute(
        """
        INSERT INTO tasks
        (
            task_id,
            task_title,
            description,
            priority,
            status,
            due_date,
            assigned_to,
            created_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task.task_id,
            task.task_title,
            task.description,
            task.priority.value,
            task.status.value,
            task.due_date.isoformat(),
            task.assigned_to,
            created_date.isoformat(),
        ),
    )

    connection.commit()
    connection.close()

    return {
        "task_id": task.task_id,
        "task_title": task.task_title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "due_date": task.due_date,
        "assigned_to": task.assigned_to,
        "created_date": created_date,
    }


# GET ALL TASKS
@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    assigned_to: str | None = Query(default=None),
):
    connection = get_connection()

    query = "SELECT * FROM tasks WHERE 1=1"
    parameters = []

    if status:
        query += " AND status = ?"
        parameters.append(status)

    if priority:
        query += " AND priority = ?"
        parameters.append(priority)

    if assigned_to:
        query += " AND assigned_to = ?"
        parameters.append(assigned_to)

    rows = connection.execute(query, parameters).fetchall()

    connection.close()

    tasks = []

    for row in rows:
        tasks.append(
            {
                "task_id": row["task_id"],
                "task_title": row["task_title"],
                "description": row["description"],
                "priority": row["priority"],
                "status": row["status"],
                "due_date": row["due_date"],
                "assigned_to": row["assigned_to"],
                "created_date": row["created_date"],
            }
        )

    return tasks


# GET TASK BY ID
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    connection = get_connection()

    task = connection.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()

    connection.close()

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    return {
        "task_id": task["task_id"],
        "task_title": task["task_title"],
        "description": task["description"],
        "priority": task["priority"],
        "status": task["status"],
        "due_date": task["due_date"],
        "assigned_to": task["assigned_to"],
        "created_date": task["created_date"],
    }


# UPDATE TASK
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskCreate):
    connection = get_connection()

    existing_task = connection.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()

    if not existing_task:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    connection.execute(
        """
        UPDATE tasks
        SET
            task_title = ?,
            description = ?,
            priority = ?,
            status = ?,
            due_date = ?,
            assigned_to = ?
        WHERE task_id = ?
        """,
        (
            task.task_title,
            task.description,
            task.priority.value,
            task.status.value,
            task.due_date.isoformat(),
            task.assigned_to,
            task_id,
        ),
    )

    connection.commit()

    updated_task = connection.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()

    connection.close()

    return {
        "task_id": updated_task["task_id"],
        "task_title": updated_task["task_title"],
        "description": updated_task["description"],
        "priority": updated_task["priority"],
        "status": updated_task["status"],
        "due_date": updated_task["due_date"],
        "assigned_to": updated_task["assigned_to"],
        "created_date": updated_task["created_date"],
    }


# DELETE TASK
@router.delete("/{task_id}")
def delete_task(task_id: int):
    connection = get_connection()

    existing_task = connection.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,),
    ).fetchone()

    if not existing_task:
        connection.close()
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    connection.execute(
        "DELETE FROM tasks WHERE task_id = ?",
        (task_id,),
    )

    connection.commit()
    connection.close()

    return {
        "message": "Task deleted successfully"
    }