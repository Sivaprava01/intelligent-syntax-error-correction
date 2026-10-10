"""FastAPI application entrypoint for C Syntax Error Detection Engine."""

import sys
from pathlib import Path

# Ensure project root is in sys.path regardless of where uvicorn is launched
_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.routes import router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Deterministic C Compiler Syntax Analysis and Error Detection Service",
)

# Allow CORS for future frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs",
        "analysis_endpoint": f"{settings.API_PREFIX}/analyze",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
