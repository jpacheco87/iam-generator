"""
Enhanced IAM services with policy validation, cross-service dependencies, and conditional policies.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import asdict

from iam_generator.policy_validator import (
    IAMPolicyValidator, 
    PolicyType, 
    ValidationSeverity,
    PolicyValidationResult
)
from iam_generator.analyzer import IAMPermissionAnalyzer
from iam_generator.role_generator import IAMRoleGenerator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedIAMService:
    """
    Enhanced IAM service with advanced features:
    - Policy validation and optimization
    - Cross-service dependency analysis
    - Conditional policy generation
    - Enhanced logging and monitoring
    """
    
    def __init__(self):
        """Initialize the enhanced service."""
        self.validator = IAMPolicyValidator()
        self.analyzer = IAMPermissionAnalyzer()
        self.role_generator = IAMRoleGenerator()
        
        # Cross-service dependencies mapping
        self.service_dependencies = {
            'lambda': {
                'vpc_config': ['ec2:CreateNetworkInterface', 'ec2:DescribeNetworkInterfaces', 'ec2:DeleteNetworkInterface'],
                'cloudwatch_logs': ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
                'xray_tracing': ['xray:PutTraceSegments', 'xray:PutTelemetryRecords'],
                'dead_letter_queue': ['sqs:SendMessage', 'sns:Publish'],
                'layers': ['lambda:GetLayerVersion']
            },
            'ecs': {
                'task_execution': ['ecs:CreateCluster', 'ecs:DescribeClusters', 'ecs:DescribeServices'],
                'ecr_access': ['ecr:GetAuthorizationToken', 'ecr:BatchCheckLayerAvailability', 'ecr:GetDownloadUrlForLayer', 'ecr:BatchGetImage'],
                'cloudwatch_logs': ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents', 'logs:DescribeLogStreams'],
                'auto_scaling': ['application-autoscaling:RegisterScalableTarget', 'application-autoscaling:DescribeScalableTargets'],
                'load_balancer': ['elasticloadbalancing:DescribeTargetGroups', 'elasticloadbalancing:DescribeListeners']
            },
            'rds': {
                'subnet_groups': ['ec2:DescribeSubnets', 'ec2:DescribeVpcs'],
                'security_groups': ['ec2:DescribeSecurityGroups', 'ec2:CreateSecurityGroup'],
                'parameter_groups': ['rds:DescribeDBParameterGroups', 'rds:CreateDBParameterGroup'],
                'monitoring': ['cloudwatch:PutMetricData', 'logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents']
            },
            'ec2': {
                'vpc_resources': ['ec2:DescribeVpcs', 'ec2:DescribeSubnets', 'ec2:DescribeRouteTables'],
                'security_groups': ['ec2:DescribeSecurityGroups', 'ec2:AuthorizeSecurityGroupIngress', 'ec2:AuthorizeSecurityGroupEgress'],
                'key_pairs': ['ec2:DescribeKeyPairs', 'ec2:CreateKeyPair'],
                'ami_access': ['ec2:DescribeImages'],
                'ebs_volumes': ['ec2:DescribeVolumes', 'ec2:CreateVolume', 'ec2:AttachVolume']
            },
            'apigateway': {
                'lambda_integration': ['lambda:InvokeFunction', 'lambda:GetFunction'],
                'cloudwatch_logs': ['logs:CreateLogGroup', 'logs:CreateLogStream', 'logs:PutLogEvents'],
                'iam_roles': ['iam:PassRole'],
                'certificate_manager': ['acm:DescribeCertificate', 'acm:ListCertificates']
            },
            's3': {
                'cloudtrail_logging': ['cloudtrail:PutEvents'],
                'cloudwatch_metrics': ['cloudwatch:PutMetricData'],
                'kms_encryption': ['kms:Decrypt', 'kms:DescribeKey', 'kms:GenerateDataKey']
            }
        }
        
        # Common IAM conditions for security
        self.security_conditions = {
            'mfa_required': {
                'Bool': {'aws:MultiFactorAuthPresent': 'true'}
            },
            'mfa_age_limit': {
                'NumericLessThan': {'aws:MultiFactorAuthAge': '3600'}
            },
            'ip_restriction': {
                'IpAddress': {'aws:SourceIp': []}  # To be filled with actual IPs
            },
            'vpce_only': {
                'StringEquals': {'aws:SourceVpce': []}  # To be filled with VPC endpoint IDs
            },
            'secure_transport': {
                'Bool': {'aws:SecureTransport': 'true'}
            },
            'time_restriction': {
                'DateGreaterThan': {'aws:CurrentTime': ''},
                'DateLessThan': {'aws:CurrentTime': ''}
            },
            'user_agent_restriction': {
                'StringLike': {'aws:UserAgent': 'AWS-CLI/*'}
            }
        }
    
    def validate_policy(
        self,
        policy: Dict[str, Any],
        policy_type: str = "managed",
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Validate an IAM policy with comprehensive checks.
        
        Args:
            policy: The IAM policy document
            policy_type: Type of policy (managed, inline_user, inline_role, inline_group)
            account_id: AWS account ID for validation
            
        Returns:
            Validation results with issues and recommendations
        """
        logger.info(f"Validating {policy_type} policy with {len(str(policy))} characters")
        
        try:
            # Map string policy type to enum
            policy_type_enum = PolicyType(policy_type)
        except ValueError:
            policy_type_enum = PolicyType.MANAGED
        
        result = self.validator.validate_policy(policy, policy_type_enum, account_id)
        
        # Convert to dictionary for API response
        return {
            'is_valid': result.is_valid,
            'policy_size': result.policy_size,
            'policy_type': result.policy_type.value,
            'issues': [asdict(issue) for issue in result.issues],
            'score': result.score,
            'recommendations': result.recommendations
        }
    
    def optimize_policy(
        self,
        policy: Dict[str, Any],
        optimization_level: str = "standard",
        account_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Optimize a policy for size and security.
        
        Args:
            policy: Original policy document
            optimization_level: Level of optimization (basic, standard, aggressive)
            account_id: AWS account ID
            
        Returns:
            Optimized policy with applied optimizations
        """
        logger.info(f"Optimizing policy with {optimization_level} level")
        
        original_size = len(json.dumps(policy, separators=(',', ':')))
        optimized_policy = policy.copy()
        optimizations_applied = []
        
        statements = optimized_policy.get('Statement', [])
        if isinstance(statements, dict):
            statements = [statements]
            optimized_policy['Statement'] = statements
        
        # Basic optimizations
        if optimization_level in ['basic', 'standard', 'aggressive']:
            # Remove unnecessary whitespace (already done by JSON serialization)
            
            # Consolidate similar statements
            consolidated_statements = self._consolidate_statements(statements)
            if len(consolidated_statements) < len(statements):
                optimized_policy['Statement'] = consolidated_statements
                optimizations_applied.append(f"Consolidated {len(statements) - len(consolidated_statements)} statements")
        
        # Standard optimizations
        if optimization_level in ['standard', 'aggressive']:
            # Optimize action patterns
            optimized_policy['Statement'] = self._optimize_actions(optimized_policy['Statement'])
            optimizations_applied.append("Optimized action patterns")
            
            # Set latest policy version
            if optimized_policy.get('Version') != '2012-10-17':
                optimized_policy['Version'] = '2012-10-17'
                optimizations_applied.append("Updated to latest policy version")
        
        # Aggressive optimizations
        if optimization_level == 'aggressive':
            # Remove redundant conditions
            optimized_policy['Statement'] = self._optimize_conditions(optimized_policy['Statement'])
            optimizations_applied.append("Optimized conditions")
        
        optimized_size = len(json.dumps(optimized_policy, separators=(',', ':')))
        size_reduction = original_size - optimized_size
        
        # Validate the optimized policy
        validation_result = self.validate_policy(optimized_policy, account_id=account_id)
        
        return {
            'original_policy': policy,
            'optimized_policy': optimized_policy,
            'size_reduction': size_reduction,
            'optimizations_applied': optimizations_applied,
            'validation_result': validation_result
        }
    
    def analyze_cross_service_dependencies(
        self,
        commands: List[str],
        include_implicit: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze cross-service dependencies for given commands.
        
        Args:
            commands: List of AWS CLI commands
            include_implicit: Whether to include implicit dependencies
            
        Returns:
            Analysis results with dependencies and enhanced permissions
        """
        logger.info(f"Analyzing cross-service dependencies for {len(commands)} commands")
        
        # Analyze each command to get base permissions
        base_permissions = []
        services_used = set()
        
        for command in commands:
            try:
                result = self.analyzer.analyze_command(command)
                base_permissions.extend(result['required_permissions'])
                services_used.add(result['service'])
            except Exception as e:
                logger.warning(f"Failed to analyze command '{command}': {e}")
        
        # Identify dependencies
        dependencies = {}
        additional_permissions = []
        
        for service in services_used:
            if service in self.service_dependencies:
                service_deps = self.service_dependencies[service]
                dependencies[service] = list(service_deps.keys())
                
                if include_implicit:
                    # Add implicit permissions based on service usage patterns
                    for dep_type, permissions in service_deps.items():
                        # Add contextual logic here based on command analysis
                        if self._should_include_dependency(commands, service, dep_type):
                            for permission in permissions:
                                additional_permissions.append({
                                    'Effect': 'Allow',
                                    'Action': permission,
                                    'Resource': '*',  # Can be refined based on context
                                    'Dependency': f"{service}:{dep_type}"
                                })
        
        # Create enhanced policy with dependencies
        all_permissions = base_permissions + additional_permissions
        enhanced_policy = self._create_enhanced_policy(all_permissions)
        
        # Create dependency graph
        dependency_graph = self._create_dependency_graph(services_used, dependencies)
        
        return {
            'dependencies': dependencies,
            'additional_permissions': additional_permissions,
            'enhanced_policy': enhanced_policy,
            'dependency_graph': dependency_graph
        }
    
    def generate_conditional_policy(
        self,
        commands: List[str],
        conditions: Dict[str, Any],
        account_id: Optional[str] = None,
        region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a policy with security conditions.
        
        Args:
            commands: AWS CLI commands to analyze
            conditions: Security conditions to apply
            account_id: AWS account ID
            region: AWS region
            
        Returns:
            Policy with applied conditions and security enhancements
        """
        logger.info(f"Generating conditional policy for {len(commands)} commands with {len(conditions)} conditions")
        
        # Analyze base permissions
        base_permissions = []
        for command in commands:
            try:
                result = self.analyzer.analyze_command(command)
                base_permissions.extend(result['required_permissions'])
            except Exception as e:
                logger.warning(f"Failed to analyze command '{command}': {e}")
        
        # Apply conditions to statements
        enhanced_statements = []
        conditions_applied = []
        security_enhancements = []
        
        for permission in base_permissions:
            statement = {
                'Effect': 'Allow',  # Default effect
                'Action': permission.get('action', permission.get('Action', '')),
                'Resource': permission.get('resource', permission.get('Resource', '*'))
            }
            
            # Determine which conditions to apply based on action sensitivity
            applicable_conditions = self._determine_applicable_conditions(
                statement['Action'], conditions
            )
            
            if applicable_conditions:
                statement['Condition'] = applicable_conditions
                conditions_applied.extend(list(applicable_conditions.keys()))
            
            enhanced_statements.append(statement)
        
        # Add security enhancements
        if conditions.get('require_mfa'):
            security_enhancements.append("Multi-factor authentication required for sensitive actions")
        
        if conditions.get('ip_restrictions'):
            security_enhancements.append(f"Access restricted to IP addresses: {conditions['ip_restrictions']}")
        
        if conditions.get('time_restrictions'):
            time_restr = conditions['time_restrictions']
            security_enhancements.append(f"Time-based access restrictions: {time_restr.get('start_time', '00:00')} - {time_restr.get('end_time', '23:59')} {time_restr.get('timezone', 'UTC')}")
        
        if conditions.get('vpc_restrictions'):
            security_enhancements.append(f"VPC access restrictions: {conditions['vpc_restrictions']}")
        
        if conditions.get('require_secure_transport'):
            security_enhancements.append("Secure transport (HTTPS/TLS) required for all data operations")
        
        policy_document = {
            'Version': '2012-10-17',
            'Statement': enhanced_statements
        }
        
        metadata = {
            'commands_analyzed': len(commands),
            'conditions_count': len(set(conditions_applied)),
            'account_id': account_id,
            'region': region,
            'generated_at': 'current_timestamp'  # Would use actual timestamp
        }
        
        return {
            'policy_document': policy_document,
            'conditions_applied': list(set(conditions_applied)),
            'security_enhancements': security_enhancements,
            'metadata': metadata
        }
    
    def _consolidate_statements(self, statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate similar policy statements."""
        # Group statements by effect and resource
        groups = {}
        
        for statement in statements:
            effect = statement.get('Effect', 'Allow')
            resource = json.dumps(statement.get('Resource', '*'), sort_keys=True)
            condition = json.dumps(statement.get('Condition', {}), sort_keys=True)
            
            key = f"{effect}|{resource}|{condition}"
            
            if key not in groups:
                groups[key] = {
                    'Effect': effect,
                    'Action': [],
                    'Resource': statement.get('Resource', '*')
                }
                if 'Condition' in statement:
                    groups[key]['Condition'] = statement['Condition']
            
            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            groups[key]['Action'].extend(actions)
        
        # Convert back to statements
        consolidated = []
        for group in groups.values():
            # Remove duplicates and sort actions
            group['Action'] = sorted(list(set(group['Action'])))
            consolidated.append(group)
        
        return consolidated
    
    def _optimize_actions(self, statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize action patterns in statements."""
        for statement in statements:
            actions = statement.get('Action', [])
            if isinstance(actions, str):
                actions = [actions]
            
            # Group actions by service
            service_actions = {}
            for action in actions:
                if ':' in action:
                    service, action_name = action.split(':', 1)
                    if service not in service_actions:
                        service_actions[service] = []
                    service_actions[service].append(action_name)
            
            # Optimize service action patterns
            optimized_actions = []
            for service, service_action_list in service_actions.items():
                if len(service_action_list) > 3:  # If many actions, consider wildcard
                    # Check if actions follow a pattern
                    if self._can_use_wildcard(service_action_list):
                        optimized_actions.append(f"{service}:*")
                    else:
                        optimized_actions.extend([f"{service}:{action}" for action in service_action_list])
                else:
                    optimized_actions.extend([f"{service}:{action}" for action in service_action_list])
            
            statement['Action'] = optimized_actions
        
        return statements
    
    def _optimize_conditions(self, statements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize conditions in statements."""
        # This is a placeholder for condition optimization logic
        # Could include removing redundant conditions, consolidating similar conditions, etc.
        return statements
    
    def _should_include_dependency(self, commands: List[str], service: str, dep_type: str) -> bool:
        """Determine if a dependency should be included based on command analysis."""
        # Placeholder logic - in reality, this would analyze the specific commands
        # and parameters to determine if certain dependencies are needed
        
        command_text = ' '.join(commands).lower()
        
        # Example heuristics
        if service == 'lambda' and dep_type == 'vpc_config':
            return 'vpc-config' in command_text or 'subnet' in command_text
        
        if service == 'ecs' and dep_type == 'ecr_access':
            return 'image' in command_text or 'repository' in command_text
        
        if service == 'lambda' and dep_type == 'cloudwatch_logs':
            return True  # Lambda always needs CloudWatch Logs
        
        return len(commands) > 1  # Include dependencies for multi-command scenarios
    
    def _create_enhanced_policy(self, permissions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create an enhanced policy from permissions list."""
        return {
            'Version': '2012-10-17',
            'Statement': permissions
        }
    
    def _create_dependency_graph(self, services: Set[str], dependencies: Dict[str, List[str]]) -> Dict[str, Any]:
        """Create a dependency graph for visualization."""
        nodes = []
        edges = []
        
        # Add service nodes
        for service in services:
            nodes.append({
                'id': service,
                'label': service.upper(),
                'type': 'service'
            })
        
        # Add dependency edges
        for service, deps in dependencies.items():
            for dep in deps:
                edges.append({
                    'from': service,
                    'to': dep,
                    'type': 'dependency'
                })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def _determine_applicable_conditions(self, action: str, conditions: Dict[str, Any]) -> Dict[str, Any]:
        """Determine which conditions should apply to a specific action."""
        applicable = {}
        
        # Check if action is sensitive and should require MFA
        if conditions.get('require_mfa') and self._is_sensitive_action(action):
            applicable.update(self.security_conditions['mfa_required'])
        
        # Apply IP restrictions if specified
        if conditions.get('ip_restrictions'):
            ip_condition = self.security_conditions['ip_restriction'].copy()
            ip_condition['IpAddress']['aws:SourceIp'] = conditions['ip_restrictions']
            applicable.update(ip_condition)
        
        # Apply time restrictions if specified
        if conditions.get('time_restrictions'):
            time_restr = conditions['time_restrictions']
            time_condition = self.security_conditions['time_restriction'].copy()
            
            # Convert time format if needed
            start_time = f"{time_restr.get('start_time', '00:00')}:00Z"
            end_time = f"{time_restr.get('end_time', '23:59')}:59Z"
            
            time_condition['DateGreaterThan']['aws:CurrentTime'] = start_time
            time_condition['DateLessThan']['aws:CurrentTime'] = end_time
            applicable.update(time_condition)
        
        # Apply VPC restrictions if specified
        if conditions.get('vpc_restrictions'):
            vpc_condition = self.security_conditions['vpc_endpoint'].copy()
            vpc_condition['StringEquals']['aws:SourceVpc'] = conditions['vpc_restrictions']
            applicable.update(vpc_condition)
        
        # Always require secure transport for data operations
        if any(data_action in action.lower() for data_action in ['put', 'upload', 'create', 'delete']):
            applicable.update(self.security_conditions['secure_transport'])
        
        return applicable
    
    def _is_sensitive_action(self, action: str) -> bool:
        """Check if an action is considered sensitive."""
        sensitive_patterns = [
            'delete', 'terminate', 'destroy', 'remove',
            'iam:', 'create-role', 'create-user', 'create-policy',
            'put-bucket-policy', 'put-user-policy', 'put-role-policy'
        ]
        
        return any(pattern in action.lower() for pattern in sensitive_patterns)
    
    def _can_use_wildcard(self, actions: List[str]) -> bool:
        """Determine if actions can be optimized with a wildcard."""
        # Simple heuristic - if we have many read actions, use wildcard
        read_actions = [action for action in actions if any(read_prefix in action.lower() 
                       for read_prefix in ['get', 'list', 'describe', 'head'])]
        
        return len(read_actions) >= len(actions) * 0.7  # 70% are read actions
