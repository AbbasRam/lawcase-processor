from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_SERVER: str = "database-1.c98m2g6e2a89.eu-central-1.rds.amazonaws.com"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "g263nNpRQE"
    POSTGRES_DB: str = "lawcase_search"
    POSTGRES_PORT: int = 5432
    REDIS_BROKER_URL: str = "redis://redis:6379/0"
    REDIS_BACKEND_URL: str = "redis://redis:6379/1"
    CELERY_WORKER_CONCURRENCY: int = 4  # Default number of cores

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
