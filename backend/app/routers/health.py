"""
Health check and system status endpoints.
"""

from fastapi import APIRouter
from ..models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for container orchestration."""
    return HealthResponse(
        status="healthy",
        service="AWS IAM Generator API [RELOAD CONFIRMED]",
        version="1.0.0",
        timestamp="2025-06-10T00:00:00Z"
    )
