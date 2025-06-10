"""
Pydantic models for API request/response schemas.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class AnalysisRequest(BaseModel):
    """Request model for command analysis."""
    command: str
    debug: bool = False


class AnalysisResponse(BaseModel):
    """Response model for command analysis."""
    service: str
    action: str
    original_command: str
    required_permissions: List[Dict[str, Any]]
    policy_document: Dict[str, Any]
    resource_arns: List[str]
    warnings: List[str]


class RoleGenerationRequest(BaseModel):
    """Request model for IAM role generation."""
    command: str
    role_name: str
    trust_policy: Optional[str] = None
    output_format: str
    account_id: Optional[str] = None
    description: Optional[str] = None
    debug: bool = False


class RoleConfigResponse(BaseModel):
    """Response model for IAM role configuration."""
    role_name: str
    trust_policy: Dict[str, Any]
    permissions_policy: Dict[str, Any]
    terraform_config: Optional[str] = None
    cloudformation_config: Optional[str] = None
    aws_cli_commands: Optional[List[str]] = None


class BatchAnalysisRequest(BaseModel):
    """Request model for batch command analysis."""
    commands: List[str]
    debug: bool = False


class BatchAnalysisResponse(BaseModel):
    """Response model for batch command analysis."""
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    combined_policy: Dict[str, Any]


class ResourceSpecificRequest(BaseModel):
    """Request model for resource-specific analysis."""
    commands: List[str]
    account_id: Optional[str] = None
    region: Optional[str] = None
    strict_mode: bool = True
    debug: bool = False


class ResourceSpecificResponse(BaseModel):
    """Response model for resource-specific analysis."""
    policy_document: Dict[str, Any]
    metadata: Dict[str, Any]
    commands_analyzed: int
    specific_resources_found: int


class LeastPrivilegeRequest(BaseModel):
    """Request model for least privilege analysis."""
    commands: List[str]
    account_id: Optional[str] = None
    region: Optional[str] = None
    debug: bool = False


class ServiceSummaryRequest(BaseModel):
    """Request model for service usage summary."""
    commands: List[str]
    debug: bool = False


class ServiceSummaryResponse(BaseModel):
    """Response model for service usage summary."""
    summary: Dict[str, Dict[str, Any]]
    total_services: int
    total_commands: int
    unique_permissions: int
    policy_document: Dict[str, Any]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    service: str
    version: str
    timestamp: str


class ServicesResponse(BaseModel):
    """Response model for supported services."""
    services: List[str]
    total_count: int
