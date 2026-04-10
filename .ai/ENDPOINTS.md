# API Endpoints

---

## Auth

### POST `/api/auth/register`

Регистрация нового пользователя.

**Auth:** не требуется

**Request Body:**
```json
{
  "username": "string (3–50 символов)",
  "password": "string (8–128 символов)"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "username": "string",
  "created_at": "datetime"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 201 | Пользователь успешно создан |
| 409 | Username уже занят |
| 422 | Ошибка валидации (невалидные поля) |

---

### POST `/api/auth/login`

Авторизация, возвращает JWT-токен.

**Auth:** не требуется

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response 200:**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 200 | Успешная авторизация |
| 401 | Неверный username или password |
| 422 | Ошибка валидации |

---

## Tasks (база знаний задач)

### GET `/api/tasks/{id}`

Получить задачу по ID.

**Auth:** JWT

**Path Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| id | uuid | ID задачи |

**Response 200:**
```json
{
  "id": "uuid",
  "title": "string",
  "text": "string",
  "task_url": "string | null",
  "solution": "string | null",
  "solution_url": "string | null",
  "comment": "string | null",
  "created_at": "datetime"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 200 | Задача найдена |
| 401 | Отсутствует или невалидный JWT |
| 404 | Задача не найдена |

---

### POST `/api/tasks`

Создать задачу.

**Auth:** JWT

**Request Body:**
```json
{
  "title": "string",
  "text": "string",
  "task_url": "string | null",
  "solution": "string | null",
  "solution_url": "string | null",
  "comment": "string | null"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "title": "string",
  "text": "string",
  "task_url": "string | null",
  "solution": "string | null",
  "solution_url": "string | null",
  "comment": "string | null",
  "created_at": "datetime"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 201 | Задача создана |
| 401 | Отсутствует или невалидный JWT |
| 422 | Ошибка валидации |

---

### PUT `/api/tasks/{id}`

Обновить задачу.

**Auth:** JWT

**Path Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| id | uuid | ID задачи |

**Request Body:**
```json
{
  "title": "string",
  "text": "string",
  "task_url": "string | null",
  "solution": "string | null",
  "solution_url": "string | null",
  "comment": "string | null"
}
```

**Response 200:**
```json
{
  "id": "uuid",
  "title": "string",
  "text": "string",
  "task_url": "string | null",
  "solution": "string | null",
  "solution_url": "string | null",
  "comment": "string | null",
  "created_at": "datetime"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 200 | Задача обновлена |
| 401 | Отсутствует или невалидный JWT |
| 404 | Задача не найдена |
| 422 | Ошибка валидации |

---

### DELETE `/api/tasks/{id}`

Удалить задачу.

**Auth:** JWT

**Path Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| id | uuid | ID задачи |

**Response 204:** No Content

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 204 | Задача удалена |
| 401 | Отсутствует или невалидный JWT |
| 404 | Задача не найдена |

---

## Queries (запросы на разбор)

### POST `/api/queries`

Создать запрос на разбор задачи. Ответ приходит асинхронно через Kafka.

**Auth:** JWT

**Request Body:**
```json
{
  "text": "string"
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "text": "string",
  "response_text": null,
  "created_at": "datetime",
  "responded_at": null
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 201 | Запрос создан |
| 401 | Отсутствует или невалидный JWT |
| 422 | Ошибка валидации |

---

### GET `/api/queries`

Список запросов текущего пользователя (пагинация).

**Auth:** JWT

**Query Parameters:**
| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| page | int | 1 | Номер страницы |
| size | int | 10 | Размер страницы |

**Response 200:**
```json
{
  "items": [
    {
      "id": "uuid",
      "text": "string",
      "response_text": "string | null",
      "created_at": "datetime",
      "responded_at": "datetime | null"
    }
  ],
  "total": "int",
  "page": "int",
  "size": "int"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 200 | Список запросов |
| 401 | Отсутствует или невалидный JWT |
| 422 | Ошибка валидации (невалидные page/size) |

---

### GET `/api/queries/{id}`

Получить запрос с ответом.

**Auth:** JWT

**Path Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| id | uuid | ID запроса |

**Response 200:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "text": "string",
  "response_text": "string | null",
  "created_at": "datetime",
  "responded_at": "datetime | null"
}
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 200 | Запрос найден |
| 401 | Отсутствует или невалидный JWT |
| 403 | Запрос принадлежит другому пользователю |
| 404 | Запрос не найден |

---

### GET `/api/queries/{id}/similar-tasks`

Получить похожие задачи для запроса.

**Auth:** JWT

**Path Parameters:**
| Параметр | Тип | Описание |
|----------|-----|----------|
| id | uuid | ID запроса |

**Response 200:**
```json
[
  {
    "id": "uuid",
    "title": "string",
    "task_url": "string | null",
    "solution_url": "string | null"
  }
]
```

**Коды ответа:**
| Код | Описание |
|-----|----------|
| 200 | Список похожих задач |
| 401 | Отсутствует или невалидный JWT |
| 403 | Запрос принадлежит другому пользователю |
| 404 | Запрос не найден |
