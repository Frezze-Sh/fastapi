from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI
from typing import Optional


app = FastAPI()

@app.get("/")
def root():
    return {"Message":"Task Api"}

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None  # опциональное поле
    done: bool = False

@app.get("/tasks",response_model=list[Task])
def get_tasks():
    return [
        {"id":1, "title":"Пример задачи", "done":False},
        {"id":2, "title":"Ещё задача", "done":True}
    ]

if __name__ == "__main__":
    uvicorn.run("main2:app", reload=True)