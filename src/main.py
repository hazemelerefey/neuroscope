"""
NeuroScope Backend — FastAPI Application
Visual Deep Learning Builder
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.api.routes import models, export, educational

# Rate limiting
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="NeuroScope API",
    description="Visual Deep Learning Builder — visually construct ML/DL models and generate production-ready code",
    version="0.2.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — restrict in production, allow localhost in development
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
if ENVIRONMENT == "production":
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
else:
    ALLOWED_ORIGINS = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(export.router, prefix="/api", tags=["export"])
app.include_router(educational.router, prefix="/api", tags=["educational"])


@app.get("/")
async def root():
    return {
        "name": "NeuroScope API",
        "version": "0.2.0",
        "description": "Visual Deep Learning Builder",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
