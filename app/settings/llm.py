from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="llm_")

    provider: str = "openai"
    api_key: str = ""
    api_type: str = "azure"
    api_version: str = "2023-03-15-preview"
    base_url: str | None = None
