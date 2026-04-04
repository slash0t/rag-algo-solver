.PHONY: run migrate migration infra-up infra-down install lint format

run:
	poetry run uvicorn app.presentation.api.app:app --reload --host 0.0.0.0 --port 8000

migrate:
	poetry run alembic upgrade head

migration:
	poetry run alembic revision --autogenerate -m "$(name)"

infra-up:
	docker compose up -d

infra-down:
	docker compose down

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .
