from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.connection import engine, Base
from app.api.auth import router as auth_router
from app.api.processing import router as processing_router
from app.api.upload import router as upload_router
from app.models.processing_log import ProcessingLog
from app.models.report import Report
from app.models.validation_report import ValidationReport

# Create database tables at application initialization
# (Ensures registered models are auto-created when the backend boots)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Business Intelligence Assistant Backend",
    description="Production-ready FastAPI foundation with JWT authentication and database connections",
    version="1.0.0"
)

# Enable CORS for local testing (allows frontend to call API endpoints from other origins/ports)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin for simple local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include modular routers
app.include_router(auth_router)
app.include_router(processing_router)
app.include_router(upload_router)

@app.get("/")
def get_root() -> dict:
    """
    Root endpoint validating that the API service is up and running.
    """
    return {"message": "AI Business Intelligence Assistant Backend Running"}
