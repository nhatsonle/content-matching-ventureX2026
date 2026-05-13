from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    chroma_persist_dir: str = "./chroma_db"
    data_path: str = "../data/directors_mockup.json"
    collection_name: str = "directors"

    class Config:
        env_file = ".env"


settings = Settings()
