"""
Advanced analysis endpoints for resource-specific and least privilege policies.
"""

from fastapi import APIRouter, HTTPException

from ..models import (
    ResourceSpecificRequest,
    ResourceSpecificResponse,
    LeastPrivilegeRequest,
    ServiceSummaryRequest,
    ServiceSummaryResponse
)
from ..services import IAMGeneratorService

router = APIRouter()
service = IAMGeneratorService()


@router.post("/analyze-resource-specific", response_model=ResourceSpecificResponse)
async def analyze_resource_specific(request: ResourceSpecificRequest):
    """Generate IAM policy with resource-specific ARNs instead of wildcards."""
    try:
        # Use the analyzer's resource-specific policy generation
        result = service.analyzer.generate_resource_specific_policy(
            commands=request.commands,
            account_id=request.account_id,
            region=request.region,
            strict_mode=request.strict_mode if request.strict_mode is not None else True
        )
        
        # Extract metadata from the policy document
        metadata = result.get("_metadata", {})
        
        # Return the response with the expected structure
        return ResourceSpecificResponse(
            policy_document=result,
            metadata=metadata,
            commands_analyzed=metadata.get("commands_analyzed", len(request.commands)),
            specific_resources_found=metadata.get("specific_resources_found", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/analyze-least-privilege")
async def analyze_least_privilege(request: LeastPrivilegeRequest):
    """Generate a least-privilege IAM policy for the given commands."""
    try:
        # Use the analyzer's least privilege policy generation
        policy_document = service.analyzer.generate_least_privilege_policy(
            commands=request.commands,
            account_id=request.account_id,
            region=request.region
        )
        
        result = {"policy_document": policy_document}
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/service-summary", response_model=ServiceSummaryResponse)
async def get_service_summary(request: ServiceSummaryRequest):
    """Generate a summary of service usage and permissions."""
    try:
        # Use the analyzer's service summary generation
        summary = service.analyzer.get_service_summary(request.commands)
        
        # Calculate totals
        total_services = len(summary)
        total_actions = sum(len(service_data.get("actions", [])) for service_data in summary.values())
        total_permissions = sum(len(service_data.get("permissions", [])) for service_data in summary.values())
        
        # Generate a basic policy document for the summary
        policy_document = {"Version": "2012-10-17", "Statement": []}
        
        result = {
            "summary": summary,
            "total_services": total_services,
            "total_commands": len(request.commands),
            "total_actions": total_actions,
            "unique_permissions": total_permissions,
            "policy_document": policy_document
        }
        return ServiceSummaryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
