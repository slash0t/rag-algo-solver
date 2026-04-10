# RAG Algo Solver — Структура проекта

## Обзор

**RAG Algo Solver** — сервис для решения алгоритмических задач с использованием RAG (Retrieval-Augmented Generation). Пользователь отправляет запрос, система находит похожие задачи в базе знаний (Qdrant), обогащает контекст и генерирует ответ через LLM.

**Стек:** FastAPI, SQLAlchemy (async), PostgreSQL 16, Qdrant, Apache Kafka, FastStream, LangChain, dependency-injector, Alembic, Pydantic Settings.

---

## Дерево каталогов

```
coursework/
├── app/                            # Основной пакет приложения
│   ├── __main__.py                 # Точка входа (uvicorn, порт 8000)
│   ├── container.py                # DI-контейнер (dependency-injector)
│   │
│   ├── settings/                   # Конфигурация (Pydantic Settings)
│   │   ├── postgres.py             #   PostgresConfig (host, port, user, password, db)
│   │   ├── kafka.py                #   KafkaConfig (bootstrap_servers)
│   │   ├── yandex_cloud.py         #   YandexCloudConfig (api_key, folder, model)
│   │   └── qdrant.py               #   QdrantConfig (host, port)
│   │
│   ├── domain/                     # Доменный слой (бизнес-логика)
│   │   ├── exceptions.py           #   DomainException — базовый класс исключений
│   │   ├── models/                 #   Доменные модели (dataclasses)
│   │   │   └── query.py            #     RawQuery, SimilarTask, IntermediateQuery,
│   │   │                           #     PreparedQuery, QueryResponse
│   │   ├── services/               #   Сервисы и абстракции
│   │   │   ├── query_service.py    #     QueryService — оркестратор pipeline (legacy)
│   │   │   ├── llm_client.py       #     LLMClient (ABC) — генерация ответа
│   │   │   ├── query_enricher.py   #     QueryEnricher (ABC) — обогащение запроса
│   │   │   ├── prompt_composer.py  #     PromptComposer (ABC) — сборка промпта
│   │   │   ├── similar_task_searcher.py  # SimilarTaskSearcher (ABC) — поиск похожих задач
│   │   │   ├── task_context_builder.py   # TaskContextBuilder (ABC) — сборка контекста
│   │   │   └── enrichment/         #     Pipeline обогащения запросов
│   │   │       ├── block.py        #       EnrichmentBlock (ABC) — блок обработки
│   │   │       └── pipeline.py     #       EnrichmentPipeline — цепочка блоков
│   │   └── repositories/           #   Абстракции репозиториев
│   │       ├── query.py            #     QueryRepository (ABC) — CRUD для Query
│   │       └── query_processing.py #     QueryProcessingRepository (ABC) — CRUD для QueryProcessing
│   │
│   ├── infrastructure/             # Инфраструктурный слой (техническая реализация)
│   │   ├── database/               #   PostgreSQL
│   │   │   ├── models.py           #     ORM-модели: User, Task, Query,
│   │   │   │                       #     QueryProcessing, QuerySimilarTask, ProcessingStatus
│   │   │   ├── session.py          #     Фабрика async-сессий
│   │   │   └── repositories/       #     Реализации репозиториев
│   │   │       ├── query.py        #       SQLQueryRepository
│   │   │       └── query_processing.py #   SQLQueryProcessingRepository
│   │   ├── adapters/               #   Адаптеры к внешним сервисам
│   │   │   ├── enricher/           #     Реализации QueryEnricher
│   │   │   │   └── passthrough_query_enricher.py  # PassthroughQueryEnricher
│   │   │   ├── search/             #     Реализации SimilarTaskSearcher
│   │   │   │   └── empty_similar_task_searcher.py # EmptySimilarTaskSearcher
│   │   │   ├── context/            #     Реализации TaskContextBuilder
│   │   │   │   └── plain_task_context_builder.py  # PlainTaskContextBuilder
│   │   │   ├── composer/           #     Реализации PromptComposer
│   │   │   │   └── plain_prompt_composer.py       # PlainPromptComposer
│   │   │   ├── llm/                #     Реализации LLMClient
│   │   │   │   ├── echo_llm_client.py             # EchoLLMClient (тестовый)
│   │   │   │   └── yandex_cloud_llm_client.py     # YandexCloudLLMClient
│   │   │   └── qdrant/             #     Реализации SimilarTaskSearcher (Qdrant, TODO)
│   │   └── rag/                    #   Утилиты RAG-pipeline (TODO)
│   │
│   └── presentation/               # Слой представления (входные точки)
│       ├── api/                    #   REST API (FastAPI)
│       │   ├── app.py              #     Фабрика FastAPI-приложения
│       │   ├── routers/            #     Обработчики маршрутов
│       │   │   ├── ping.py         #       GET /ping — health check
│       │   │   └── query.py        #       POST /api/queries — создание запроса
│       │   └── schemas/            #     Pydantic-схемы запросов/ответов
│       │       └── query.py        #       CreateQueryRequest, CreateQueryResponse
│       └── streams/                #   Kafka-потоки (FastStream)
│           ├── app.py              #     KafkaBroker + FastStream приложение
│           ├── handlers/           #     Обработчики Kafka-сообщений
│           │   ├── enrich.py       #       enrich_handler (топик query.enrich)
│           │   ├── search.py       #       search_handler (топик query.search)
│           │   ├── compose.py      #       compose_handler (топик query.compose)
│           │   └── generate.py     #       generate_handler (топик query.generate)
│           └── schemas/            #     Схемы Kafka-сообщений
│               └── processing.py   #       ProcessingMessage { processing_id: UUID }
│
├── migrations/                     # Alembic-миграции
│   ├── env.py                      #   Конфигурация Alembic (async)
│   ├── script.py.mako              #   Шаблон миграций
│   └── versions/
│       ├── dce56e4c70b2_...py      #   Начальная миграция (users, tasks, queries,
│       │                           #   query_similar_tasks)
│       └── a1b2c3d4e5f6_...py      #   Миграция: query_processing + queries.user_id nullable
│
├── docker/                         # Docker-конфигурации сервисов
│   ├── postgres.yml                #   PostgreSQL 16
│   ├── kafka.yml                   #   Apache Kafka
│   └── qdrant.yml                  #   Qdrant vector DB
│
├── docker-compose.yml              # Агрегирует docker/*.yml
├── alembic.ini                     # Настройки Alembic
├── pyproject.toml                  # Зависимости (Poetry), настройки Ruff
├── Makefile                        # Команды: run, migrate, infra-up/down, lint
├── env.json                        # Переменные окружения
├── ENDPOINTS.md                    # Описание API-эндпоинтов
└── openapi.yaml                    # OpenAPI-спецификация
```

