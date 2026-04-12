# Frontend — RAG Algo Solver

## Обзор

Простой фронтенд на Node.js (Express) с ванильным HTML/CSS/JS. Все файлы расположены в папке `front/`.

**Стек:** Express, http-proxy-middleware, vanilla HTML/CSS/JS.

---

## Структура

```
front/
├── package.json             # Зависимости (Express, http-proxy-middleware)
├── server.js                # Express-сервер: статика + прокси /api → backend
└── public/
    ├── index.html           # Единственная HTML-страница (SPA)
    ├── css/
    │   └── style.css        # Стили (палитра: #213448, #547792, #94B4C1, #EAE0CF)
    └── js/
        ├── api.js           # API-клиент (fetch, JWT, localStorage)
        ├── auth.js          # Логика авторизации/регистрации
        └── queries.js       # Логика работы с запросами
```

---

## Запуск

```bash
cd front
npm install
npm start
```

Фронтенд запустится на `http://localhost:3000`, проксируя `/api/*` на `http://localhost:8000` (бэкенд).

Переменная окружения `API_URL` позволяет изменить адрес бэкенда:

```bash
API_URL=http://backend:8000 npm start
```

---

## Страницы и состояния

### 1. Авторизация (`#auth-page`)

- Форма **входа**: username + password → `POST /api/auth/login` → JWT сохраняется в `localStorage`
- Форма **регистрации**: username + password + подтверждение → `POST /api/auth/register` → автоматический вход
- Переключение между формами по ссылкам

### 2. Основная страница (`#app-page`)

Двухколоночный layout:

**Сайдбар (слева):**
- Имя пользователя + кнопка «Выйти»
- Кнопка «+ Новый запрос»
- История запросов с пагинацией (`GET /api/queries?page=N&size=15`)
- Каждый элемент показывает текст запроса, дату и статус (цветной индикатор)

**Основная область (справа) — 4 состояния:**

| Состояние | ID | Описание |
|---|---|---|
| Пусто | `state-empty` | Нет выбранного запроса, предложение создать новый |
| Создание | `state-create` | Форма ввода текста задачи → `POST /api/queries` |
| Обработка | `state-processing` | Спиннер + текст запроса; polling каждые 3 сек (`GET /api/queries/{id}`) |
| Результат | `state-result` | Текст запроса, ответ LLM, похожие задачи (`GET /api/queries/{id}/similar-tasks`) |

---

## Используемые API-эндпоинты

| Эндпоинт | Метод | Где используется |
|---|---|---|
| `/api/auth/register` | POST | Регистрация |
| `/api/auth/login` | POST | Вход |
| `/api/queries` | POST | Создание запроса |
| `/api/queries` | GET | История запросов (пагинация) |
| `/api/queries/{id}` | GET | Получение запроса (+ polling) |
| `/api/queries/{id}/similar-tasks` | GET | Похожие задачи |

---

## Цветовая палитра

| Переменная | Цвет | Использование |
|---|---|---|
| `--dark` | `#213448` | Сайдбар, заголовки, основной текст |
| `--medium` | `#547792` | Кнопки, ссылки, акценты |
| `--light` | `#94B4C1` | Границы, вторичные элементы |
| `--cream` | `#EAE0CF` | Фон страницы, текст в сайдбаре |

---

## Аутентификация

JWT-токен хранится в `localStorage` (`rag_token`). Передаётся в заголовке `Authorization: Bearer <token>`. При получении 401 — автоматический logout и редирект на форму входа.
