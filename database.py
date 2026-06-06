# import sqlite3
#
# try:
#     conn = sqlite3.connect("tasks.db")
#     print("Подключение к SQLite успешно!")
#
#     cursor = conn.cursor()
#     cursor.execute("SELECT sqlite_version();")
#     version = cursor.fetchone()
#     print(f"Версия SQLite: {version[0]}")
#
#     conn.close()
#
# except Exception as e:
#     print(f"Ошибка: {e}")

# import psycopg2
# import sys
#
# try:
#     print("Попытка подключения...")
#     conn = psycopg2.connect(
#         host="127.0.0.1",
#         port=5433,
#         database="taskdb",
#         user="postgres",
#         password="mysecretpassword",
#         connect_timeout=5
#     )
#     print("Подключение к PostgreSQL успешно!")
#
#     cur = conn.cursor()
#     cur.execute("SELECT version();")
#     version = cur.fetchone()
#     print(f"Версия PostgreSQL: {version[0]}")
#
#     cur.close()
#     conn.close()
#
# except Exception as e:
#     print(f"Ошибка: {type(e).__name__}: {e}")



import psycopg2

# Параметры подключения (твой рабочий вариант)
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 5433,
    "database": "taskdb",
    "user": "postgres",
    "password": "mysecretpassword"
}

def get_connection():
    """Возвращает соединение с базой данных"""
    return psycopg2.connect(**DB_CONFIG)

# Проверка подключения (опционально)
if __name__ == "__main__":
    try:
        conn = get_connection()
        print("Подключение к PostgreSQL успешно!")
        conn.close()
    except Exception as e:
        print(f"Ошибка: {e}")