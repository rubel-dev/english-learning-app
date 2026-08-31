from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name:str = 'English Learning App'
    app_version:str = '0.1.0'
    debug:bool = True
    database_url: str
    secret_key: str
    algorithm: str
    gemini_api_key: str
    model_config = SettingsConfigDict(
        env_file = '.env',
        env_file_encoding = 'utf-8',
        case_sensitive=False
    )
settings = Settings()