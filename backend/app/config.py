from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    nebius_api_key: str = ""
    nebius_base_url: str = "https://api.tokenfactory.nebius.com/v1/"

    model_nano: str = "nvidia/nemotron-3-nano-30b-a3b"
    model_super: str = "nvidia/nemotron-3-super-120b-a12b"
    model_ultra: str = "nvidia/nemotron-3-ultra-550b-a55b"
    model_embedding: str = "BAAI/bge-en-icl"

    mock_mode: bool = False
    database_url: str = "sqlite:///./triage.db"

    @property
    def effective_mock_mode(self) -> bool:
        return self.mock_mode or not self.nebius_api_key


settings = Settings()
