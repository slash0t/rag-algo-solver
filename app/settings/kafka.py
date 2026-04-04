from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="kafka_")

    bootstrap_servers: str = "localhost:9092"
