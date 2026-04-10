# Kafka-based Query Processing Pipeline

## Обзор

Текущий pipeline обработки запроса выполняется синхронно внутри `QueryService.process()`. Новая архитектура разбивает pipeline на независимые этапы, связанные через **Kafka-топики**. Каждый этап читает данные из БД по ключу, выполняет свою работу, записывает результат обратно в БД и публикует ключ в следующий топик.

---

## Новая схема базы данных

### Таблица `query_processing` (вспомогательная модель)

Хранит промежуточное состояние обработки запроса. Связана 1:1 с `queries`.

```
query_processing
┌──────────────────────────────────────────┐
│ id              UUID, PK, default uuid4  │
│ query_id        UUID, FK → queries.id    │  UNIQUE
│ original_text   TEXT, NOT NULL           │
│ enriched_text   TEXT, NULLABLE           │
│ task_context    TEXT, NULLABLE           │
│ status          VARCHAR(50), NOT NULL    │  -- enum: pending, enriching, searching,
│                                          │  --   composing, generating, completed, failed
│ error_message   TEXT, NULLABLE           │
│ created_at      DATETIME, NOT NULL       │
│ updated_at      DATETIME, NULLABLE       │
└──────────────────────────────────────────┘
```

**Связь:** `queries.id` ← 1:1 → `query_processing.query_id`

### Обновлённая ER-диаграмма

```
users                        tasks (база знаний)
┌────────────────┐           ┌────────────────────┐
│ id (UUID, PK)  │           │ id (UUID, PK)      │
│ username       │           │ title              │
│ password_hash  │           │ text               │
│ created_at     │           │ task_url           │
└───────┬────────┘           │ solution           │
        │                    │ solution_url       │
        │ 1:N                │ comment            │
        ▼                    │ created_at         │
queries                      └─────────┬──────────┘
┌──────────────────┐                   │
│ id (UUID, PK)    │                   │
│ user_id (FK)     │       N:M         │
│ text             │◄─────────────────►│
│ response_text    │ query_similar_tasks│
│ created_at       │ (query_id,task_id)│
│ responded_at     │                   │
└───────┬──────────┘
        │
        │ 1:1
        ▼
query_processing
┌──────────────────────────┐
│ id (UUID, PK)            │
│ query_id (FK, UNIQUE)    │
│ original_text            │
│ enriched_text            │
│ task_context             │
│ status                   │
│ error_message            │
│ created_at               │
│ updated_at               │
└──────────────────────────┘
```

### SQLAlchemy-модель

```python
class QueryProcessing(Base):
    __tablename__ = "query_processing"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    query_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("queries.id"), unique=True,
    )
    original_text: Mapped[str] = mapped_column(Text)
    enriched_text: Mapped[str | None] = mapped_column(Text)
    task_context: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(onupdate=datetime.utcnow)

    query: Mapped["Query"] = relationship(back_populates="processing")
```

---

## Kafka-топики

| Топик | Producer | Consumer | Payload | Назначение |
|-------|----------|----------|---------|------------|
| `query.enrich` | API endpoint | Enrichment handler | `{ "processing_id": UUID }` | Запуск обогащения текста запроса |
| `query.search` | Enrichment handler | Search handler | `{ "processing_id": UUID }` | Запуск поиска похожих задач |
| `query.compose` | Search handler | Compose handler | `{ "processing_id": UUID }` | Запуск сборки контекста и промпта |
| `query.generate` | Compose handler | Generate handler | `{ "processing_id": UUID }` | Запуск генерации ответа через LLM |

**Формат сообщения во всех топиках единый:**

```json
{
  "processing_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

Каждый handler получает `processing_id`, загружает `QueryProcessing` из БД, выполняет свой этап, обновляет запись и публикует `processing_id` в следующий топик.

---

## Pipeline: поэтапная обработка

### Этап 0 — API Endpoint (точка входа)

**POST `/api/queries`**

```
Request Body:
{
    "text": "Найди кратчайший путь в графе"
}
```

Логика обработчика:

1. Получить `user_id` из JWT-токена.
2. Создать запись `Query`:
   ```python
   query = Query(user_id=user_id, text=request.text)
   session.add(query)
   ```
3. Создать запись `QueryProcessing`:
   ```python
   processing = QueryProcessing(
       query_id=query.id,
       original_text=request.text,
       status="pending",
   )
   session.add(processing)
   ```
4. `await session.flush()` — получить `processing.id`.
5. Опубликовать в топик `query.enrich`:
   ```python
   await broker.publish(
       {"processing_id": str(processing.id)},
       topic="query.enrich",
   )
   ```
6. Обновить `processing.status = "enriching"`.
7. `await session.commit()`.
8. Вернуть ответ клиенту:
   ```json
   {
       "query_id": "...",
       "processing_id": "...",
       "status": "enriching"
   }
   ```

---

### Этап 1 — Enrichment (обогащение запроса)

**Топик:** `query.enrich` → **Consumer:** `enrich_handler`

```python
@broker.subscriber("query.enrich")
async def enrich_handler(msg: ProcessingMessage) -> None:
    processing = await repo.get(msg.processing_id)

    enriched_text = await enricher.enrich(RawQuery(text=processing.original_text))

    processing.enriched_text = enriched_text
    processing.status = "searching"
    await repo.update(processing)

    await broker.publish(
        {"processing_id": str(processing.id)},
        topic="query.search",
    )
