from app.settings.kafka import KafkaConfig
from app.settings.llm import LLMConfig
from app.settings.postgres import PostgresConfig
from app.settings.qdrant import QdrantConfig


class AppConfig:
    def __init__(self) -> None:
        self.postgres = PostgresConfig()
        self.kafka = KafkaConfig()
        self.qdrant = QdrantConfig()
        self.llm = LLMConfig()
