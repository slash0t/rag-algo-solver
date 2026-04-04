from faststream import FastStream
from faststream.kafka import KafkaBroker

broker = KafkaBroker()
stream_app = FastStream(broker)
