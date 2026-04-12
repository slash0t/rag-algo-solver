import json
from typing import Any

from aiokafka import AIOKafkaProducer


class KafkaPublisher:
    def __init__(self, bootstrap_servers: str) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._producer: AIOKafkaProducer | None = None

    async def _ensure_connected(self) -> AIOKafkaProducer:
        if self._producer is None:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._producer.start()
        return self._producer

    async def publish(self, message: Any, topic: str) -> None:
        producer = await self._ensure_connected()
        await producer.send_and_wait(topic, value=message)

    async def close(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
