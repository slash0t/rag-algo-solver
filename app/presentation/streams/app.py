from faststream import FastStream
from faststream.kafka import KafkaBroker

from app.settings.kafka import KafkaConfig

kafka_config = KafkaConfig()
broker = KafkaBroker(kafka_config.bootstrap_servers)

stream_app = FastStream(broker)
