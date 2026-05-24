from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    database_url: str = "sqlite:///./app.db"
    ai_model: str = "deepseek-chat"
    secret_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
