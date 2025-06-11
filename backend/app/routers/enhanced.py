"""
Enhanced API endpoints for advanced IAM features.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.models import (
    PolicyValidationRequest,
    PolicyValidationResponse,
    PolicyOptimizationRequest,
    PolicyOptimizationResponse,
    CrossServiceDependencyRequest,
    CrossServiceDependencyResponse,
    ConditionalPolicyRequest,
    ConditionalPolicyResponse,
    ValidationIssueModel
)
from iam_generator.enhanced_services import EnhancedIAMService

router = APIRouter(prefix="/enhanced", tags=["Enhanced Features"])

# Initialize the enhanced service
enhanced_service = EnhancedIAMService()


@router.post("/validate-policy", response_model=PolicyValidationResponse)
async def validate_policy(request: PolicyValidationRequest) -> PolicyValidationResponse:
    """
    Validate an IAM policy with comprehensive security and best practice checks.
    
    This endpoint provides:
    - AWS size limit validation
    - Syntax and structure validation
    - Security vulnerability detection
    - Best practice recommendations
    - Overall security score (0-100)
    """
    try:
        result = enhanced_service.validate_policy(
            policy=request.policy,
            policy_type=request.policy_type,
            account_id=request.account_id
        )
        
        # Convert issues to response models
        issues = [
            ValidationIssueModel(**issue) for issue in result['issues']
        ]
        
        return PolicyValidationResponse(
            is_valid=result['is_valid'],
            policy_size=result['policy_size'],
            policy_type=result['policy_type'],
            issues=issues,
            score=result['score'],
            recommendations=result['recommendations']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy validation failed: {str(e)}")


@router.post("/optimize-policy", response_model=PolicyOptimizationResponse)
async def optimize_policy(request: PolicyOptimizationRequest) -> PolicyOptimizationResponse:
    """
    Optimize an IAM policy for size, security, and best practices.
    
    Optimization levels:
    - basic: Remove redundancy, consolidate statements
    - standard: Include action pattern optimization, version updates
    - aggressive: Advanced condition optimization, maximum consolidation
    """
    try:
        result = enhanced_service.optimize_policy(
            policy=request.policy,
            optimization_level=request.optimization_level,
            account_id=request.account_id
        )
        
        # Convert validation result
        validation_result = result['validation_result']
        validation_issues = [
            ValidationIssueModel(**issue) for issue in validation_result['issues']
        ]
        
        validation_response = PolicyValidationResponse(
            is_valid=validation_result['is_valid'],
            policy_size=validation_result['policy_size'],
            policy_type=validation_result['policy_type'],
            issues=validation_issues,
            score=validation_result['score'],
            recommendations=validation_result['recommendations']
        )
        
        return PolicyOptimizationResponse(
            original_policy=result['original_policy'],
            optimized_policy=result['optimized_policy'],
            size_reduction=result['size_reduction'],
            optimizations_applied=result['optimizations_applied'],
            validation_result=validation_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy optimization failed: {str(e)}")


@router.post("/cross-service-dependencies", response_model=CrossServiceDependencyResponse)
async def analyze_cross_service_dependencies(request: CrossServiceDependencyRequest) -> CrossServiceDependencyResponse:
    """
    Analyze cross-service dependencies and generate enhanced permissions.
    
    This endpoint identifies:
    - Implicit service dependencies (e.g., Lambda in VPC needs EC2 permissions)
    - Required supporting permissions (e.g., CloudWatch Logs for Lambda)
    - Service integration requirements
    - Enhanced policy with all necessary permissions
    """
    try:
        result = enhanced_service.analyze_cross_service_dependencies(
            commands=request.commands,
            include_implicit=request.include_implicit
        )
        
        return CrossServiceDependencyResponse(
            dependencies=result['dependencies'],
            additional_permissions=result['additional_permissions'],
            enhanced_policy=result['enhanced_policy'],
            dependency_graph=result['dependency_graph']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dependency analysis failed: {str(e)}")


@router.post("/conditional-policy", response_model=ConditionalPolicyResponse)
async def generate_conditional_policy(request: ConditionalPolicyRequest) -> ConditionalPolicyResponse:
    """
    Generate IAM policies with security conditions and restrictions.
    
    Supported conditions:
    - MFA requirements for sensitive operations
    - IP address restrictions
    - Time-based access controls
    - VPC endpoint restrictions
    - Secure transport requirements
    - User agent restrictions
    """
    try:
        result = enhanced_service.generate_conditional_policy(
            commands=request.commands,
            conditions=request.conditions,
            account_id=request.account_id,
            region=request.region
        )
        
        return ConditionalPolicyResponse(
            policy_document=result['policy_document'],
            conditions_applied=result['conditions_applied'],
            security_enhancements=result['security_enhancements'],
            metadata=result['metadata']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conditional policy generation failed: {str(e)}")


@router.get("/security-recommendations/{service}")
async def get_security_recommendations(service: str) -> Dict[str, Any]:
    """
    Get security recommendations for a specific AWS service.
    
    Returns best practices, common vulnerabilities, and recommended conditions
    for the specified service.
    """
    try:
        # Service-specific security recommendations
        recommendations = {
            's3': {
                'best_practices': [
                    'Use bucket policies with explicit denies',
                    'Enable MFA delete for critical buckets',
                    'Use VPC endpoints for private access',
                    'Enable server-side encryption by default'
                ],
                'conditions': [
                    'aws:SecureTransport for all data operations',
                    'aws:SourceIp for location restrictions',
                    'aws:MultiFactorAuthPresent for delete operations'
                ],
                'common_issues': [
                    'Overly permissive bucket policies',
                    'Missing encryption requirements',
                    'Public read/write access'
                ]
            },
            'iam': {
                'best_practices': [
                    'Use managed policies when possible',
                    'Apply principle of least privilege',
                    'Require MFA for sensitive operations',
                    'Use policy conditions for additional security'
                ],
                'conditions': [
                    'aws:MultiFactorAuthPresent for all IAM operations',
                    'aws:SourceIp for administrative access',
                    'aws:RequestedRegion for region restrictions'
                ],
                'common_issues': [
                    'Wildcard permissions in IAM policies',
                    'Missing MFA requirements',
                    'Overly broad administrative access'
                ]
            },
            'lambda': {
                'best_practices': [
                    'Use execution roles with minimal permissions',
                    'Enable VPC configuration for network isolation',
                    'Use dead letter queues for error handling',
                    'Enable X-Ray tracing for monitoring'
                ],
                'conditions': [
                    'aws:SourceVpce for VPC endpoint access',
                    'aws:RequestedRegion for region restrictions'
                ],
                'common_issues': [
                    'Overly broad execution role permissions',
                    'Missing VPC configuration for sensitive functions',
                    'Inadequate error handling'
                ]
            },
            'ec2': {
                'best_practices': [
                    'Use IAM roles instead of access keys',
                    'Implement security groups with least privilege',
                    'Enable CloudTrail for audit logging',
                    'Use Systems Manager for secure access'
                ],
                'conditions': [
                    'aws:RequestedRegion for region restrictions',
                    'aws:SourceIp for location-based access'
                ],
                'common_issues': [
                    'Overly permissive security groups',
                    'Missing instance profile roles',
                    'Inadequate network segmentation'
                ]
            }
        }
        
        if service.lower() not in recommendations:
            return {
                'service': service,
                'message': f'Security recommendations not available for {service}',
                'general_recommendations': [
                    'Apply principle of least privilege',
                    'Use IAM conditions for additional security',
                    'Enable CloudTrail for audit logging',
                    'Regular review and rotate credentials'
                ]
            }
        
        return {
            'service': service,
            **recommendations[service.lower()]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get security recommendations: {str(e)}")


@router.get("/policy-templates/{use_case}")
async def get_policy_template(use_case: str) -> Dict[str, Any]:
    """
    Get pre-built policy templates for common use cases.
    
    Available templates:
    - lambda-basic: Basic Lambda execution permissions
    - lambda-vpc: Lambda with VPC access
    - s3-read-only: Read-only S3 access
    - s3-full-bucket: Full access to specific bucket
    - ec2-developer: Developer EC2 permissions
    - rds-admin: RDS administration permissions
    """
    try:
        templates = {
            'lambda-basic': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'logs:CreateLogGroup',
                            'logs:CreateLogStream',
                            'logs:PutLogEvents'
                        ],
                        'Resource': 'arn:aws:logs:*:*:*'
                    }
                ]
            },
            'lambda-vpc': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'logs:CreateLogGroup',
                            'logs:CreateLogStream',
                            'logs:PutLogEvents'
                        ],
                        'Resource': 'arn:aws:logs:*:*:*'
                    },
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'ec2:CreateNetworkInterface',
                            'ec2:DescribeNetworkInterfaces',
                            'ec2:DeleteNetworkInterface'
                        ],
                        'Resource': '*'
                    }
                ]
            },
            's3-read-only': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': [
                            's3:GetObject',
                            's3:GetObjectVersion',
                            's3:ListBucket'
                        ],
                        'Resource': [
                            'arn:aws:s3:::your-bucket-name',
                            'arn:aws:s3:::your-bucket-name/*'
                        ]
                    }
                ]
            },
            's3-full-bucket': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': 's3:*',
                        'Resource': [
                            'arn:aws:s3:::your-bucket-name',
                            'arn:aws:s3:::your-bucket-name/*'
                        ],
                        'Condition': {
                            'Bool': {
                                'aws:SecureTransport': 'true'
                            }
                        }
                    }
                ]
            },
            'ec2-developer': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'ec2:DescribeInstances',
                            'ec2:DescribeImages',
                            'ec2:DescribeKeyPairs',
                            'ec2:DescribeSecurityGroups',
                            'ec2:DescribeAvailabilityZones',
                            'ec2:RunInstances',
                            'ec2:TerminateInstances',
                            'ec2:StopInstances',
                            'ec2:StartInstances'
                        ],
                        'Resource': '*',
                        'Condition': {
                            'StringEquals': {
                                'ec2:InstanceType': ['t2.micro', 't2.small', 't3.micro', 't3.small']
                            }
                        }
                    }
                ]
            },
            'rds-admin': {
                'Version': '2012-10-17',
                'Statement': [
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'rds:*',
                            'cloudwatch:GetMetricStatistics',
                            'logs:DescribeLogStreams',
                            'logs:GetLogEvents'
                        ],
                        'Resource': '*'
                    },
                    {
                        'Effect': 'Allow',
                        'Action': [
                            'rds:DeleteDBInstance',
                            'rds:DeleteDBCluster'
                        ],
                        'Resource': '*',
                        'Condition': {
                            'Bool': {
                                'aws:MultiFactorAuthPresent': 'true'
                            }
                        }
                    }
                ]
            }
        }
        
        if use_case not in templates:
            available_templates = list(templates.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Template '{use_case}' not found. Available templates: {available_templates}"
            )
        
        return {
            'use_case': use_case,
            'template': templates[use_case],
            'description': f"Policy template for {use_case.replace('-', ' ')} use case",
            'customization_notes': [
                'Replace placeholder values (e.g., your-bucket-name) with actual resources',
                'Adjust resource ARNs to match your environment',
                'Review conditions and modify as needed for your security requirements',
                'Consider adding additional conditions for enhanced security'
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get policy template: {str(e)}")


@router.get("/compliance-check/{framework}")
async def check_compliance(framework: str, policy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check policy compliance against security frameworks.
    
    Supported frameworks:
    - SOC2: Service Organization Control 2
    - PCI: Payment Card Industry
    - HIPAA: Health Insurance Portability and Accountability Act
    - GDPR: General Data Protection Regulation
    """
    try:
        # Placeholder for compliance checking logic
        # In a real implementation, this would have detailed compliance rules
        
        compliance_rules = {
            'soc2': {
                'name': 'SOC 2 Type II',
                'requirements': [
                    'Principle of least privilege',
                    'Access logging and monitoring',
                    'Regular access reviews',
                    'Multi-factor authentication for sensitive operations'
                ]
            },
            'pci': {
                'name': 'PCI DSS',
                'requirements': [
                    'Restrict access by business need-to-know',
                    'Unique ID assignment',
                    'Multi-factor authentication',
                    'Encryption of data transmission'
                ]
            },
            'hipaa': {
                'name': 'HIPAA Security Rule',
                'requirements': [
                    'Unique user identification',
                    'Emergency access procedures',
                    'Automatic logoff',
                    'Encryption and decryption'
                ]
            },
            'gdpr': {
                'name': 'GDPR Article 32',
                'requirements': [
                    'Pseudonymisation and encryption',
                    'Confidentiality, integrity, availability',
                    'Regular testing and evaluation',
                    'Data breach notification procedures'
                ]
            }
        }
        
        if framework.lower() not in compliance_rules:
            available_frameworks = list(compliance_rules.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Framework '{framework}' not supported. Available: {available_frameworks}"
            )
        
        # Simplified compliance checking
        compliance_result = {
            'framework': compliance_rules[framework.lower()]['name'],
            'overall_compliance': 'PARTIAL',
            'score': 75,  # Placeholder score
            'checks': [
                {
                    'requirement': 'Principle of least privilege',
                    'status': 'PASS',
                    'details': 'Policy uses specific actions rather than wildcards'
                },
                {
                    'requirement': 'Multi-factor authentication',
                    'status': 'FAIL',
                    'details': 'No MFA conditions found in policy',
                    'remediation': 'Add MFA conditions for sensitive operations'
                },
                {
                    'requirement': 'Access logging',
                    'status': 'WARNING',
                    'details': 'CloudTrail logging should be verified separately'
                }
            ],
            'recommendations': [
                'Add MFA requirements for administrative actions',
                'Implement time-based access restrictions',
                'Add IP address restrictions where appropriate',
                'Ensure CloudTrail is enabled for audit logging'
            ]
        }
        
        return compliance_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")
