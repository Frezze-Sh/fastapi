from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import Optional, List
from datetime import datetime
from database import get_connection
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="Task Manager API", description="API для управления задачами")

# Pydantic модели

class TaskCreate(BaseModel):
    """Модель для создания задачи (не требует id, created_at и т.д.)"""
    title: str
    description: Optional[str] = None
    priority: Optional[int] = 2
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None
    user_id: int


class TaskUpdate(BaseModel):
    """Модель для обновления задачи (все поля опциональны)"""
    title: Optional[str] = None
    description: Optional[str] = None
    done: Optional[bool] = None
    priority: Optional[int] = None
    estimated_minutes: Optional[int] = None
    category_id: Optional[int] = None


class TaskResponse(BaseModel):
    """Модель для ответа (все поля, которые есть в БД)"""
    id: int
    title: str
    description: Optional[str] = None
    done: bool
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    priority: int
    created_at: datetime
    updated_at: datetime
    estimated_minutes: Optional[int] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


# Модели для пользователей
class UserCreate(BaseModel):
    name: str
    email: str
    is_active: Optional[bool] = True


class UserResponse(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime

class UserDeleteResponse(BaseModel):
    """Модель ответа при успешном удалении пользователя"""
    message: str
    deleted_user: UserResponse

# Эндпоинты

@app.get("/")
def root():
    return {"message": "Task API работает с PostgreSQL!"}


# Эндпоинты для пользователей

@app.get("/users", response_model=List[UserResponse])
def get_all_users():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, email, is_active, created_at FROM users ORDER BY id")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(u) for u in users]


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        INSERT INTO users (name, email, is_active)
        VALUES (%s, %s, %s)
        RETURNING id, name, email, is_active, created_at
    """, (user.name, user.email, user.is_active))
    new_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return dict(new_user)


@app.get("/users/{user_id}/tasks", response_model=List[TaskResponse])
def get_tasks_by_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    cur.execute("""
        SELECT id, title, description, done, user_id, category_id, 
               priority, created_at, updated_at, estimated_minutes
        FROM tasks 
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))
    tasks = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(t) for t in tasks]


@app.delete("/users/{user_id}", response_model=UserDeleteResponse)
def delete_user(user_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            DELETE FROM users 
            WHERE id = %s 
            RETURNING id, name, email, is_active, created_at
        """, (user_id,))

        deleted_user = cur.fetchone()

        if not deleted_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        conn.commit()

        return {
            "message": f"Пользователь '{deleted_user['name']}' (ID: {deleted_user['id']}) и все его задачи успешно удалены",
            "deleted_user": dict(deleted_user)
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера при удалении пользователя: {str(e)}")
    finally:
        cur.close()
        conn.close()

# Эндпоинты для категорий

@app.get("/categories", response_model=List[CategoryResponse])
def get_all_categories():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, description, color, icon FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(c) for c in categories]


# Эндпоинты для задач

@app.get("/tasks", response_model=List[TaskResponse])
def get_all_tasks(category_id: Optional[int] = None):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if category_id is not None:
        cur.execute("SELECT id FROM categories WHERE id = %s", (category_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=404, detail="Категория не найдена")

        cur.execute("""
            SELECT id, title, description, done, user_id, category_id, 
                   priority, created_at, updated_at, estimated_minutes
            FROM tasks 
            WHERE category_id = %s
            ORDER BY created_at DESC
        """, (category_id,))
    else:
        cur.execute("""
            SELECT id, title, description, done, user_id, category_id, 
                   priority, created_at, updated_at, estimated_minutes
            FROM tasks
            ORDER BY created_at DESC
        """)

    tasks = cur.fetchall()
    cur.close()
    conn.close()

    return [dict(t) for t in tasks]


@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            INSERT INTO tasks (title, description, priority, estimated_minutes, category_id, user_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, title, description, done, user_id, category_id,
                      priority, created_at, updated_at, estimated_minutes
        """, (
            task.title, task.description, task.priority,
            task.estimated_minutes, task.category_id, task.user_id
        ))
        new_task = cur.fetchone()
        conn.commit()
    except psycopg2.errors.ForeignKeyViolation:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Ошибка: указанная категория (category_id) или пользователь (user_id) не найдены в базе данных."
        )
    finally:
        cur.close()
        conn.close()

    return dict(new_task)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, title, description, done, user_id, category_id,
               priority, created_at, updated_at, estimated_minutes
        FROM tasks WHERE id = %s
    """, (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()

    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return dict(task)


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    existing = cur.fetchone()
    if not existing:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Задача не найдена")

    cur.execute("""
        UPDATE tasks 
        SET title = COALESCE(%s, title),
            description = COALESCE(%s, description),
            done = COALESCE(%s, done),
            priority = COALESCE(%s, priority),
            estimated_minutes = COALESCE(%s, estimated_minutes),
            category_id = COALESCE(%s, category_id),
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, title, description, done, user_id, category_id,
                  priority, created_at, updated_at, estimated_minutes
    """, (
        task.title, task.description, task.done, task.priority,
        task.estimated_minutes, task.category_id, task_id
    ))

    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return dict(updated)


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id", (task_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not deleted:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return {"message": f"Задача {task_id} удалена"}

# эндпоинт для отметки конкретной задачи как выполненной
@app.patch("/tasks/{task_id}/done", response_model=TaskResponse)
def mark_done(task_id: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        UPDATE tasks
        SET done = TRUE, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, title, description, done, user_id, category_id,
                  priority, created_at, updated_at, estimated_minutes
    """, (task_id,))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not updated:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return dict(updated)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)