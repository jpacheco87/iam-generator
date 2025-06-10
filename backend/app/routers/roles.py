"""
IAM role generation endpoints.
"""

from fastapi import APIRouter, HTTPException

from ..models import (
    RoleGenerationRequest,
    RoleConfigResponse
)
from ..services import IAMGeneratorService

router = APIRouter()
service = IAMGeneratorService()


@router.post("/generate-role", response_model=RoleConfigResponse)
async def generate_iam_role(request: RoleGenerationRequest):
    """Generate an IAM role configuration for the given command."""
    try:
        result = service.generate_role(
            command=request.command,
            role_name=request.role_name,
            trust_policy=request.trust_policy,
            output_format=request.output_format,
            account_id=request.account_id,
            description=request.description,
            debug=request.debug
        )
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
            
        return RoleConfigResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
