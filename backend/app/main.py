#!/usr/bin/env python3
"""
FastAPI backend server for the IAM Generator frontend.
This serves as a bridge between the React frontend and the CLI tool.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import API_TITLE, API_VERSION, API_DESCRIPTION, CORS_ORIGINS
from .routers import health, analysis, roles, advanced

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(analysis.router, tags=["Analysis"])
app.include_router(roles.router, tags=["Roles"])
app.include_router(advanced.router, tags=["Advanced"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
