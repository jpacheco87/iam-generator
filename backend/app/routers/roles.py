"""
IAM role generation endpoints.
"""

from fastapi import APIRouter, HTTPException

from ..models import (
    RoleGenerationRequest,
    RoleGenerationAllFormatsRequest,
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


@router.post("/generate-role-all-formats", response_model=RoleConfigResponse)
async def generate_iam_role_all_formats(request: RoleGenerationAllFormatsRequest):
    """Generate an IAM role configuration with all output formats."""
    try:
        # Generate all formats by calling the service multiple times
        formats = ["json", "terraform", "cloudformation", "aws_cli"]
        results = {}
        
        for format_type in formats:
            result = service.generate_role(
                command=request.command,
                role_name=request.role_name,
                trust_policy=request.trust_policy,
                output_format=format_type,
                account_id=request.account_id,
                description=request.description,
                debug=request.debug
            )
            
            if 'error' in result:
                raise HTTPException(status_code=400, detail=result['error'])
                
            results[format_type] = result
        
        # Combine all results into a single response
        combined_result = {
            'role_name': results['json']['role_name'],
            'trust_policy': results['json']['trust_policy'],
            'permissions_policy': results['json']['permissions_policy'],
            'terraform_config': results['terraform'].get('terraform_config'),
            'cloudformation_config': results['cloudformation'].get('cloudformation_config'),
            'aws_cli_commands': results['aws_cli'].get('aws_cli_commands')
        }
        
        return RoleConfigResponse(**combined_result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
