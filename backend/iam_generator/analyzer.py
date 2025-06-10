"""
IAM Permission Analyzer

This module provides the main analysis functionality that combines command parsing
with permission lookup to generate comprehensive IAM role requirements.
"""

import json
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .parser import AWSCLIParser, ParsedCommand
from .permissions_db import IAMPermissionsDatabase, IAMPermission, CommandPermissions

# Import the auto-discovery system
try:
    from .auto_discovery import EnhancedPermissionsDatabase, create_enhanced_database
    AUTO_DISCOVERY_AVAILABLE = True
except ImportError:
    AUTO_DISCOVERY_AVAILABLE = False

# Import the documentation scraper for fallback functionality
try:
    from .doc_scraper import AWSCLIDocumentationScraper
    DOC_SCRAPER_AVAILABLE = True
except ImportError:
    DOC_SCRAPER_AVAILABLE = False


class AnalysisResult(BaseModel):
    """Result of IAM permission analysis."""
    
    commands: List[ParsedCommand] = Field(description="Parsed commands")
    required_permissions: List[IAMPermission] = Field(description="All required permissions")
    policy_document: Dict = Field(description="Generated IAM policy document")
    missing_commands: List[str] = Field(default_factory=list, description="Commands not found in database")
    warnings: List[str] = Field(default_factory=list, description="Analysis warnings")
    resource_arns: List[str] = Field(default_factory=list, description="Identified resource ARNs")
    services_used: List[str] = Field(default_factory=list, description="AWS services used")


class ResourceSpecificPolicy(BaseModel):
    """Resource-specific policy configuration."""
    
    service: str
    resource_type: str
    resource_identifiers: List[str]
    actions: List[str]
    arn_patterns: List[str]


