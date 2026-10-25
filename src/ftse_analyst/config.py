from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    eodhd_api_key: str = ""
    companies_house_api_key: str = ""


settings = Settings()