---

## Архитектурные слои

Проект построен по принципам **Clean Architecture**. Зависимости направлены внутрь: presentation -> domain <- infrastructure.

### 1. Domain (`app/domain/`)

Ядро приложения. Не зависит от фреймворков и инфраструктуры.

| Компонент | Ответственность |
|-----------|----------------|
| `models/query.py` | Доменные dataclass-модели, описывающие жизненный цикл запроса |
| `services/query_service.py` | Оркестратор — координирует pipeline обработки запроса (legacy, заменён Kafka-pipeline) |
| `services/llm_client.py` | ABC-интерфейс для генерации текста через LLM |
| `services/query_enricher.py` | ABC-интерфейс для обогащения пользовательского запроса |
| `services/similar_task_searcher.py` | ABC-интерфейс для семантического поиска похожих задач |
| `services/task_context_builder.py` | ABC-интерфейс для формирования контекста из найденных задач |
| `services/prompt_composer.py` | ABC-интерфейс для финальной сборки промпта |
| `services/enrichment/` | Реализация паттерна Chain of Responsibility для обогащения |
| `exceptions.py` | Базовый класс доменных исключений |
| `repositories/query.py` | ABC-интерфейс репозитория для Query |
| `repositories/query_processing.py` | ABC-интерфейс репозитория для QueryProcessing |

### 2. Infrastructure (`app/infrastructure/`)

Технические реализации абстракций доменного слоя.

| Компонент | Ответственность |
|-----------|----------------|
| `database/models.py` | SQLAlchemy ORM-модели (User, Task, Query, QueryProcessing, QuerySimilarTask) + ProcessingStatus enum |
| `database/session.py` | Фабрика `async_sessionmaker` из `PostgresConfig` |
| `database/repositories/query.py` | `SQLQueryRepository` — реализация репозитория Query |
| `database/repositories/query_processing.py` | `SQLQueryProcessingRepository` — реализация репозитория QueryProcessing |
| `adapters/enricher/` | `PassthroughQueryEnricher` — реализует `QueryEnricher` |
| `adapters/search/` | `EmptySimilarTaskSearcher` — реализует `SimilarTaskSearcher` |
| `adapters/context/` | `PlainTaskContextBuilder` — реализует `TaskContextBuilder` |
| `adapters/composer/` | `PlainPromptComposer` — реализует `PromptComposer` |
| `adapters/llm/` | `EchoLLMClient`, `YandexCloudLLMClient` — реализуют `LLMClient` |
| `adapters/qdrant/` | Адаптер Qdrant — реализует `SimilarTaskSearcher` (TODO) |
| `rag/` | Вспомогательные утилиты RAG-pipeline (TODO) |

### 3. Presentation (`app/presentation/`)

Входные точки в систему — HTTP API и Kafka-потоки.

