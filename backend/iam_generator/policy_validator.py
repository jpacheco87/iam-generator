"""
AWS IAM Policy Validator

This module provides comprehensive validation for AWS IAM policies including:
- Policy size limits validation
- Syntax and structure validation
- Security best practices checking
- Common vulnerability detection
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class PolicyType(Enum):
    """AWS IAM Policy types with their size limits."""
    MANAGED = "managed"
    INLINE_USER = "inline_user"
    INLINE_ROLE = "inline_role"
    INLINE_GROUP = "inline_group"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a policy."""
    severity: ValidationSeverity
    category: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    code: Optional[str] = None


@dataclass
class PolicyValidationResult:
    """Results of policy validation."""
    is_valid: bool
    policy_size: int
    policy_type: PolicyType
    issues: List[ValidationIssue]
    score: int  # 0-100, higher is better
    recommendations: List[str]


class IAMPolicyValidator:
    """
    Comprehensive AWS IAM Policy validator.
    
    Validates policies against AWS limits, best practices, and security guidelines.
    """
    
    # AWS Policy Size Limits (in characters)
    SIZE_LIMITS = {
        PolicyType.MANAGED: 6144,
        PolicyType.INLINE_USER: 2048,
        PolicyType.INLINE_ROLE: 10240,
        PolicyType.INLINE_GROUP: 10240
    }
    
    # Maximum statements per policy
    MAX_STATEMENTS = 12
    
    # Sensitive actions that should require conditions
    SENSITIVE_ACTIONS = {
        "iam:*",
        "iam:CreateRole",
        "iam:CreateUser",
        "iam:CreatePolicy",
        "iam:AttachUserPolicy",
        "iam:AttachRolePolicy",
        "iam:AttachGroupPolicy",
        "iam:PutUserPolicy",
        "iam:PutRolePolicy",
        "iam:PutGroupPolicy",
        "s3:DeleteBucket",
        "s3:PutBucketPolicy",
        "ec2:TerminateInstances",
        "rds:DeleteDBInstance",
        "rds:DeleteDBCluster",
        "lambda:DeleteFunction",
        "cloudformation:DeleteStack",
    }
    
    # Actions that should require MFA
    MFA_REQUIRED_ACTIONS = {
        "iam:DeleteUser",
        "iam:DeleteRole",
        "iam:DeletePolicy",
        "s3:DeleteBucket",
        "ec2:TerminateInstances",
        "rds:DeleteDBInstance",
        "rds:DeleteDBCluster",
    }
    
    def __init__(self):
        """Initialize the policy validator."""
        pass
    
    def validate_policy(
        self,
        policy: Dict[str, Any],
        policy_type: PolicyType = PolicyType.MANAGED,
        account_id: Optional[str] = None
    ) -> PolicyValidationResult:
        """
        Validate an IAM policy comprehensively.
        
        Args:
            policy: The IAM policy document as a dictionary
            policy_type: Type of policy (managed, inline_user, etc.)
            account_id: AWS account ID for ARN validation
            
        Returns:
            PolicyValidationResult with all validation findings
        """
        issues = []
        recommendations = []
        
        # Convert policy to JSON string for size calculation
        policy_json = json.dumps(policy, separators=(',', ':'))
        policy_size = len(policy_json)
        
        # 1. Size validation
        issues.extend(self._validate_size(policy_size, policy_type))
        
        # 2. Structure validation
        structure_issues, structure_valid = self._validate_structure(policy)
        issues.extend(structure_issues)
        
        # 3. Statement validation
        if structure_valid and 'Statement' in policy:
            issues.extend(self._validate_statements(policy['Statement']))
        
        # 4. Security validation
        if structure_valid:
            security_issues, security_recommendations = self._validate_security(policy)
            issues.extend(security_issues)
            recommendations.extend(security_recommendations)
        
        # 5. Best practices validation
        if structure_valid:
            bp_issues, bp_recommendations = self._validate_best_practices(policy, account_id)
            issues.extend(bp_issues)
            recommendations.extend(bp_recommendations)
        
        # Calculate overall score
        score = self._calculate_score(issues)
        
        # Determine if policy is valid (no ERROR or CRITICAL issues)
        is_valid = not any(issue.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL] 
                          for issue in issues)
        
        return PolicyValidationResult(
            is_valid=is_valid,
            policy_size=policy_size,
            policy_type=policy_type,
            issues=issues,
            score=score,
            recommendations=recommendations
        )
    
    def _validate_size(self, policy_size: int, policy_type: PolicyType) -> List[ValidationIssue]:
        """Validate policy size against AWS limits."""
        issues = []
        limit = self.SIZE_LIMITS[policy_type]
        
        if policy_size > limit:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="size",
                message=f"Policy size ({policy_size} characters) exceeds AWS limit for {policy_type.value} policies ({limit} characters)",
                suggestion=f"Reduce policy size by {policy_size - limit} characters or split into multiple policies"
            ))
        elif policy_size > limit * 0.8:  # Warning at 80% of limit
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="size",
                message=f"Policy size ({policy_size} characters) is approaching AWS limit ({limit} characters)",
                suggestion="Consider optimizing the policy or splitting it into multiple policies"
            ))
        
        return issues
    
    def _validate_structure(self, policy: Dict[str, Any]) -> Tuple[List[ValidationIssue], bool]:
        """Validate basic policy structure."""
        issues = []
        is_valid = True
        
        # Check required fields
        if 'Version' not in policy:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="structure",
                message="Policy missing 'Version' field",
                suggestion="Add 'Version': '2012-10-17' to use the latest policy language"
            ))
        elif policy['Version'] != '2012-10-17':
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category="structure",
                message=f"Policy uses outdated version '{policy['Version']}'",
                suggestion="Update to '2012-10-17' for latest policy language features"
            ))
        
        if 'Statement' not in policy:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="structure",
                message="Policy missing required 'Statement' field",
                suggestion="Add a 'Statement' field with policy statements"
            ))
            is_valid = False
        elif not isinstance(policy['Statement'], (list, dict)):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="structure",
                message="'Statement' field must be a list or object",
                suggestion="Ensure 'Statement' contains valid policy statements"
            ))
            is_valid = False
        
        return issues, is_valid
    
    def _validate_statements(self, statements: List[Dict[str, Any]]) -> List[ValidationIssue]:
        """Validate individual policy statements."""
        issues = []
        
        # Ensure statements is a list
        if isinstance(statements, dict):
            statements = [statements]
        
        if len(statements) > self.MAX_STATEMENTS:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category="statements",
                message=f"Policy has {len(statements)} statements, exceeding AWS limit of {self.MAX_STATEMENTS}",
                suggestion="Consolidate or split statements across multiple policies"
            ))
        
        for i, statement in enumerate(statements):
            statement_location = f"Statement[{i}]"
            
            # Check required fields
            if 'Effect' not in statement:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="statements",
                    message="Statement missing required 'Effect' field",
                    location=statement_location,
                    suggestion="Add 'Effect': 'Allow' or 'Effect': 'Deny'"
                ))
            elif statement['Effect'] not in ['Allow', 'Deny']:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="statements",
                    message=f"Invalid Effect value: '{statement['Effect']}'",
                    location=statement_location,
                    suggestion="Effect must be 'Allow' or 'Deny'"
                ))
            
            # Check Action or NotAction
            has_action = 'Action' in statement
            has_notaction = 'NotAction' in statement
            
            if not has_action and not has_notaction:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="statements",
                    message="Statement missing 'Action' or 'NotAction' field",
                    location=statement_location,
                    suggestion="Add an 'Action' field specifying the allowed/denied actions"
                ))
            elif has_action and has_notaction:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="statements",
                    message="Statement cannot have both 'Action' and 'NotAction'",
                    location=statement_location,
                    suggestion="Use either 'Action' or 'NotAction', not both"
                ))
            
            # Validate actions
            if has_action:
                actions = statement['Action']
                if isinstance(actions, str):
                    actions = [actions]
                issues.extend(self._validate_actions(actions, statement_location))
            
            # Check Resource or NotResource
            has_resource = 'Resource' in statement
            has_notresource = 'NotResource' in statement
            
            if has_resource and has_notresource:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="statements",
                    message="Statement cannot have both 'Resource' and 'NotResource'",
                    location=statement_location,
                    suggestion="Use either 'Resource' or 'NotResource', not both"
                ))
        
        return issues
    
    def _validate_actions(self, actions: List[str], location: str) -> List[ValidationIssue]:
        """Validate action formats and patterns."""
        issues = []
        
        for action in actions:
            # Check for valid action format (service:action)
            if ':' not in action and action != '*':
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="actions",
                    message=f"Action '{action}' doesn't follow service:action format",
                    location=location,
                    suggestion="Use format 'service:action' (e.g., 's3:GetObject')"
                ))
            
            # Check for overly broad actions
            if action == '*':
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="security",
                    message="Wildcard action '*' grants all permissions",
                    location=location,
                    suggestion="Specify only the required actions instead of using '*'"
                ))
            elif action.endswith(':*'):
                service = action.split(':')[0]
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="security",
                    message=f"Wildcard action '{action}' grants all {service} permissions",
                    location=location,
                    suggestion=f"Specify only the required {service} actions"
                ))
        
        return issues
    
    def _validate_security(self, policy: Dict[str, Any]) -> Tuple[List[ValidationIssue], List[str]]:
        """Validate security-related aspects of the policy."""
        issues = []
        recommendations = []
        
        statements = policy.get('Statement', [])
        if isinstance(statements, dict):
            statements = [statements]
        
        for i, statement in enumerate(statements):
            statement_location = f"Statement[{i}]"
            
            if statement.get('Effect') == 'Allow':
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                
                resources = statement.get('Resource', [])
                if isinstance(resources, str):
                    resources = [resources]
                
                # Check for sensitive actions without conditions
                sensitive_actions_found = []
                for action in actions:
                    if any(action.startswith(sensitive.replace('*', '')) or action == sensitive 
                          for sensitive in self.SENSITIVE_ACTIONS):
                        sensitive_actions_found.append(action)
                
                if sensitive_actions_found and 'Condition' not in statement:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="security",
                        message=f"Sensitive actions without conditions: {', '.join(sensitive_actions_found)}",
                        location=statement_location,
                        suggestion="Add conditions to restrict when these sensitive actions can be performed"
                    ))
                
                # Check for actions requiring MFA
                mfa_actions_found = []
                for action in actions:
                    if action in self.MFA_REQUIRED_ACTIONS:
                        mfa_actions_found.append(action)
                
                if mfa_actions_found:
                    has_mfa_condition = False
                    if 'Condition' in statement:
                        conditions = statement['Condition']
                        has_mfa_condition = any(
                            'aws:MultiFactorAuthPresent' in condition_block or
                            'aws:MultiFactorAuthAge' in condition_block
                            for condition_type, condition_block in conditions.items()
                            if isinstance(condition_block, dict)
                        )
                    
                    if not has_mfa_condition:
                        issues.append(ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category="security",
                            message=f"Destructive actions should require MFA: {', '.join(mfa_actions_found)}",
                            location=statement_location,
                            suggestion="Add MFA condition: {'Bool': {'aws:MultiFactorAuthPresent': 'true'}}"
                        ))
                
                # Check for wildcard resources with powerful actions
                if '*' in resources and any(not action.endswith(':List*') and not action.endswith(':Get*') 
                                          for action in actions):
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="security",
                        message="Wildcard resource '*' with write/delete actions",
                        location=statement_location,
                        suggestion="Specify specific resource ARNs instead of using '*'"
                    ))
        
        return issues, recommendations
    
    def _validate_best_practices(self, policy: Dict[str, Any], account_id: Optional[str]) -> Tuple[List[ValidationIssue], List[str]]:
        """Validate against AWS IAM best practices."""
        issues = []
        recommendations = []
        
        statements = policy.get('Statement', [])
        if isinstance(statements, dict):
            statements = [statements]
        
        # Check for policy optimization opportunities
        all_actions = []
        all_resources = []
        
        for statement in statements:
            if statement.get('Effect') == 'Allow':
                actions = statement.get('Action', [])
                if isinstance(actions, str):
                    actions = [actions]
                all_actions.extend(actions)
                
                resources = statement.get('Resource', [])
                if isinstance(resources, str):
                    resources = [resources]
                all_resources.extend(resources)
        
        # Check for duplicate actions
        if len(all_actions) != len(set(all_actions)):
            recommendations.append("Consider consolidating duplicate actions into fewer statements")
        
        # Check for resource specificity
        wildcard_resources = [r for r in all_resources if '*' in r]
        if wildcard_resources:
            recommendations.append("Consider using specific resource ARNs instead of wildcards where possible")
        
        # Check for account ID in ARNs if provided
        if account_id:
            for resource in all_resources:
                if resource.startswith('arn:aws:') and account_id not in resource and '*' not in resource:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category="best_practices",
                        message=f"Resource ARN doesn't contain expected account ID: {resource}",
                        suggestion=f"Verify the account ID in ARN is correct for account {account_id}"
                    ))
        
        return issues, recommendations
    
    def _calculate_score(self, issues: List[ValidationIssue]) -> int:
        """Calculate a security/quality score for the policy (0-100)."""
        score = 100
        
        for issue in issues:
            if issue.severity == ValidationSeverity.CRITICAL:
                score -= 25
            elif issue.severity == ValidationSeverity.ERROR:
                score -= 15
            elif issue.severity == ValidationSeverity.WARNING:
                score -= 10
            elif issue.severity == ValidationSeverity.INFO:
                score -= 5
        
        return max(0, score)
    
    def validate_policy_json(self, policy_json: str, **kwargs) -> PolicyValidationResult:
        """
        Validate a policy from JSON string.
        
        Args:
            policy_json: JSON string containing the policy
            **kwargs: Additional arguments passed to validate_policy
            
        Returns:
            PolicyValidationResult
        """
        try:
            policy = json.loads(policy_json)
            return self.validate_policy(policy, **kwargs)
        except json.JSONDecodeError as e:
            return PolicyValidationResult(
                is_valid=False,
                policy_size=len(policy_json),
                policy_type=kwargs.get('policy_type', PolicyType.MANAGED),
                issues=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="json",
                    message=f"Invalid JSON: {str(e)}",
                    suggestion="Fix JSON syntax errors"
                )],
                score=0,
                recommendations=["Fix JSON syntax before validation"]
            )
    
    def get_policy_recommendations(self, policy: Dict[str, Any]) -> List[str]:
        """
        Get optimization recommendations for a policy.
        
        Args:
            policy: The IAM policy document
            
        Returns:
            List of optimization recommendations
        """
        validation_result = self.validate_policy(policy)
        recommendations = validation_result.recommendations.copy()
        
        # Add general recommendations based on policy content
        statements = policy.get('Statement', [])
        if isinstance(statements, dict):
            statements = [statements]
        
        if len(statements) > 5:
            recommendations.append("Consider splitting large policies into smaller, more focused policies")
        
        # Check for version optimization
        if policy.get('Version') != '2012-10-17':
            recommendations.append("Update policy version to '2012-10-17' for latest features")
        
        return recommendations
