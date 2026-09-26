import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from .database.database import init_db
from .api import audit, recommendations, reports

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SEO Agent Database...")
    init_db()
    yield
    logger.info("Shutting down SEO Agent Service...")

app = FastAPI(
    title="AI-Powered Website SEO Analysis & Recommendation Agent",
    description="Automated SEO Audit, Technical Diagnostic, and AI Strategy Generator",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration to allow local Vite frontend and remote production environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audit.router)
app.include_router(recommendations.router)
app.include_router(reports.router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI SEO Analysis Agent API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