| Компонент | Ответственность |
|-----------|----------------|
| `api/app.py` | Фабрика FastAPI-приложения, подключает роутеры |
| `api/routers/ping.py` | GET `/ping` — health check |
| `api/routers/query.py` | POST `/api/queries` — создание запроса, запуск Kafka-pipeline |
| `api/schemas/query.py` | `CreateQueryRequest`, `CreateQueryResponse` — Pydantic-схемы |
| `streams/app.py` | `KafkaBroker` (из `KafkaConfig`) + `FastStream` приложение |
| `streams/handlers/enrich.py` | Обогащение запроса (топик `query.enrich`) |
| `streams/handlers/search.py` | Поиск похожих задач (топик `query.search`) |
| `streams/handlers/compose.py` | Сборка контекста (топик `query.compose`) |
| `streams/handlers/generate.py` | Генерация ответа LLM + запись в Query (топик `query.generate`) |
| `streams/schemas/processing.py` | `ProcessingMessage` — единый формат Kafka-сообщения |

### 4. Settings (`app/settings/`)

Конфигурация через переменные окружения (Pydantic Settings): `PostgresConfig`, `KafkaConfig`, `YandexCloudConfig`, `QdrantConfig`.

### 5. DI-контейнер (`app/container.py`)

`AppContainer` (dependency-injector `DeclarativeContainer`) — точка сборки всех зависимостей: конфиги, фабрика сессий, репозитории (`query_repo`, `processing_repo`), адаптеры (`enricher`, `searcher`, `context_builder`, `composer`, `llm_client`). Синглтон `APP_CONTAINER`.

---

## Pipeline обработки запроса (Kafka-based)

Каждый этап pipeline связан через отдельный Kafka-топик. В сообщениях передаётся только `processing_id` — все данные читаются/пишутся через БД (таблица `query_processing`).

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

### Kafka-топики

| Топик | Producer | Consumer | Назначение |
|-------|----------|----------|------------|
| `query.enrich` | API endpoint | `enrich_handler` | Запуск обогащения текста |
| `query.search` | `enrich_handler` | `search_handler` | Запуск поиска похожих задач |
| `query.compose` | `search_handler` | `compose_handler` | Запуск сборки контекста |
| `query.generate` | `compose_handler` | `generate_handler` | Запуск генерации ответа LLM |

### Статусная модель

```
pending → enriching → searching → composing → generating → completed
   │          │           │           │            │
   └──────────┴───────────┴───────────┴────────────┴──→ failed
```

---

## Схема базы данных

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
│ user_id (FK,NULL)│       N:M         │
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

---

## API-эндпоинты

| Метод | Путь | Статус | Назначение |
|-------|------|--------|-----------|
| GET | `/ping` | Реализован | Health check |
| POST | `/api/queries` | Реализован | Создать запрос (асинхронная обработка через Kafka) |
| POST | `/api/auth/register` | TODO | Регистрация пользователя |
| POST | `/api/auth/login` | TODO | Аутентификация, получение JWT |
| GET | `/api/tasks/{id}` | TODO | Получить задачу из базы знаний |
| POST | `/api/tasks` | TODO | Создать задачу |
| PUT | `/api/tasks/{id}` | TODO | Обновить задачу |
| DELETE | `/api/tasks/{id}` | TODO | Удалить задачу |
| GET | `/api/queries` | TODO | Список запросов пользователя (с пагинацией) |
| GET | `/api/queries/{id}` | TODO | Получить запрос с ответом |
| GET | `/api/queries/{id}/similar-tasks` | TODO | Похожие задачи для запроса |

---

## Makefile-команды

| Команда | Действие |
|---------|---------|
| `make run` | Запуск FastAPI (uvicorn, порт 8000) |
| `make migrate` | Применить миграции Alembic |
| `make migration name="..."` | Создать новую миграцию |
| `make infra-up` | Поднять инфраструктуру (Docker) |
| `make infra-down` | Остановить инфраструктуру |
| `make install` | Установить зависимости (Poetry) |
| `make lint` / `make format` | Линтинг / форматирование (Ruff) |

---

## Граф зависимостей между модулями

```
app.settings ──────────────────────────────────────────────────┐
                                                                │
app.presentation.api ──► app.domain.repositories ◄── app.infrastructure.database.repositories
app.presentation.api ──► app.presentation.streams.app (broker)
                                                                │
app.presentation.streams.handlers ──► app.domain.repositories ◄─┘
app.presentation.streams.handlers ──► app.domain.services (enricher, searcher, etc.)
                              │
                              ▼
                         app.domain.models
```

**Правило:** доменный слой не импортирует ничего из `infrastructure` и `presentation`. Инфраструктурные адаптеры реализуют абстракции домена. Presentation вызывает доменные сервисы и репозитории. Связывание — через DI-контейнер (`container.py`).
