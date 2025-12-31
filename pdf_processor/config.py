from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    REDIS_BROKER_URL: str
    REDIS_BACKEND_URL: str
    CELERY_WORKER_CONCURRENCY: int

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = "pdf_processor/.env"
        env_file_encoding = "utf-8"

settings = Settings()
