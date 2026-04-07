from openai import AsyncOpenAI

from app.domain.services.llm_client import LLMClient
from app.settings.yandex_cloud import YandexCloudConfig


class YandexCloudLLMClient(LLMClient):
    def __init__(self, config: YandexCloudConfig) -> None:
        self._config = config
        self._client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            project=config.folder,
        )
        self._model = f"gpt://{config.folder}/{config.model}"

    async def generate(self, prompt: str) -> str:
        response = await self._client.responses.create(
            model=self._model,
            temperature=self._config.temperature,
            instructions="",
            input=prompt,
            max_output_tokens=self._config.max_output_tokens,
        )
        return response.output_text
