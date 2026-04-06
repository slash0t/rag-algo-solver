from app.domain.services.llm_client import LLMClient


class EchoLLMClient(LLMClient):
    async def generate(self, prompt: str) -> str:
        return prompt
