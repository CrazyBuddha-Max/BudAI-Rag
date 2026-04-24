from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # mysql
    db_host: str
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str
    # elasticsearch
    es_host: str = "http://localhost:9200"
    es_index: str = "budai_rag_chunks"
    # jwt
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    @property
    def database_url(self) -> str:
        return (
            f"mysql+aiomysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    class Config:
        env_file = ".env"


settings = Settings()
