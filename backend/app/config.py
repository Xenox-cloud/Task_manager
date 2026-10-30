from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App settings read from environment variables or a .env file."""

    database_url: str = "sqlite:///./tasks.db"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def sqlalchemy_url(self) -> str:
        # Neon and most hosted Postgres give "postgres://" URLs; SQLAlchemy needs the driver name.
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url


settings = Settings()
