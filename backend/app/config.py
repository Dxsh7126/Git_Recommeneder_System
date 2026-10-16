import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    PROJECT_NAME: str = "Open-Source Issue Recommender"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Try PostgreSQL first (e.g. docker container on 5433 or 5432), fallback to sqlite
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:postgres@localhost:5433/issue_recommender"
    )
    SQLITE_FALLBACK_URL: str = "sqlite:///./issue_recommender.db"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # Model parameters
    ALS_FACTORS: int = 20
    ALS_REGULARIZATION: float = 0.1
    ALS_ITERATIONS: int = 15
    ALS_ALPHA: float = 40.0
    
    CACHE_EXPIRATION_SECONDS: int = 300  # 5 minutes

settings = Settings()
