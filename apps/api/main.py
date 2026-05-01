"""
Mourya Scholarium — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import settings
from database import init_db
from routers import auth, profile, projects, write, retrieve, cite, review, evidence

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Mourya Scholarium API starting...")
    await init_db()
    logging.info("Database initialized.")
    yield
    # Shutdown
    logging.info("Mourya Scholarium API shutting down.")


app = FastAPI(
    title="Mourya Scholarium API",
    description="Academic Intelligence & Writing Platform — Backend API",
    version="1.0.0-mvp",
    lifespan=lifespan,
)

# CORS — allow configured origins + common dev variants
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
# In development, also allow 127.0.0.1 variants
if settings.app_debug:
    dev_origins = {"http://localhost:3000", "http://127.0.0.1:3000"}
    origins = list(set(origins) | dev_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/v1/profile", tags=["Profile"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
app.include_router(write.router, prefix="/api/v1/write", tags=["Writing"])
app.include_router(retrieve.router, prefix="/api/v1/retrieve", tags=["Retrieval"])
app.include_router(cite.router, prefix="/api/v1/cite", tags=["Citations"])
app.include_router(review.router, prefix="/api/v1/review", tags=["Reviews"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["Evidence"])


@app.get("/", tags=["Health"])
async def health():
    return {"service": "Mourya Scholarium API", "version": "1.0.0-mvp", "status": "running"}
