"""
Role Generator

This module provides functionality to generate IAM roles and policies
based on the analyzed permissions from AWS CLI commands.
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

from .analyzer import AnalysisResult, IAMPermissionAnalyzer


class RoleConfiguration(BaseModel):
    """Configuration for IAM role generation."""
    
    role_name: str = Field(description="Name of the IAM role")
    description: str = Field(default="", description="Role description")
    assume_role_policy: Dict = Field(description="Trust policy for the role")
    max_session_duration: int = Field(default=3600, description="Maximum session duration in seconds")
    path: str = Field(default="/", description="IAM path for the role")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for the role")


class PolicyConfiguration(BaseModel):
    """Configuration for IAM policy generation."""
    
    policy_name: str = Field(description="Name of the IAM policy")
    description: str = Field(default="", description="Policy description")
    path: str = Field(default="/", description="IAM path for the policy")
    tags: Dict[str, str] = Field(default_factory=dict, description="Tags for the policy")


class GeneratedRole(BaseModel):
    """Generated IAM role with policies."""
    
    role_config: RoleConfiguration
    policy_config: PolicyConfiguration
    policy_document: Dict
    terraform_config: Optional[str] = None
    cloudformation_template: Optional[Dict] = None
    aws_cli_commands: List[str] = Field(default_factory=list)


class IAMRoleGenerator:
    """Generator for IAM roles and policies based on analyzed permissions."""
    
    def __init__(self):
        """Initialize the role generator."""
        self.analyzer = IAMPermissionAnalyzer()
    
    def generate_role(self, analysis_result: Dict = None,
                     commands: List[str] = None,
                     role_name: str = None,
                     trust_policy: Optional[Dict] = None,
                     trust_policy_type: str = "default",
                     cross_account_id: Optional[str] = None,
                     output_format: str = "json",
                     description: Optional[str] = None,
                     **kwargs) -> Dict:
        """
        Generate a complete IAM role configuration.
        
        Args:
            analysis_result: Analysis result dictionary (for test compatibility)
            commands: List of AWS CLI commands (alternative to analysis_result)
            role_name: Name for the IAM role
            trust_policy: Custom trust policy (overrides trust_policy_type)
            trust_policy_type: Type of trust policy (default, ec2, lambda, ecs, cross-account)
            cross_account_id: Account ID for cross-account trust policy
            output_format: Output format (json, terraform, cloudformation, aws-cli)
            description: Role description
            **kwargs: Additional configuration options
            
        Returns:
            Role configuration dictionary
        """
        # Handle different calling patterns
        if analysis_result is not None:
            # Called with analysis_result (test compatibility)
            return self.generate_role_from_analysis(
                analysis_result, role_name, trust_policy_type, 
                cross_account_id, output_format, description, **kwargs
            )
        elif commands is not None:
            # Called with commands (analyze first)
            analysis = self.analyze_commands_for_role(commands)
            return self.generate_role_from_analysis(
                {
                    "policy_document": analysis.policy_document,
                    "services_used": analysis.services_used,
                    "required_permissions": [
                        {"action": p.action, "resource": p.resource, "condition": p.condition}
                        for p in analysis.required_permissions
                    ]
                },
                role_name, trust_policy_type, cross_account_id, output_format, description, **kwargs
            )
        else:
            raise ValueError("Either analysis_result or commands must be provided")
    
    def generate_role_from_analysis(self, analysis_result: Dict,
                                  role_name: str,
                                  trust_policy_type: str = "default",
                                  cross_account_id: Optional[str] = None,
                                  output_format: str = "json",
                                  description: Optional[str] = None,
                                  **kwargs) -> Dict:
        """
        Generate IAM role from analysis result (test compatibility method).
        
        Args:
            analysis_result: Analysis result dictionary
            role_name: Name for the IAM role
            trust_policy_type: Type of trust policy (default, ec2, lambda, ecs, cross-account)
            cross_account_id: Account ID for cross-account trust policy
            output_format: Output format (json, terraform, cloudformation, aws-cli)
            description: Role description
            **kwargs: Additional options
            
        Returns:
            Role configuration dictionary with all output formats
        """
        # Validate cross-account requirements
        if trust_policy_type == "cross-account" and not cross_account_id:
            raise ValueError("Cross-account ID is required for cross-account trust policy")
            
        # Validate trust policy type
        valid_types = ["default", "ec2", "lambda", "ecs", "cross-account"]
        if trust_policy_type not in valid_types:
            raise ValueError(f"Unsupported trust policy type: {trust_policy_type}")
        
        # Generate trust policy
        trust_policy = self._generate_trust_policy(trust_policy_type, cross_account_id)
        
        # Sanitize role name
        sanitized_name = self._sanitize_role_name(role_name)
        
        # Generate description
        if not description:
            # Check if original command is available in analysis result
            original_command = analysis_result.get("original_command")
            if original_command:
                description = f"IAM role for AWS CLI command: {original_command}"
            else:
                services = analysis_result.get("services_used", [])
                if isinstance(services, list) and services:
                    description = f"IAM role for {', '.join(services)} operations"
                else:
                    description = f"IAM role for AWS CLI operations"
        
        # Create base role structure
        role_data = {
            "role_name": sanitized_name,
            "description": description,
            "assume_role_policy": trust_policy,
            "policy_document": analysis_result.get("policy_document", {}),
            "trust_policy_type": trust_policy_type
        }
        
        # Generate comprehensive result with all formats
        result = {
            # Base data
            "role_name": sanitized_name,
            "description": description,
            "assume_role_policy": trust_policy,
            "policy_document": analysis_result.get("policy_document", {}),
            "trust_policy_type": trust_policy_type,
            
            # JSON format (for compatibility)
            "json": {
                "role_name": sanitized_name,
                "description": description,
                "trust_policy": trust_policy,
                "permissions_policy": analysis_result.get("policy_document", {}),
                "policy_document": analysis_result.get("policy_document", {}),
                "assume_role_policy": trust_policy
            },
            
            # Generate all output formats
            "terraform": self._generate_terraform_config(role_data),
            "cloudformation": self._generate_cloudformation_config(role_data),
            "aws_cli": self._generate_aws_cli_commands(role_data)
        }
        
        return result
    
    def analyze_commands_for_role(self, commands: List[str]) -> AnalysisResult:
        """
        Analyze commands specifically for role generation.
        
        Args:
            commands: List of AWS CLI commands
            
        Returns:
            AnalysisResult optimized for role generation
        """
        return self.analyzer.analyze_commands(
            commands, 
            strict_resources=False,  # Use broader permissions for roles
            include_read_only=True
        )
    
    def _create_role_config(self, role_name: str, trust_policy: Dict, **kwargs) -> RoleConfiguration:
        """Create role configuration."""
        return RoleConfiguration(
            role_name=role_name,
            description=kwargs.get('description', f"IAM role for {role_name}"),
            assume_role_policy=trust_policy,
            max_session_duration=kwargs.get('max_session_duration', 3600),
            path=kwargs.get('path', '/'),
            tags=kwargs.get('tags', {
                'CreatedBy': 'IAMGenerator',
                'CreatedAt': datetime.now().isoformat()
            })
        )
    
    def _create_policy_config(self, policy_name: str, **kwargs) -> PolicyConfiguration:
        """Create policy configuration."""
        return PolicyConfiguration(
            policy_name=policy_name,
            description=kwargs.get('policy_description', f"Policy for {policy_name}"),
            path=kwargs.get('policy_path', '/'),
            tags=kwargs.get('policy_tags', {
                'CreatedBy': 'IAMGenerator',
                'CreatedAt': datetime.now().isoformat()
            })
        )
    
    def _default_trust_policy(self) -> Dict:
        """Get default trust policy for EC2 instances."""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ec2.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    
    def lambda_trust_policy(self) -> Dict:
        """Get trust policy for Lambda functions."""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    
    def ecs_trust_policy(self) -> Dict:
        """Get trust policy for ECS tasks."""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "ecs-tasks.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
    
    def cross_account_trust_policy(self, account_ids: List[str], 
                                  external_id: Optional[str] = None,
                                  require_mfa: bool = False) -> Dict:
        """
        Get trust policy for cross-account access.
        
        Args:
            account_ids: List of trusted AWS account IDs
            external_id: External ID for additional security
            require_mfa: Whether to require MFA
            
        Returns:
            Cross-account trust policy
        """
        principals = [f"arn:aws:iam::{account_id}:root" for account_id in account_ids]
        
        statement = {
            "Effect": "Allow",
            "Principal": {
                "AWS": principals
            },
            "Action": "sts:AssumeRole"
        }
        
        conditions = {}
        if external_id:
            conditions["StringEquals"] = {"sts:ExternalId": external_id}
        
        if require_mfa:
            conditions["Bool"] = {"aws:MultiFactorAuthPresent": "true"}
        
        if conditions:
            statement["Condition"] = conditions
        
        return {
            "Version": "2012-10-17",
            "Statement": [statement]
        }
    
    def _generate_terraform(self, role_config: RoleConfiguration, 
                          policy_config: PolicyConfiguration,
                          policy_document: Dict) -> str:
        """Generate Terraform configuration."""
        terraform_config = f'''# IAM Role and Policy Configuration
# Generated by IAM Generator

resource "aws_iam_role" "{role_config.role_name}" {{
  name               = "{role_config.role_name}"
  description        = "{role_config.description}"
  path               = "{role_config.path}"
  max_session_duration = {role_config.max_session_duration}
  
  assume_role_policy = jsonencode({json.dumps(role_config.assume_role_policy, indent=2)})
  
  tags = {{
{self._format_terraform_tags(role_config.tags)}
  }}
}}

resource "aws_iam_policy" "{policy_config.policy_name}" {{
  name        = "{policy_config.policy_name}"
  description = "{policy_config.description}"
  path        = "{policy_config.path}"
  
  policy = jsonencode({json.dumps(policy_document, indent=2)})
  
  tags = {{
{self._format_terraform_tags(policy_config.tags)}
  }}
}}

resource "aws_iam_role_policy_attachment" "{role_config.role_name}_policy_attachment" {{
  role       = aws_iam_role.{role_config.role_name}.name
  policy_arn = aws_iam_policy.{policy_config.policy_name}.arn
}}

# Instance Profile (if needed for EC2)
resource "aws_iam_instance_profile" "{role_config.role_name}_profile" {{
  name = "{role_config.role_name}-profile"
  role = aws_iam_role.{role_config.role_name}.name
}}

# Outputs
output "{role_config.role_name}_arn" {{
  description = "ARN of the IAM role"
  value       = aws_iam_role.{role_config.role_name}.arn
}}

output "{policy_config.policy_name}_arn" {{
  description = "ARN of the IAM policy"
  value       = aws_iam_policy.{policy_config.policy_name}.arn
}}
'''
        return terraform_config
    
    def _format_terraform_tags(self, tags: Dict[str, str]) -> str:
        """Format tags for Terraform configuration."""
        if not tags:
            return ""
        
        tag_lines = []
        for key, value in tags.items():
            tag_lines.append(f'    {key} = "{value}"')
        
        return '\n'.join(tag_lines)
    
    def _generate_cloudformation(self, role_config: RoleConfiguration,
                               policy_config: PolicyConfiguration,
                               policy_document: Dict) -> Dict:
        """Generate CloudFormation template."""
        return {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"IAM Role and Policy for {role_config.role_name}",
            "Resources": {
                f"{role_config.role_name}Role": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "RoleName": role_config.role_name,
                        "Description": role_config.description,
                        "Path": role_config.path,
                        "MaxSessionDuration": role_config.max_session_duration,
                        "AssumeRolePolicyDocument": role_config.assume_role_policy,
                        "Tags": [
                            {"Key": k, "Value": v} for k, v in role_config.tags.items()
                        ]
                    }
                },
                f"{policy_config.policy_name}Policy": {
                    "Type": "AWS::IAM::Policy",
                    "Properties": {
                        "PolicyName": policy_config.policy_name,
                        "PolicyDocument": policy_document,
                        "Roles": [{"Ref": f"{role_config.role_name}Role"}]
                    }
                },
                f"{role_config.role_name}InstanceProfile": {
                    "Type": "AWS::IAM::InstanceProfile",
                    "Properties": {
                        "InstanceProfileName": f"{role_config.role_name}-profile",
                        "Roles": [{"Ref": f"{role_config.role_name}Role"}]
                    }
                }
            },
            "Outputs": {
                f"{role_config.role_name}Arn": {
                    "Description": "ARN of the IAM role",
                    "Value": {"Fn::GetAtt": [f"{role_config.role_name}Role", "Arn"]},
                    "Export": {"Name": {"Fn::Sub": f"${{AWS::StackName}}-{role_config.role_name}-Arn"}}
                },
                f"{policy_config.policy_name}Arn": {
                    "Description": "ARN of the IAM policy",
                    "Value": {"Ref": f"{policy_config.policy_name}Policy"},
                    "Export": {"Name": {"Fn::Sub": f"${{AWS::StackName}}-{policy_config.policy_name}-Arn"}}
                }
            }
        }
    
    def _generate_cli_commands(self, role_config: RoleConfiguration,
                             policy_config: PolicyConfiguration,
                             policy_document: Dict) -> List[str]:
        """Generate AWS CLI commands to create the role and policy."""
        commands = []
        
        # Create trust policy file
        commands.append("# Save trust policy to file")
        commands.append(f"cat > trust-policy.json << 'EOF'")
        commands.append(json.dumps(role_config.assume_role_policy, indent=2))
        commands.append("EOF")
        commands.append("")
        
        # Create permissions policy file
        commands.append("# Save permissions policy to file")
        commands.append(f"cat > {policy_config.policy_name.lower()}-policy.json << 'EOF'")
        commands.append(json.dumps(policy_document, indent=2))
        commands.append("EOF")
        commands.append("")
        
        # Create IAM role
        create_role_cmd = f"aws iam create-role --role-name {role_config.role_name}"
        create_role_cmd += f" --assume-role-policy-document file://trust-policy.json"
        create_role_cmd += f" --description '{role_config.description}'"
        create_role_cmd += f" --path {role_config.path}"
        create_role_cmd += f" --max-session-duration {role_config.max_session_duration}"
        commands.append(create_role_cmd)
        
        # Create IAM policy
        create_policy_cmd = f"aws iam create-policy --policy-name {policy_config.policy_name}"
        create_policy_cmd += f" --policy-document file://{policy_config.policy_name.lower()}-policy.json"
        create_policy_cmd += f" --description '{policy_config.description}'"
        create_policy_cmd += f" --path {policy_config.path}"
        commands.append(create_policy_cmd)
        
        # Attach policy to role
        attach_cmd = f"aws iam attach-role-policy --role-name {role_config.role_name}"
        attach_cmd += f" --policy-arn arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):policy{policy_config.path}{policy_config.policy_name}"
        commands.append(attach_cmd)
        
        # Create instance profile (for EC2)
        commands.append("")
        commands.append("# Create instance profile for EC2 (optional)")
        commands.append(f"aws iam create-instance-profile --instance-profile-name {role_config.role_name}-profile")
        commands.append(f"aws iam add-role-to-instance-profile --instance-profile-name {role_config.role_name}-profile --role-name {role_config.role_name}")
        
        # Add tags
        if role_config.tags:
            commands.append("")
            commands.append("# Add tags to role")
            tag_specs = []
            for key, value in role_config.tags.items():
                tag_specs.append(f"Key={key},Value={value}")
            tag_cmd = f"aws iam tag-role --role-name {role_config.role_name} --tags {' '.join(tag_specs)}"
            commands.append(tag_cmd)
        
        return commands


    def _generate_trust_policy(self, trust_policy_type: str, cross_account_id: Optional[str] = None) -> Dict:
        """Generate trust policy based on type."""
        if trust_policy_type == "ec2":
            return {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
        elif trust_policy_type == "lambda":
            return {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
        elif trust_policy_type == "ecs":
            return {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
        elif trust_policy_type == "cross-account":
            return {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": f"arn:aws:iam::{cross_account_id}:root"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
        else:
            # Default trust policy
            return {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole"
                    }
                ]
            }
    
    def _sanitize_role_name(self, role_name: str) -> str:
        """Sanitize role name to meet AWS requirements."""
        import re
        # Remove invalid characters and replace with hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9+=,.@_-]', '-', role_name)
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        return sanitized[:64]  # Max length 64 characters
    
    def _generate_terraform_config(self, role_data: Dict) -> str:
        """Generate Terraform configuration as a string."""
        terraform_hcl = f'''# IAM Role and Policy Configuration
# Generated by IAM Generator

resource "aws_iam_role" "{self._terraform_name(role_data['role_name'])}" {{
  name        = "{role_data['role_name']}"
  description = "{role_data['description']}"
  
  assume_role_policy = jsonencode({json.dumps(role_data['assume_role_policy'], indent=2)})
  
  tags = {{
    Name      = "{role_data['role_name']}"
    Generator = "IAMGenerator"
  }}
}}

resource "aws_iam_policy" "{self._terraform_name(role_data['role_name'])}_policy" {{
  name        = "{role_data['role_name']}_policy"
  description = "Policy for {role_data['role_name']}"
  
  policy = jsonencode({json.dumps(role_data['policy_document'], indent=2)})
  
  tags = {{
    Name      = "{role_data['role_name']}_policy"
    Generator = "IAMGenerator"
  }}
}}

resource "aws_iam_role_policy_attachment" "{self._terraform_name(role_data['role_name'])}_attachment" {{
  role       = aws_iam_role.{self._terraform_name(role_data['role_name'])}.name
  policy_arn = aws_iam_policy.{self._terraform_name(role_data['role_name'])}_policy.arn
}}

# Outputs
output "{self._terraform_name(role_data['role_name'])}_arn" {{
  description = "ARN of the IAM role"
  value       = aws_iam_role.{self._terraform_name(role_data['role_name'])}.arn
}}

output "{self._terraform_name(role_data['role_name'])}_policy_arn" {{
  description = "ARN of the IAM policy"
  value       = aws_iam_policy.{self._terraform_name(role_data['role_name'])}_policy.arn
}}
'''
        return terraform_hcl

    def _generate_cloudformation_config(self, role_data: Dict) -> Dict:
        """Generate CloudFormation template as a dictionary."""
        return {
            "AWSTemplateFormatVersion": "2010-09-09",
            "Description": f"IAM Role and Policy for {role_data['role_name']}",
            "Resources": {
                f"{role_data['role_name']}Role": {
                    "Type": "AWS::IAM::Role",
                    "Properties": {
                        "RoleName": role_data['role_name'],
                        "Description": role_data['description'],
                        "AssumeRolePolicyDocument": role_data['assume_role_policy']
                    }
                },
                f"{role_data['role_name']}Policy": {
                    "Type": "AWS::IAM::Policy",
                    "Properties": {
                        "PolicyName": f"{role_data['role_name']}_policy",
                        "PolicyDocument": role_data['policy_document'],
                        "Roles": [{"Ref": f"{role_data['role_name']}Role"}]
                    }
                }
            },
            "Outputs": {
                "RoleArn": {
                    "Description": "ARN of the created IAM role",
                    "Value": {"Fn::GetAtt": [f"{role_data['role_name']}Role", "Arn"]}
                },
                "PolicyArn": {
                    "Description": "ARN of the created IAM policy",
                    "Value": {"Ref": f"{role_data['role_name']}Policy"}
                }
            }
        }

    def _generate_aws_cli_commands(self, role_data: Dict) -> List[str]:
        """Generate AWS CLI commands as a list of strings."""
        commands = [
            f"# Create IAM role {role_data['role_name']}",
            "",
            "# Create trust policy file",
            "cat > trust-policy.json << 'EOF'",
            json.dumps(role_data['assume_role_policy'], indent=2),
            "EOF",
            "",
            "# Create permissions policy file",
            "cat > permissions-policy.json << 'EOF'",
            json.dumps(role_data['policy_document'], indent=2),
            "EOF",
            "",
            f"# Create the IAM role",
            f"aws iam create-role --role-name {role_data['role_name']} --assume-role-policy-document file://trust-policy.json --description '{role_data['description']}'",
            "",
            f"# Create the IAM policy",
            f"aws iam create-policy --policy-name {role_data['role_name']}_policy --policy-document file://permissions-policy.json --description 'Policy for {role_data['role_name']}'",
            "",
            f"# Attach policy to role",
            f"aws iam attach-role-policy --role-name {role_data['role_name']} --policy-arn arn:aws:iam::ACCOUNT_ID:policy/{role_data['role_name']}_policy",
            "",
            "# Clean up temporary files",
            "rm trust-policy.json permissions-policy.json"
        ]
        return commands

    def _terraform_name(self, name: str) -> str:
        """Convert role name to Terraform-safe identifier."""
        import re
        # Convert to lowercase and replace invalid chars with underscores
        terraform_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        # Remove consecutive underscores
        terraform_name = re.sub(r'_+', '_', terraform_name)
        # Remove leading/trailing underscores
        terraform_name = terraform_name.strip('_').lower()
        return terraform_name
    
    def generate_service_specific_role(self, service: str, commands: List[str], **kwargs) -> GeneratedRole:
        """
        Generate a role optimized for a specific AWS service.
        
        Args:
            service: AWS service name (lambda, ecs, ec2, etc.)
            commands: List of AWS CLI commands
            **kwargs: Additional configuration
            
        Returns:
            GeneratedRole optimized for the service
        """
        trust_policies = {
            'lambda': self.lambda_trust_policy(),
            'ecs': self.ecs_trust_policy(),
            'ec2': self._default_trust_policy()
        }
        
        trust_policy = trust_policies.get(service, self._default_trust_policy())
        role_name = kwargs.get('role_name', f"{service.title()}Role")
        
        return self.generate_role(
            commands=commands,
            role_name=role_name,
            trust_policy=trust_policy,
            **kwargs
        )


# Example usage
if __name__ == "__main__":
    generator = IAMRoleGenerator()
    
    commands = [
        "aws s3 ls",
        "aws s3 cp file.txt s3://my-bucket/",
        "aws ec2 describe-instances",
        "aws logs get-log-events --log-group-name my-log-group"
    ]
    
    # Generate a basic role
    role = generator.generate_role(
        commands=commands,
        role_name="MyApplicationRole",
        description="Role for my application"
    )
    
    print("Generated Role Configuration:")
    print(f"Role Name: {role.role_config.role_name}")
    print(f"Policy Name: {role.policy_config.policy_name}")
    print("\nTerraform Configuration:")
    print(role.terraform_config)
    
    print("\nAWS CLI Commands:")
    for cmd in role.aws_cli_commands:
        print(cmd)
