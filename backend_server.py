#!/usr/bin/env python3
"""
FastAPI backend server for the IAM Generator frontend.
This serves as a bridge between the React frontend and the CLI tool.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the CLI components directly
sys.path.append(str(Path(__file__).parent.parent / "src"))
from iam_generator.analyzer import IAMPermissionAnalyzer
from iam_generator.role_generator import IAMRoleGenerator
from iam_generator.parser import AWSCLIParser

app = FastAPI(title="AWS IAM Generator API", version="1.0.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000",
        "http://frontend:80",  # Docker container communication
        "http://localhost:80",  # Docker host access
        "http://127.0.0.1:80"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
analyzer = IAMPermissionAnalyzer()
role_generator = IAMRoleGenerator()
parser = AWSCLIParser()

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "AWS IAM Generator API",
        "version": "1.0.0",
        "timestamp": "2025-06-09T00:00:00Z"
    }

# Request/Response models
class AnalysisRequest(BaseModel):
    command: str
    debug: bool = False

class AnalysisResponse(BaseModel):
    service: str
    action: str
    original_command: str
    required_permissions: List[Dict[str, Any]]
    policy_document: Dict[str, Any]
    resource_arns: List[str]
    warnings: List[str]

class RoleGenerationRequest(BaseModel):
    command: str
    role_name: str
    trust_policy: Optional[str] = None
    output_format: str
    account_id: Optional[str] = None
    description: Optional[str] = None
    debug: bool = False

class RoleConfigResponse(BaseModel):
    role_name: str
    trust_policy: Dict[str, Any]
    permissions_policy: Dict[str, Any]
    terraform_config: Optional[str] = None
    cloudformation_config: Optional[str] = None
    aws_cli_commands: Optional[List[str]] = None

class BatchAnalysisRequest(BaseModel):
    commands: List[str]
    debug: bool = False

class BatchAnalysisResponse(BaseModel):
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]
    combined_policy: Dict[str, Any]

class ResourceSpecificRequest(BaseModel):
    commands: List[str]
    account_id: Optional[str] = None
    region: Optional[str] = None
    strict_mode: bool = True
    debug: bool = False

class ResourceSpecificResponse(BaseModel):
    policy_document: Dict[str, Any]
    metadata: Dict[str, Any]
    commands_analyzed: int
    specific_resources_found: int
    
class LeastPrivilegeRequest(BaseModel):
    commands: List[str]
    account_id: Optional[str] = None
    region: Optional[str] = None
    debug: bool = False

class ServiceSummaryRequest(BaseModel):
    commands: List[str]
    debug: bool = False

class ServiceSummaryResponse(BaseModel):
    summary: Dict[str, Dict[str, Any]]
    total_services: int
    total_actions: int

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/services")
async def get_supported_services():
    """Get list of supported AWS services."""
    # Get supported services from the permissions database
    supported_services = analyzer.permissions_db.get_supported_services()
    return {"services": list(supported_services)}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_command(request: AnalysisRequest):
    """Analyze a single AWS CLI command."""
    try:
        # Ensure command starts with 'aws'
        command = request.command.strip()
        if not command.startswith('aws '):
            command = f"aws {command}"
        
        # Create analyzer with debug mode
        print(f"DEBUG: Creating analyzer with debug_mode={request.debug}")
        analyzer_instance = IAMPermissionAnalyzer(debug_mode=request.debug)
        result = analyzer_instance.analyze_command(command)
        print(f"DEBUG: Result warnings: {result.get('warnings', [])}")
        
        return AnalysisResponse(
            service=result["service"],
            action=result["action"],
            original_command=result["original_command"],
            required_permissions=result["required_permissions"],
            policy_document=result["policy_document"],
            resource_arns=result["resource_arns"],
            warnings=result["warnings"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate-role", response_model=RoleConfigResponse)
async def generate_role(request: RoleGenerationRequest):
    """Generate an IAM role configuration."""
    try:
        # Ensure command starts with 'aws'
        command = request.command.strip()
        if not command.startswith('aws '):
            command = f"aws {command}"
        
        # Create analyzer with debug mode
        analyzer_instance = IAMPermissionAnalyzer(debug_mode=request.debug)
        analysis_result = analyzer_instance.analyze_command(command)
        
        # Generate the role
        trust_policy = request.trust_policy if request.trust_policy else "ec2"
        role_config = role_generator.generate_role(
            analysis_result=analysis_result,
            role_name=request.role_name,
            trust_policy_type=trust_policy,
            cross_account_id=request.account_id,
            output_format=request.output_format
        )
        
        # Extract the generated configurations and convert to proper formats
        terraform_config = role_config.get("terraform")  # Already a string
        cloudformation_config = role_config.get("cloudformation")
        if cloudformation_config and isinstance(cloudformation_config, dict):
            cloudformation_config = json.dumps(cloudformation_config, indent=2)
        aws_cli_commands = role_config.get("aws_cli")
        
        return RoleConfigResponse(
            role_name=role_config["role_name"],
            trust_policy=role_config["json"]["trust_policy"],
            permissions_policy=role_config["json"]["permissions_policy"],
            terraform_config=terraform_config,
            cloudformation_config=cloudformation_config,
            aws_cli_commands=aws_cli_commands
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze(request: BatchAnalysisRequest):
    """Analyze multiple AWS CLI commands."""
    try:
        # Filter out empty lines and comments
        commands = [
            cmd.strip() for cmd in request.commands 
            if cmd.strip() and not cmd.strip().startswith('#')
        ]
        
        if not commands:
            raise ValueError("No valid commands provided")
        
        # Ensure all commands start with 'aws'
        normalized_commands = []
        for cmd in commands:
            if not cmd.startswith('aws '):
                cmd = f"aws {cmd}"
            normalized_commands.append(cmd)
        
        # Create analyzer with debug mode
        analyzer_instance = IAMPermissionAnalyzer(debug_mode=request.debug)
        analysis_result = analyzer_instance.analyze_commands(normalized_commands)
        
        # Build individual results
        results = []
        for cmd in analysis_result.commands:
            cmd_permissions = [
                perm for perm in analysis_result.required_permissions
                # This is a simplified mapping - in practice you'd need better correlation
            ]
            
            results.append({
                "command": cmd.raw_command,
                "service": cmd.service,
                "action": cmd.action,
                "required_permissions": [
                    {
                        "action": perm.action,
                        "resource": perm.resource,
                        "condition": perm.condition
                    }
                    for perm in cmd_permissions[:5]  # Limit for demo
                ],
                "warnings": analysis_result.warnings
            })
        
        # Calculate summary
        summary = {
            "total_commands": len(results),
            "services_used": analysis_result.services_used,
            "total_permissions": len(analysis_result.required_permissions),
            "unique_permissions": [
                {
                    "action": perm.action,
                    "resource": perm.resource
                }
                for perm in analysis_result.required_permissions
            ]
        }
        
        return BatchAnalysisResponse(
            results=results,
            summary=summary,
            combined_policy=analysis_result.policy_document
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-resource-specific", response_model=ResourceSpecificResponse)
async def analyze_resource_specific(request: ResourceSpecificRequest):
    """Generate IAM policy with resource-specific ARNs instead of wildcards."""
    try:
        # Filter out empty lines and comments
        commands = [
            cmd.strip() for cmd in request.commands 
            if cmd.strip() and not cmd.strip().startswith('#')
        ]
        
        if not commands:
            raise ValueError("No valid commands provided")
        
        # Ensure all commands start with 'aws'
        normalized_commands = []
        for cmd in commands:
            if not cmd.startswith('aws '):
                cmd = f"aws {cmd}"
            normalized_commands.append(cmd)
        
        # Create analyzer with debug mode
        analyzer_instance = IAMPermissionAnalyzer(debug_mode=request.debug)
        
        # Generate resource-specific policy
        policy_doc = analyzer_instance.generate_resource_specific_policy(
            commands=normalized_commands,
            account_id=request.account_id,
            region=request.region,
            strict_mode=request.strict_mode
        )
        
        # Extract metadata
        metadata = policy_doc.pop("_metadata", {})
        
        return ResourceSpecificResponse(
            policy_document=policy_doc,
            metadata=metadata,
            commands_analyzed=metadata.get("commands_analyzed", len(commands)),
            specific_resources_found=metadata.get("specific_resources_found", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze-least-privilege")
async def analyze_least_privilege(request: LeastPrivilegeRequest):
    """Generate a least-privilege IAM policy for the given commands."""
    try:
        # Filter out empty lines and comments
        commands = [
            cmd.strip() for cmd in request.commands 
            if cmd.strip() and not cmd.strip().startswith('#')
        ]
        
        if not commands:
            raise ValueError("No valid commands provided")
        
        # Ensure all commands start with 'aws'
        normalized_commands = []
        for cmd in commands:
            if not cmd.startswith('aws '):
                cmd = f"aws {cmd}"
            normalized_commands.append(cmd)
        
        # Create analyzer with debug mode
        analyzer_instance = IAMPermissionAnalyzer(debug_mode=request.debug)
        
        # Generate least privilege policy
        policy_doc = analyzer_instance.generate_least_privilege_policy(
            commands=normalized_commands,
            account_id=request.account_id,
            region=request.region
        )
        
        return {"policy_document": policy_doc}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/service-summary", response_model=ServiceSummaryResponse)
async def get_service_summary(request: ServiceSummaryRequest):
    """Get a summary of services and actions used by commands."""
    try:
        # Filter out empty lines and comments
        commands = [
            cmd.strip() for cmd in request.commands 
            if cmd.strip() and not cmd.strip().startswith('#')
        ]
        
        if not commands:
            raise ValueError("No valid commands provided")
        
        # Ensure all commands start with 'aws'
        normalized_commands = []
        for cmd in commands:
            if not cmd.startswith('aws '):
                cmd = f"aws {cmd}"
            normalized_commands.append(cmd)
        
        # Create analyzer with debug mode
        analyzer_instance = IAMPermissionAnalyzer(debug_mode=request.debug)
        
        # Get service summary
        summary = analyzer_instance.get_service_summary(normalized_commands)
        
        total_services = len(summary)
        total_actions = sum(len(service_data.get("actions", [])) for service_data in summary.values())
        
        return ServiceSummaryResponse(
            summary=summary,
            total_services=total_services,
            total_actions=total_actions
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend_server:app", host="0.0.0.0", port=8000, reload=True)
