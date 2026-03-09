from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "JARVIS"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