```

---

### Этап 2 — Search (поиск похожих задач)

**Топик:** `query.search` → **Consumer:** `search_handler`

```python
@broker.subscriber("query.search")
async def search_handler(msg: ProcessingMessage) -> None:
    processing = await repo.get(msg.processing_id)

    similar_tasks = await searcher.search(processing.enriched_text)

    # Сохраняем связи query <-> similar_tasks
    for task in similar_tasks:
        await repo.add_similar_task(processing.query_id, task.id)

    processing.status = "composing"
    await repo.update(processing)

    await broker.publish(
        {"processing_id": str(processing.id)},
        topic="query.compose",
    )
```

---

### Этап 3 — Compose (сборка контекста + промпта)

**Топик:** `query.compose` → **Consumer:** `compose_handler`

```python
@broker.subscriber("query.compose")
async def compose_handler(msg: ProcessingMessage) -> None:
    processing = await repo.get(msg.processing_id)

    # Загружаем similar_tasks из связи query.similar_tasks
    similar_tasks = await repo.get_similar_tasks(processing.query_id)

    task_context = await context_builder.build(similar_tasks)

    processing.task_context = task_context
    processing.status = "generating"
    await repo.update(processing)

    await broker.publish(
        {"processing_id": str(processing.id)},
        topic="query.generate",
    )
```

---

### Этап 4 — Generate (генерация ответа LLM)

**Топик:** `query.generate` → **Consumer:** `generate_handler`

```python
@broker.subscriber("query.generate")
async def generate_handler(msg: ProcessingMessage) -> None:
    processing = await repo.get(msg.processing_id)

    prepared = await composer.compose(
        original_text=processing.original_text,
        enriched_text=processing.enriched_text,
        task_context=processing.task_context,
    )

    response_text = await llm_client.generate(prepared.text)

    # Записываем ответ в Query
    query = await query_repo.get(processing.query_id)
    query.response_text = response_text
    query.responded_at = datetime.utcnow()
    await query_repo.update(query)

    processing.status = "completed"
    await repo.update(processing)
```

---

## Диаграмма потока данных

```
                        ┌──────────────────┐
   POST /api/queries    │  API Endpoint    │
   ─────────────────►   │                  │
                        │  1. Create Query │
   ◄─────────────────   │  2. Create QP    │
   { query_id,          │  3. Publish key  │
     processing_id,     └────────┬─────────┘
     status }                    │
                                 │  processing_id
                                 ▼
                        ┌─ query.enrich ──┐
                        │                 │
                        │ enrich_handler  │
                        │  read QP        │
                        │  enrich text    │
                        │  write QP       │
                        └────────┬────────┘
                                 │  processing_id
                                 ▼
                        ┌─ query.search ──┐
                        │                 │
                        │ search_handler  │
                        │  read QP        │
                        │  search Qdrant  │
                        │  save links     │
                        │  write QP       │
                        └────────┬────────┘
                                 │  processing_id
                                 ▼
                        ┌─ query.compose ─┐
                        │                 │
                        │ compose_handler │
                        │  read QP        │
                        │  build context  │
                        │  write QP       │
                        └────────┬────────┘
                                 │  processing_id
                                 ▼
                        ┌─ query.generate ┐
                        │                 │
                        │ generate_handler│
                        │  read QP        │
                        │  compose prompt │
                        │  call LLM       │
                        │  write Query    │  ← response_text, responded_at
                        │  write QP       │  ← status = "completed"
                        └─────────────────┘

QP = QueryProcessing
```

---

## Pydantic-схемы (Kafka messages)

```python
# app/presentation/streams/schemas/processing.py
from uuid import UUID
from pydantic import BaseModel

class ProcessingMessage(BaseModel):
    processing_id: UUID
```

---

## Pydantic-схемы (API)

```python
# app/presentation/api/schemas/query.py
from uuid import UUID
from pydantic import BaseModel

class CreateQueryRequest(BaseModel):
    text: str

class CreateQueryResponse(BaseModel):
    query_id: UUID
    processing_id: UUID
    status: str
```

---

## Обработка ошибок

Каждый handler оборачивается в try/except. При ошибке:

```python
processing.status = "failed"
processing.error_message = str(exception)
await repo.update(processing)
```

Сообщение **не перепубликуется** в следующий топик. Клиент может проверить статус через `GET /api/queries/{id}` (поле `status` из связанного `query_processing`).

---

## Статусная модель

```
pending → enriching → searching → composing → generating → completed
   │          │           │           │            │
   └──────────┴───────────┴───────────┴────────────┴──→ failed
```

---

## Итого: что меняется

| Было | Стало |
|------|-------|
| Синхронный pipeline в `QueryService.process()` | 4 независимых Kafka-consumer'а |
| Данные передаются через аргументы между методами | Данные хранятся в `query_processing`, передаётся только `processing_id` |
| Нет промежуточного состояния | Полная трассируемость: `original_text`, `enriched_text`, `task_context`, `status` |
| Одна модель `Query` | `Query` (результат) + `QueryProcessing` (промежуточное состояние) |
| Ответ синхронный | Ответ асинхронный: endpoint возвращает `processing_id`, клиент поллит статус |
