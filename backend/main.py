import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.models import Developer, Repository, Issue, Interaction, Feedback
from backend.app.api.router import api_router
from backend.app.services.data_collector import seed_database
from backend.app.services.hybrid_ranker import hybrid_ranker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Create database tables
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    # 2. Automatically seed initial sample repos and issues if empty
    db = SessionLocal()
    try:
        logger.info("Checking seed data status...")
        seed_database(db, force=False)
        # 3. Train models on seeded data
        logger.info("Fitting recommender models (TF-IDF, ALS, LightGBM)...")
        hybrid_ranker.train(db)
    except Exception as e:
        logger.error("Error during startup seed/training: %s", e)
    finally:
        db.close()

    yield
    logger.info("Shutting down Open-source Issue Recommender API.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent open-source issue recommendation engine combining Content-based, Collaborative Filtering, and LightGBM ranking.",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
