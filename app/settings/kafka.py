from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="kafka_")

    bootstrap_servers: str = "localhost:9092"

    topic_enrich: str = "query.enrich"
    topic_search: str = "query.search"
    topic_compose: str = "query.compose"
    topic_generate: str = "query.generate"
