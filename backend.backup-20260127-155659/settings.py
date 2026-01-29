from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    postgres_host: str = "pg-database"
    postgres_port: int = 5432
    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    
    # JWT - No default for secret in production
    jwt_secret: str
    jwt_alg: str = "HS256"
    jwt_access_ttl_min: int = 10080
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Log shipping
    os_ingest_url: str = "http://log-ingest:8080/ingest"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
