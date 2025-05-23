# Сервис для работы с направленными ациклическими графами (DAG)

Сервис предоставляет API для хранения и отображения направленных ациклических графов с хранением данных в PostgreSQL.

Сервис позволяет:
- Добавить граф по списку вершин и ребер
- Получить граф по его идентификатору в виде списка вершин и ребер
- Получить граф по его идентификатору в виде списка смежности ребер
- Получить граф по его идентификатору в виде транспонированного списка смежности ребер
- Удалить вершину из графа по его идентификатору и имени вершины


## Технологии
- Python 3.11
- FastAPI
- PostgreSQL 13
- SQLAlchemy
- Контейнеризация: Docker + docker compose

## Описание архитектуры
- При старте приложение подключается к базе данных PostgreSQL и создает таблицы `graphs`, `nodes` и `edges`.
- При создании графа выполняется проверка на наличие хотя бы одной вершины. Затем граф проверяется на ацикличность с помощью нерекурсивного DFS, а условия в таблицах БД проверяют граф на отсутствие дубликатов вершин и дубликатов ребер.
- Схемы данных валидируются с помощью Pydantic.
- Для работы с базой данных используется SQLAlchemy.
- Используются health-check и depends для запуска контейнеров в правильном порядке.

## Запуск

### Через Docker Compose
1. У вас должен быть [установлен](https://docs.docker.com/engine/install/) Docker и Docker Compose
2. Склонируйте репозиторий:
```bash
git clone https://github.com/kisorimaD/fastapi-dag-service.git
cd fastapi-dag-service
```
3. Запустите сервис с помощью Docker Compose:
```bash
docker compose up
```
Сервис работает на порту 8080. Вы можете получить доступ к API по адресу `http://localhost:8080`.

### Локально
1. Склонируйте репозиторий:
```bash
git clone https://github.com/kisorimaD/fastapi-dag-service.git
cd fastapi-dag-service
```
2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv .venv
```
Для Linux и macOS:
```bash
source .venv/bin/activate
```

Для Windows:
```bash
.venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```
4. Запустите PostgreSQL (можно через Docker):
```bash
docker run --name postgres -e POSTGRES_DB=db -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:13
```
Или, находясь в корне репозитория
```bash
docker compose up postgres
```
5. Установите переменные окружения для подключения к базе данных:
```bash
export DATABASE_URL=postgresql+asynpcg://user:password@localhost/db
```
Для Windows:
```bash
set DATABASE_URL=postgresql+asynpcg://user:password@localhost/db
```
6. Запустите сервис:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## Запуск тестов
### Через Docker Compose
1. Сервис должен быть запущен.
2. Запустите тесты с помощью Docker Compose:
```bash
docker compose exec dag-api pytest tests/
```
### Локально
1. База данных должна быть запущена.
2. Активируйте виртуальное окружение и установите зависимости, как описано в разделе "Локально".
3. Запустите тесты:
```bash
pytest tests/
```

> При запуске с флагом `-k "not slow"` можно пропустить медленные тесты

## API Endpoints

> FastAPI автоматически генерирует интерактивную документацию для API по адресу [`/docs`](http://localhost:8080/docs). 

### `POST /api/graph`
Создает новый граф в базе данных.
```json
{
    "nodes": [
        {"name": "a"},
        {"name": "b"},
        {"name": "c"}
    ],

    "edges": [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "c"}
    ]
}
```

### `GET /api/graph/{graph_id}`
Получает граф по его идентификатору в виде списка вершин и ребер.
```json
{
    "nodes": [
        {"name": "a"},
        {"name": "b"},
        {"name": "c"}
    ],

    "edges": [
        {"source": "a", "target": "b"},
        {"source": "b", "target": "c"}
    ]
}
```

### `GET /api/graph/{graph_id}/adjacency_list`
Получает граф по его идентификатору в виде списка вершин и списка смежности ребер.
```json
{
    "adjacency_list": {
        "a": ["b"],
        "b": ["c"],
        "c": []
    }
}
```

### `GET /api/graph/{graph_id}/reverse_adjacency_list`
Получает граф по его идентификатору в виде списка вершин и транспонированного списка смежности ребер.
```json
{
    "reverse_adjacency_list": {
        "a": [],
        "b": ["a"],
        "c": ["b"]
    }
}
```

### `DELETE /api/graph/{graph_id}/node/{node_name}`
Удаляет вершину из графа по его идентификатору и имени вершины.
Отвечает 204 No Content в случае успешного удаления.
