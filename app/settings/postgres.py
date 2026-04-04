from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="postgres_")

    host: str = "localhost"
    port: int = 5432
    name: str = "rag_algo_solver"
    user: str = "postgres"
    password: str = "postgres"