class IAMPermissionAnalyzer:
    """Main analyzer for AWS CLI commands and IAM permissions."""
    
    def __init__(self, enable_auto_discovery: bool = True, debug_mode: bool = False):
        """Initialize the analyzer.
        
        Args:
            enable_auto_discovery: Enable automatic discovery of new services/commands
            debug_mode: Enable debug warnings for fallback permissions
        """
        self.parser = AWSCLIParser()
        self.debug_mode = debug_mode
        
        # Use enhanced database if auto-discovery is available
        if AUTO_DISCOVERY_AVAILABLE and enable_auto_discovery:
            self.permissions_db = create_enhanced_database(
                enable_auto_discovery=True,
                enable_background_preload=True
            )
            self.auto_discovery_enabled = True
        else:
            self.permissions_db = IAMPermissionsDatabase()
            self.auto_discovery_enabled = False
        
        # Initialize documentation scraper for fallback functionality
        if DOC_SCRAPER_AVAILABLE:
            self._doc_scraper = AWSCLIDocumentationScraper()
            self._scraper_cache = {}  # Cache for discovered services/commands
        else:
            self._doc_scraper = None
            self._scraper_cache = None
    
    def analyze_command(self, command: str, 
                       strict_resources: bool = False,
                       include_read_only: bool = True) -> Dict:
        """
        Analyze a single AWS CLI command and generate IAM requirements.
        
        Args:
            command: AWS CLI command string
            strict_resources: If True, generate resource-specific ARN patterns
            include_read_only: If True, include basic read permissions
            
        Returns:
            Dict with analysis results for backward compatibility with tests
        """
        # Use analyze_commands for single command
        result = self.analyze_commands([command], strict_resources, include_read_only)
        
        if not result.commands:
            raise ValueError(f"Failed to parse command: {command}")
        
        parsed_cmd = result.commands[0]
        
        # Return format expected by tests
        return {
            "service": parsed_cmd.service,
            "action": parsed_cmd.action,
            "original_command": command,
            "required_permissions": [
                {
                    "action": perm.action,
                    "resource": perm.resource,
                    "condition": perm.condition
                }
                for perm in result.required_permissions
            ],
            "policy_document": result.policy_document,
            "resource_arns": result.resource_arns,
            "warnings": result.warnings
        }
    
    def analyze_commands(self, commands: List[str], 
                        strict_resources: bool = False,
                        include_read_only: bool = True) -> AnalysisResult:
        """
        Analyze a list of AWS CLI commands and generate IAM requirements.
        
        Args:
            commands: List of AWS CLI command strings
            strict_resources: If True, generate resource-specific ARN patterns
            include_read_only: If True, include basic read permissions
            
        Returns:
            AnalysisResult with comprehensive analysis
        """
        parsed_commands = []
        all_permissions = []
        missing_commands = []
        warnings = []
        all_resource_arns = []
        services_used = set()
        
        # Parse and analyze each command
        for command_str in commands:
            try:
                # Parse command
                parsed_cmd = self.parser.parse_command(command_str)
                parsed_commands.append(parsed_cmd)
                services_used.add(parsed_cmd.service)
                
                # Get permissions from database
                cmd_perms = self.permissions_db.get_permissions_object(
                    parsed_cmd.service, parsed_cmd.action
                )
                
                if cmd_perms:
                    # Add permissions, optionally modifying resources
                    command_permissions = []
                    for perm in cmd_perms.permissions:
                        modified_perm = self._customize_permission_resource(
                            perm, parsed_cmd, strict_resources
                        )
                        command_permissions.append(modified_perm)
                    
                    # Enhance with additional permissions
                    enhanced_permissions = self._enhance_with_additional_permissions(
                        command_permissions, parsed_cmd
                    )
                    all_permissions.extend(enhanced_permissions)
                    
                    # Collect resource ARNs
                    all_resource_arns.extend(parsed_cmd.resource_arns)
                    
                else:
                    # Command not in database
                    missing_commands.append(command_str)
                    
                    # Only generate fallback permission if service is supported
                    supported_services = self.permissions_db.get_supported_services()
                    if parsed_cmd.service in supported_services:
                        # Generate best-guess permission for supported service
                        fallback_perm = self._generate_fallback_permission(parsed_cmd)
                        all_permissions.append(fallback_perm)
                        
                        if self.debug_mode:
                            warnings.append(
                                f"Command '{command_str}' not found in permissions database. "
                                f"Generated fallback permission: {fallback_perm.action}"
                            )
                    else:
                        # Try using documentation scraper as fallback
                        scraper_permissions = self._get_scraper_permissions(parsed_cmd)
                        if scraper_permissions:
                            all_permissions.extend(scraper_permissions)
                            if self.debug_mode:
                                warnings.append(
                                    f"Command '{command_str}' not found in permissions database. "
                                    f"Used doc scraper fallback: {[perm.action for perm in scraper_permissions]}"
                                )
                        else:
                            # Try fallback for unknown service
                            fallback_permissions = self._try_scraper_for_unknown_service(parsed_cmd)
                            if fallback_permissions:
                                all_permissions.extend(fallback_permissions)
                                if self.debug_mode:
                                    warnings.append(
                                        f"Unknown service '{parsed_cmd.service}' - used doc scraper: {[perm.action for perm in fallback_permissions]}"
                                    )
                            else:
                                # Last resort - generate basic fallback
                                fallback_perm = self._generate_fallback_permission(parsed_cmd)
                                all_permissions.append(fallback_perm)
                                if self.debug_mode:
                                    warnings.append(
                                        f"Unknown command '{command_str}' - generated basic fallback: {fallback_perm.action}"
                                    )
            
            except ValueError as e:
                warnings.append(f"Failed to parse command '{command_str}': {str(e)}")
                continue
        
        # Add read-only permissions if requested
        if include_read_only:
            read_only_perms = self._get_read_only_permissions(services_used)
            all_permissions.extend(read_only_perms)
        
        # Remove duplicate permissions
        unique_permissions = self._deduplicate_permissions(all_permissions)
        
        # Generate policy document
        policy_doc = self._generate_policy_document(unique_permissions)
        
        return AnalysisResult(
            commands=parsed_commands,
            required_permissions=unique_permissions,
            policy_document=policy_doc,
            missing_commands=missing_commands,
            warnings=warnings,
            resource_arns=list(set(all_resource_arns)),
            services_used=list(services_used)
        )
    
    def analyze_single_command(self, command: str) -> AnalysisResult:
        """
        Analyze a single AWS CLI command.
        
        Args:
            command: AWS CLI command string
            
        Returns:
            AnalysisResult for the single command
        """
        return self.analyze_commands([command])
    
    def generate_least_privilege_policy(self, commands: List[str], 
                                      account_id: Optional[str] = None,
                                      region: Optional[str] = None) -> Dict:
        """
        Generate a least-privilege IAM policy for the given commands.
        
        Args:
            commands: List of AWS CLI commands
            account_id: AWS account ID for resource ARNs
            region: AWS region for resource ARNs
            
        Returns:
            Least-privilege IAM policy document
        """
        analysis = self.analyze_commands(commands, strict_resources=True)
        
        # Enhance ARN patterns with account and region info
        if account_id or region:
            policy_doc = self._enhance_arn_patterns(
                analysis.policy_document, account_id, region
            )
        else:
            policy_doc = analysis.policy_document
        
        # Add conditions for enhanced security
        policy_doc = self._add_security_conditions(policy_doc)
        
        return policy_doc
    
    def generate_resource_specific_policy(self, commands: List[str], 
                                        account_id: Optional[str] = None,
                                        region: Optional[str] = None,
                                        strict_mode: bool = True) -> Dict:
        """
        Generate IAM policy with resource-specific ARNs instead of wildcards.
        
        Args:
            commands: List of AWS CLI commands
            account_id: AWS account ID for ARN generation
            region: AWS region for ARN generation
            strict_mode: If True, use specific resources whenever possible
            
        Returns:
            Enhanced policy with resource-specific permissions
        """
        # Analyze commands with strict resource mode
        analysis = self.analyze_commands(commands, strict_resources=strict_mode)
        
        # Create enhanced permissions with specific resources
        enhanced_permissions = []
        
        for cmd in analysis.commands:
            cmd_perms = self.permissions_db.get_permissions_object(cmd.service, cmd.action)
            if not cmd_perms:
                continue
                
            for perm in cmd_perms.permissions:
                enhanced_perm = self._create_resource_specific_permission(
                    perm, cmd, account_id, region
                )
                enhanced_permissions.append(enhanced_perm)
        
        # Remove duplicates and generate policy
        unique_permissions = self._deduplicate_permissions(enhanced_permissions)
        policy_doc = self._generate_policy_document(unique_permissions)
        
        # Add metadata about resource specificity
        policy_doc["_metadata"] = {
            "resource_specific": True,
            "account_id": account_id,
            "region": region,
            "commands_analyzed": len(commands),
            "specific_resources_found": sum(1 for cmd in analysis.commands if cmd.resource_arns)
        }
        
        return policy_doc

    def _create_resource_specific_permission(self, permission: IAMPermission, 
                                           parsed_cmd: ParsedCommand,
                                           account_id: Optional[str],
                                           region: Optional[str]) -> IAMPermission:
        """
        Create a resource-specific permission from a generic permission.
        
        Args:
            permission: Original permission with potential wildcards
            parsed_cmd: Parsed command with resource information
            account_id: AWS account ID
            region: AWS region
            
        Returns:
            Enhanced permission with specific resources
        """
        # If we have specific resource ARNs from the command, use them
        if parsed_cmd.resource_arns and self._should_use_specific_resource(
            permission.action, parsed_cmd.service
        ):
            specific_resource = self._select_appropriate_resource_arn(
                permission.action, parsed_cmd.resource_arns
            )
            if specific_resource:
                return IAMPermission(
                    action=permission.action,
                    resource=self._enhance_single_arn(specific_resource, account_id, region),
                    condition=permission.condition,
                    effect=permission.effect
                )
        
        # Try to generate specific ARNs from command parameters
        generated_arns = self._generate_arns_from_command_params(
            parsed_cmd, permission.action, account_id, region
        )
        if generated_arns:
            return IAMPermission(
                action=permission.action,
                resource=generated_arns[0],  # Use first generated ARN
                condition=permission.condition,
                effect=permission.effect
            )
        
        # Enhance existing ARN pattern with account/region if available
        enhanced_resource = self._enhance_single_arn(
            permission.resource, account_id, region
        )
        
        return IAMPermission(
            action=permission.action,
            resource=enhanced_resource,
            condition=permission.condition,
            effect=permission.effect
        )

    def _generate_arns_from_command_params(self, parsed_cmd: ParsedCommand, 
                                         action: str,
                                         account_id: Optional[str],
                                         region: Optional[str]) -> List[str]:
        """
        Generate specific ARNs from command parameters.
        
        Args:
            parsed_cmd: Parsed command
            action: IAM action
            account_id: AWS account ID
            region: AWS region
            
        Returns:
            List of generated ARNs
        """
        arns = []
        service = parsed_cmd.service
        params = parsed_cmd.parameters
        
        # S3 specific ARN generation
        if service == "s3":
            if action == "s3:ListBucket":
                # Extract bucket names from s3:// URIs
                for value in params.values():
                    if isinstance(value, str) and value.startswith("s3://"):
                        bucket_name = value.replace("s3://", "").split("/")[0]
                        arns.append(f"arn:aws:s3:::{bucket_name}")
                        
            elif action in ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]:
                # Extract object ARNs
                for value in params.values():
                    if isinstance(value, str) and value.startswith("s3://"):
                        s3_uri = value.replace("s3://", "")
                        if "/" in s3_uri:
                            bucket_name = s3_uri.split("/")[0]
                            object_key = "/".join(s3_uri.split("/")[1:])
                            if object_key:
                                arns.append(f"arn:aws:s3:::{bucket_name}/{object_key}")
                            else:
                                arns.append(f"arn:aws:s3:::{bucket_name}/*")
                        else:
                            arns.append(f"arn:aws:s3:::{s3_uri}/*")
        
        # EC2 specific ARN generation
        elif service == "ec2":
            account = account_id or "*"
            reg = region or "*"
            
            if "instance" in action.lower():
                instance_params = ["instance-ids", "instance-id"]
                for param in instance_params:
                    if param in params:
                        instances = params[param]
                        if isinstance(instances, str):
                            instances = [instances]
                        for instance_id in instances:
                            arns.append(f"arn:aws:ec2:{reg}:{account}:instance/{instance_id}")
            
            elif "volume" in action.lower():
                volume_params = ["volume-ids", "volume-id"]
                for param in volume_params:
                    if param in params:
                        volumes = params[param]
                        if isinstance(volumes, str):
                            volumes = [volumes]
                        for volume_id in volumes:
                            arns.append(f"arn:aws:ec2:{reg}:{account}:volume/{volume_id}")
        
        # Lambda specific ARN generation
        elif service == "lambda":
            account = account_id or "*"
            reg = region or "*"
            
            if "function-name" in params:
                function_name = params["function-name"]
                arns.append(f"arn:aws:lambda:{reg}:{account}:function:{function_name}")
        
        # DynamoDB specific ARN generation
        elif service == "dynamodb":
            account = account_id or "*"
            reg = region or "*"
            
            if "table-name" in params:
                table_name = params["table-name"]
                arns.append(f"arn:aws:dynamodb:{reg}:{account}:table/{table_name}")
        
        # IAM specific ARN generation
        elif service == "iam":
            account = account_id or "*"
            
            if "role-name" in params:
                role_name = params["role-name"]
                arns.append(f"arn:aws:iam::{account}:role/{role_name}")
            elif "user-name" in params:
                user_name = params["user-name"]
                arns.append(f"arn:aws:iam::{account}:user/{user_name}")
            elif "policy-name" in params:
                policy_name = params["policy-name"]
                arns.append(f"arn:aws:iam::{account}:policy/{policy_name}")
        
        return arns
    
    def _customize_permission_resource(self, permission: IAMPermission, 
                                     parsed_cmd: ParsedCommand,
                                     strict_resources: bool) -> IAMPermission:
        """
        Customize permission resource based on parsed command.
        
        Args:
            permission: Original permission
            parsed_cmd: Parsed command with resource info
            strict_resources: Whether to use strict resource patterns
            
        Returns:
            Modified permission with updated resource
        """
        # Always use specific resource ARNs when available and appropriate
        if parsed_cmd.resource_arns:
            # For certain actions, use specific resources even in non-strict mode
            if self._should_use_specific_resource(permission.action, parsed_cmd.service):
                resource = self._select_appropriate_resource_arn(permission.action, parsed_cmd.resource_arns)
                if resource:
                    return IAMPermission(
                        action=permission.action,
                        resource=resource,
                        condition=permission.condition,
                        effect=permission.effect
                    )
        
        # Fallback to strict_resources behavior
        if strict_resources and parsed_cmd.resource_arns:
            resource = parsed_cmd.resource_arns[0] if parsed_cmd.resource_arns else permission.resource
            return IAMPermission(
                action=permission.action,
                resource=resource,
                condition=permission.condition,
                effect=permission.effect
            )
        
        return permission
    
    def _enhance_with_additional_permissions(self, permissions: List[IAMPermission], 
                                           parsed_command: ParsedCommand) -> List[IAMPermission]:
        """
        Enhance permissions with additional commonly needed permissions.
        
        Args:
            permissions: Base permissions
            parsed_command: The parsed command
            
        Returns:
            Enhanced permissions list
        """
        enhanced_permissions = permissions.copy()
        
        # For S3 cp operations with multiple buckets, ensure both buckets are covered
        if (parsed_command.service == "s3" and parsed_command.action == "cp" 
            and len(parsed_command.resource_arns) > 1):
            
            # Find bucket ARNs (without object paths)
            bucket_arns = [arn for arn in parsed_command.resource_arns 
                          if arn.startswith("arn:aws:s3:::") and "/" not in arn.split(":::")[-1]]
            
            # For each bucket, ensure we have ListBucket permission
            for bucket_arn in bucket_arns:
                # Check if we already have ListBucket for this bucket
                has_list_permission = any(
                    perm.action == "s3:ListBucket" and bucket_arn in str(perm.resource)
                    for perm in enhanced_permissions
                )
                
                if not has_list_permission:
                    enhanced_permissions.append(IAMPermission(
                        action="s3:ListBucket",
                        resource=bucket_arn,
                        condition=None,
                        effect="Allow"
                    ))
            
            # For S3 cp, we also need PutObject permissions on destination buckets
            # Since we can't easily distinguish source vs dest, add PutObject for all buckets
            for bucket_arn in bucket_arns:
                enhanced_permissions.append(IAMPermission(
                    action="s3:PutObject",
                    resource=bucket_arn + "/*",
                    condition=None,
                    effect="Allow"
                ))
                
                enhanced_permissions.append(IAMPermission(
                    action="s3:GetObject", 
                    resource=bucket_arn + "/*",
                    condition=None,
                    effect="Allow"
                ))
        
        return enhanced_permissions
    
    def _generate_fallback_permission(self, parsed_cmd: ParsedCommand) -> IAMPermission:
        """
        Generate a fallback permission for unknown commands.
        
        Args:
            parsed_cmd: Parsed command
            
        Returns:
            Fallback IAM permission
        """
        # Convert CLI action to IAM action format
        iam_action = self.permissions_db._convert_action_to_iam(parsed_cmd.action)
        action = f"{parsed_cmd.service}:{iam_action}"
        
        return IAMPermission(
            action=action,
            resource="*"
        )
    
    def _get_read_only_permissions(self, services: Set[str]) -> List[IAMPermission]:
        """
        Get basic read-only permissions for services.
        
        Args:
            services: Set of AWS service names
            
        Returns:
            List of read-only permissions
        """
        read_only_perms = []
        
        read_only_actions = {
            "s3": ["s3:ListBucket", "s3:GetBucketLocation", "s3:ListAllMyBuckets"],
            "ec2": ["ec2:Describe*"],
            "iam": ["iam:List*", "iam:Get*"],
            "lambda": ["lambda:List*", "lambda:Get*"],
            "logs": ["logs:Describe*"],
            "sts": ["sts:GetCallerIdentity"],
        }
        
        for service in services:
            if service in read_only_actions:
                for action in read_only_actions[service]:
                    read_only_perms.append(IAMPermission(action=action, resource="*"))
        
        return read_only_perms
    
    def _deduplicate_permissions(self, permissions: List[IAMPermission]) -> List[IAMPermission]:
        """
        Remove duplicate permissions, preferring specific resources over wildcards.
        
        Args:
            permissions: List of permissions
            
        Returns:
            Deduplicated list of permissions
        """
        # Group permissions by action and condition
        action_groups = {}
        
        for perm in permissions:
            # Create a key based on action and condition (but not resource)
            key = (perm.action, str(perm.condition), perm.effect)
            
            if key not in action_groups:
                action_groups[key] = []
            action_groups[key].append(perm)
        
        # For each action group, prefer specific resources over wildcards
        unique_perms = []
        for group in action_groups.values():
            if len(group) == 1:
                unique_perms.append(group[0])
            else:
                # Sort by resource specificity - specific resources first, wildcards last
                sorted_group = sorted(group, key=lambda p: (p.resource == "*", p.resource))
                
                # If we have both specific and wildcard resources, only keep specific ones
                specific_resources = [p for p in sorted_group if p.resource != "*"]
                if specific_resources:
                    unique_perms.extend(specific_resources)
                else:
                    # All are wildcards, keep just one
                    unique_perms.append(sorted_group[0])
        
        return unique_perms
    
    def _generate_policy_document(self, permissions: List[IAMPermission]) -> Dict:
        """
        Generate IAM policy document from permissions.
        
        Args:
            permissions: List of IAM permissions
            
        Returns:
            IAM policy document
        """
        # Group permissions by resource and effect
        resource_groups = {}
        
        for perm in permissions:
            key = (perm.resource, perm.effect, str(perm.condition))
            
            if key not in resource_groups:
                resource_groups[key] = {
                    "Effect": perm.effect,
                    "Action": [],
                    "Resource": perm.resource
                }
                if perm.condition:
                    resource_groups[key]["Condition"] = perm.condition
            
            resource_groups[key]["Action"].append(perm.action)
        
        # Sort actions and remove duplicates
        statements = []
        for group in resource_groups.values():
            group["Action"] = sorted(list(set(group["Action"])))
            statements.append(group)
        
        return {
            "Version": "2012-10-17",
            "Statement": statements
        }
    
    def _enhance_arn_patterns(self, policy_doc: Dict, 
                            account_id: Optional[str] = None,
                            region: Optional[str] = None) -> Dict:
        """
        Enhance ARN patterns with specific account and region.
        
        Args:
            policy_doc: Original policy document
            account_id: AWS account ID
            region: AWS region
            
        Returns:
            Enhanced policy document
        """
        if not account_id and not region:
            return policy_doc
        
        enhanced_doc = policy_doc.copy()
        
        for statement in enhanced_doc["Statement"]:
            resource = statement.get("Resource", "*")
            
            if isinstance(resource, str) and resource == "*":
                continue
            
            # Enhance resource ARNs
            if isinstance(resource, list):
                enhanced_resources = []
                for res in resource:
                    enhanced_res = self._enhance_single_arn(res, account_id, region)
                    enhanced_resources.append(enhanced_res)
                statement["Resource"] = enhanced_resources
            else:
                statement["Resource"] = self._enhance_single_arn(resource, account_id, region)
        
        return enhanced_doc
    
    def _enhance_single_arn(self, arn: str, account_id: Optional[str], region: Optional[str]) -> str:
        """Enhance a single ARN with account and region info."""
        if not arn.startswith("arn:aws:"):
            return arn
        
        parts = arn.split(":")
        if len(parts) >= 6:
            # parts: ["arn", "aws", "service", "region", "account", "resource"]
            if account_id and parts[4] == "*":
                parts[4] = account_id
            if region and parts[3] == "*":
                parts[3] = region
            
            return ":".join(parts)
        
        return arn
    
    def _add_security_conditions(self, policy_doc: Dict) -> Dict:
        """
        Add security conditions to policy statements.
        
        Args:
            policy_doc: Original policy document
            
        Returns:
            Policy document with security conditions
        """
        enhanced_doc = policy_doc.copy()
        
        # Common security conditions
        security_conditions = {
            "Bool": {
                "aws:SecureTransport": "true"
            }
        }
        
        for statement in enhanced_doc["Statement"]:
            # Add secure transport condition for data operations
            actions = statement.get("Action", [])
            if isinstance(actions, str):
                actions = [actions]
            
            data_actions = [
                action for action in actions 
                if any(keyword in action.lower() for keyword in 
                      ["get", "put", "post", "upload", "download"])
            ]
            
            if data_actions:
                existing_conditions = statement.get("Condition", {})
                # Merge conditions
                for key, value in security_conditions.items():
                    if key in existing_conditions:
                        existing_conditions[key].update(value)
                    else:
                        existing_conditions[key] = value
                
                statement["Condition"] = existing_conditions
        
        return enhanced_doc
    
    def get_service_summary(self, commands: List[str]) -> Dict[str, Dict]:
        """
        Get a summary of services and actions used.
        
        Args:
            commands: List of AWS CLI commands
            
        Returns:
            Summary dictionary with services and their actions
        """
        analysis = self.analyze_commands(commands)
        summary = {}
        
        for cmd in analysis.commands:
            if cmd.service not in summary:
                summary[cmd.service] = {
                    "actions": set(),
                    "permissions": set(),
                    "resources": set()
                }
            
            summary[cmd.service]["actions"].add(cmd.action)
            summary[cmd.service]["resources"].update(cmd.resource_arns)
        
        # Add permissions
        for perm in analysis.required_permissions:
            service = perm.action.split(":")[0] if ":" in perm.action else "unknown"
            if service in summary:
                summary[service]["permissions"].add(perm.action)
        
        # Convert sets to lists for JSON serialization
        for service_data in summary.values():
            for key in service_data:
                if isinstance(service_data[key], set):
                    service_data[key] = list(service_data[key])
        
        return summary

    def get_auto_discovery_stats(self) -> Dict:
        """
        Get comprehensive auto-discovery statistics.
        
        Returns:
            Dictionary with auto-discovery statistics and performance metrics
        """
        if not self.auto_discovery_enabled or not hasattr(self.permissions_db, 'get_auto_discovery_stats'):
            return {
                'auto_discovery_enabled': False,
                'message': 'Auto-discovery is not enabled or available'
            }
        
        # Get stats from the enhanced database
        stats = self.permissions_db.get_auto_discovery_stats()
        
        # Add additional analyzer-level stats
        stats.update({
            'analyzer_cache_size': len(self._scraper_cache) if self._scraper_cache else 0,
            'scraper_available': DOC_SCRAPER_AVAILABLE,
            'auto_discovery_available': AUTO_DISCOVERY_AVAILABLE,
            'supported_manual_services': len(self.permissions_db.get_supported_services()) if hasattr(self.permissions_db, 'get_supported_services') else 0
        })
        
        return stats

    def _get_scraper_permissions(self, parsed_cmd: ParsedCommand) -> List[IAMPermission]:
        """
        Get permissions using documentation scraper for known services.
        
        Args:
            parsed_cmd: Parsed command
            
        Returns:
            List of IAM permissions from scraper, or empty list if unavailable
        """
        if not DOC_SCRAPER_AVAILABLE or not self._doc_scraper:
            return []
        
        try:
            # Use cached result if available
            cache_key = f"{parsed_cmd.service}:{parsed_cmd.action}"
            if self._scraper_cache and cache_key in self._scraper_cache:
                return self._scraper_cache[cache_key]
            
            # Try to map the command using the scraper
            command_perms = self._doc_scraper.map_command_to_permissions(
                parsed_cmd.service, parsed_cmd.action
            )
            
            # Cache the result
            if self._scraper_cache is not None:
                self._scraper_cache[cache_key] = command_perms.permissions
            
            return command_perms.permissions
            
        except Exception as e:
            # Log the error but don't fail - fallback to other methods
            print(f"Warning: Scraper failed for {parsed_cmd.service} {parsed_cmd.action}: {e}")
            return []
    
    def _try_scraper_for_unknown_service(self, parsed_cmd: ParsedCommand) -> List[IAMPermission]:
        """
        Try using scraper for completely unknown services.
        
        Args:
            parsed_cmd: Parsed command
            
        Returns:
            List of IAM permissions from scraper, or empty list if unavailable
        """
        if not DOC_SCRAPER_AVAILABLE or not self._doc_scraper:
            return []
        
        try:
            # Check if the scraper knows about this service
            services = self._doc_scraper.discover_services()
            if parsed_cmd.service in services:
                # Service exists, try to discover the command
                commands = self._doc_scraper.discover_commands(parsed_cmd.service)
                command_names = [cmd.command for cmd in commands]
                
                if parsed_cmd.action in command_names:
                    # Command exists, map it to permissions
                    command_perms = self._doc_scraper.map_command_to_permissions(
                        parsed_cmd.service, parsed_cmd.action
                    )
                    return command_perms.permissions
            
            return []
            
        except Exception as e:
            # Log the error but don't fail
            print(f"Warning: Unknown service scraper failed for {parsed_cmd.service}: {e}")
            return []

    def _should_use_specific_resource(self, action: str, service: str) -> bool:
        """
        Determine whether to use specific resource ARNs for an action/service combination.
        
        Args:
            action: IAM action (e.g., "s3:GetObject")
            service: AWS service (e.g., "s3")
            
        Returns:
            True if specific resources should be used, False otherwise
        """
        # Define actions that should use specific resources when available
        specific_resource_actions = {
            "s3": {
                "s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:GetObjectAcl",
                "s3:PutObjectAcl", "s3:ListBucket", "s3:GetBucketLocation", 
                "s3:GetBucketAcl", "s3:PutBucketAcl"
            },
            "ec2": {
                "ec2:TerminateInstances", "ec2:StopInstances", "ec2:StartInstances",
                "ec2:RebootInstances", "ec2:DescribeInstances", "ec2:ModifyInstanceAttribute",
                "ec2:GetConsoleOutput", "ec2:GetConsoleScreenshot"
            },
            "lambda": {
                "lambda:InvokeFunction", "lambda:GetFunction", "lambda:UpdateFunctionCode",
                "lambda:UpdateFunctionConfiguration", "lambda:DeleteFunction",
                "lambda:AddPermission", "lambda:RemovePermission"
            },
            "dynamodb": {
                "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem",
                "dynamodb:DeleteItem", "dynamodb:Query", "dynamodb:Scan",
                "dynamodb:BatchGetItem", "dynamodb:BatchWriteItem"
            },
            "iam": {
                "iam:GetUser", "iam:GetRole", "iam:GetPolicy", "iam:AttachRolePolicy",
                "iam:DetachRolePolicy", "iam:AttachUserPolicy", "iam:DetachUserPolicy",
                "iam:DeleteUser", "iam:DeleteRole"
            }
        }
        
        service_actions = specific_resource_actions.get(service, set())
        return action in service_actions

    def _select_appropriate_resource_arn(self, action: str, resource_arns: List[str]) -> Optional[str]:
        """
        Select the most appropriate resource ARN for a given action.
        
        Args:
            action: IAM action (e.g., "s3:GetObject")
            resource_arns: List of available resource ARNs
            
        Returns:
            Selected resource ARN or None if no appropriate match
        """
        if not resource_arns:
            return None
            
        # For most cases, just return the first ARN
        # This could be enhanced with more sophisticated matching logic
        service = action.split(":")[0] if ":" in action else ""
        
        # Filter ARNs by service if possible
        matching_arns = [
            arn for arn in resource_arns 
            if service in arn or arn.startswith(f"arn:aws:{service}:")
        ]
        
        if matching_arns:
            return matching_arns[0]
            
        # Fallback to first ARN if no service-specific match
        return resource_arns[0]

# Example usage
if __name__ == "__main__":
    analyzer = IAMPermissionAnalyzer()
    
    commands = [
        "aws s3 ls",
        "aws s3 cp file.txt s3://my-bucket/data/",
        "aws ec2 describe-instances --instance-ids i-1234567890abcdef0",
        "aws iam list-users",
        "aws lambda list-functions --region us-east-1",
        "aws sts assume-role --role-arn arn:aws:iam::123456789012:role/TestRole --role-session-name test"
    ]
    
    # Basic analysis
    result = analyzer.analyze_commands(commands)
    print("Analysis Results:")
    print(f"Commands analyzed: {len(result.commands)}")
    print(f"Services used: {result.services_used}")
    print(f"Permissions required: {len(result.required_permissions)}")
    print(f"Warnings: {len(result.warnings)}")
    
    # Generate policy
    print("\nGenerated IAM Policy:")
    print(json.dumps(result.policy_document, indent=2))
    
    # Least privilege policy
    print("\nLeast Privilege Policy:")
    least_privilege = analyzer.generate_least_privilege_policy(
        commands, account_id="123456789012", region="us-east-1"
    )
    print(json.dumps(least_privilege, indent=2))
