from pydantic_core import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str

    SQLALCHEMY_DATABASE_URI: str

    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()