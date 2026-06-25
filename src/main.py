"""
NeuroScope Backend — FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import upload, analyze, export, compare

app = FastAPI(
    title="NeuroScope API",
    description="AI-Powered 3D Neural Network Architecture Visualizer & Analyzer",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(export.router, prefix="/api", tags=["export"])
app.include_router(compare.router, prefix="/api", tags=["compare"])


@app.get("/")
async def root():
    return {
        "name": "NeuroScope API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
