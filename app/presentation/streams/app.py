from faststream import FastStream

from app.container import APP_CONTAINER
from utils.env import load_env

load_env()

kafka_config = APP_CONTAINER.kafka_config()
broker = APP_CONTAINER.broker()

stream_app = FastStream(broker)
