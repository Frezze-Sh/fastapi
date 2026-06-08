from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

app = FastAPI()

books = [
    {
     "id":1,
     "title":"Асинхронность в Python",
     "author":"Метью"
    },
    {
     "id":2,
     "title":"Бекэнд разработка в Python",
     "author":"Артём"
    }
]

class New_Book(BaseModel):
    title: str
    author: str

@app.get("/books", tags=["Книги"], summary="Получить все книги")
def read_books():
    return books

@app.get("/books/{book_id}", tags=["Книги"], summary="Получить одну книгу")
def get_book(book_id:int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


@app.post("/books")
def create_book(new_book:New_Book):
    books.append({
        "id":len(books)+1,
        "title":new_book.title,
        "author":new_book.author
    })
    return {"success":True}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
#----------------------------------------------------------------------------------------
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr, ConfigDict
#BaseModel — это базовый класс, от которого наследуются все модели данных в Pydantic.
#Field - это функция, которая используется для добавления метаданных и дополнительных правил валидации к полю модели
# Для более строгой валидации данных
#EmailStr - это подкласс str (строки) с дополнительной, строгой валидацией формата email
data_wo_age = {
    "email":"abc@mail.ru",
    "bio":None,
    "brthd":"2022",#1)При запуске с этими 2 доп-ми параметрами и без обозначения их в классе UserSChema ошибки не будет
    "gender":"male"#При передаче данных в Pyd-c с полями, которые не определены в схеме, они просто игнорируются(особенность Py-c)
}
data = {
    "email": "abc@mail.ru",
    "bio": None,
    "age":12
}
class UserSChema(BaseModel):
    email:EmailStr
    bio:str | None = Field(max_length=100)

#1) Но иногда нам надо что эти избыточные данные не игнорировались
#Для этого можно использовать ConfigDict (не разрешает доп-ые input-ы)
    model_config = ConfigDict(extra="forbid")

class UserAgeSchema(UserSChema):
    age:int = Field(ge=0, le=120)
print(repr(UserSChema(**data_wo_age)))#repr - для более немного информативного вывода
print(repr(UserAgeSchema(**data)))
#-----------------------------------------------------------------------------
from pydantic import BaseModel, Field, EmailStr
from fastapi import FastAPI
app = FastAPI()
users = []
data_wo_age = {
    "email":"abc@mail.ru",
    "bio":None
}
class UserSChema(BaseModel):
    email:EmailStr
    bio:str | None = Field(max_length=100)
@app.get("/users")
def get_users():
    return users
@app.post("/users")
def add_users(user:UserSChema):
    users.append(user)