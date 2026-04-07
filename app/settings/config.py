from app.settings.kafka import KafkaConfig
from app.settings.postgres import PostgresConfig
from app.settings.qdrant import QdrantConfig
from app.settings.yandex_cloud import YandexCloudConfig


class AppConfig:
    def __init__(self) -> None:
        self.postgres = PostgresConfig()
        self.kafka = KafkaConfig()
        self.qdrant = QdrantConfig()
        self.yandex_cloud = YandexCloudConfig()
