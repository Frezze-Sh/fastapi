-- Таблица users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    hashed_password TEXT
);

-- Таблица categories
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    icon VARCHAR(50)
);

-- Таблица tasks
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    done BOOLEAN DEFAULT FALSE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    priority INTEGER DEFAULT 2,
    due_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estimated_minutes INTEGER
);

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_category_id ON tasks(category_id);
CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);

-- Начальные категории
INSERT INTO categories (name, description, color, icon)
VALUES
    ('Учеба', 'Задачи по учебе', '#0000FF', 'book'),
    ('Покупки', 'Список покупок', '#00FF00', 'cart'),
    ('Спорт', 'Тренировки', '#FFA5000', 'dumbbell'),
    ('Дом', 'Домашние дела', '#800080', 'home'),
    ('Хобби', 'Увлечения', '#00FFFF', 'gamepad')
ON CONFLICT (name) DO NOTHING;