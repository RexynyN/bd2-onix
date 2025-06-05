"""
Application configuration settings
"""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://super_user:carimboatrasado@localhost:5432/onixlibrary"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "super_user"
    DATABASE_PASSWORD: str = "carimboatrasado"
    DATABASE_NAME: str = "onixlibrary"
    
    # Connection Pool Settings
    MIN_CONNECTIONS: int = 5
    MAX_CONNECTIONS: int = 20
    
    # Application
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Gerenciamento de Biblioteca"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API para gerenciamento de biblioteca e empréstimos de livros"
    
    class Config:
        env_file = ".env"

settings = Settings()
