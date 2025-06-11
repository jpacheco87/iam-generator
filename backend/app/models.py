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


class PolicyValidationRequest(BaseModel):
    """Request model for policy validation."""
    policy: Dict[str, Any]
    policy_type: str = "managed"  # managed, inline_user, inline_role, inline_group
    account_id: Optional[str] = None
    debug: bool = False


class ValidationIssueModel(BaseModel):
    """Model for validation issues."""
    severity: str
    category: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    code: Optional[str] = None


class PolicyValidationResponse(BaseModel):
    """Response model for policy validation."""
    is_valid: bool
    policy_size: int
    policy_type: str
    issues: List[ValidationIssueModel]
    score: int
    recommendations: List[str]


class PolicyOptimizationRequest(BaseModel):
    """Request model for policy optimization."""
    policy: Dict[str, Any]
    optimization_level: str = "standard"  # basic, standard, aggressive
    account_id: Optional[str] = None


class PolicyOptimizationResponse(BaseModel):
    """Response model for policy optimization."""
    original_policy: Dict[str, Any]
    optimized_policy: Dict[str, Any]
    size_reduction: int
    optimizations_applied: List[str]
    validation_result: PolicyValidationResponse


class CrossServiceDependencyRequest(BaseModel):
    """Request model for cross-service dependency analysis."""
    commands: List[str]
    include_implicit: bool = True
    debug: bool = False


class CrossServiceDependencyResponse(BaseModel):
    """Response model for cross-service dependency analysis."""
    dependencies: Dict[str, List[str]]
    additional_permissions: List[Dict[str, Any]]
    enhanced_policy: Dict[str, Any]
    dependency_graph: Dict[str, Any]


class ConditionalPolicyRequest(BaseModel):
    """Request model for conditional policy generation."""
    commands: List[str]
    conditions: Dict[str, Any]  # IP restrictions, MFA requirements, etc.
    account_id: Optional[str] = None
    region: Optional[str] = None


class ConditionalPolicyResponse(BaseModel):
    """Response model for conditional policy generation."""
    policy_document: Dict[str, Any]
    conditions_applied: List[str]
    security_enhancements: List[str]
    metadata: Dict[str, Any]
