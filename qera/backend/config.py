import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = Field("changeme", env="SECRET_KEY")
    DB_PATH: str = Field("../database/qera.db", env="DB_PATH")
    ALLOWED_ORIGIN: str = Field("http://localhost:5173", env="ALLOWED_ORIGIN")
    DEBUG: bool = Field(True, env="DEBUG")


settings = Settings()
