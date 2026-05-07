from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str

    PROJECT_NAME: str = "StoxCircle API"
    VERSION     : str = "0.0.1"
    API_V1_STR  : str = "/api/v1"

    class Config:
        env_file = ".env"

settings = Settings()