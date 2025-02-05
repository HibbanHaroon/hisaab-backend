from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    PROJECT_NAME: str
    VERSION: str
    SQLALCHEMY_DATABASE_URI: str

    class Config:
        env_file = ".env"
        case_sensitive = True

    @classmethod
    def get_settings(cls):
        return cls()

settings = Settings.get_settings()