"""
Command analysis endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from ..models import (
    AnalysisRequest, 
    AnalysisResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    ServicesResponse
)
from ..services import IAMGeneratorService

router = APIRouter()
service = IAMGeneratorService()


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_command(request: AnalysisRequest):
    """Analyze a single AWS CLI command and return required permissions."""
    try:
        result = service.analyze_command(request.command, request.debug)
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_commands(request: BatchAnalysisRequest):
    """Analyze multiple AWS CLI commands and return combined results."""
    try:
        result = service.batch_analyze(request.commands, request.debug)
        return BatchAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/services", response_model=ServicesResponse)
async def get_supported_services():
    """Get list of supported AWS services."""
    try:
        services = service.get_supported_services()
        return ServicesResponse(
            services=services,
            total_count=len(services)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
