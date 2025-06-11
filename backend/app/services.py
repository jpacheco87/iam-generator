"""
Business logic services for the IAM Generator API.
"""

import json
import subprocess
from typing import List, Dict, Any, Optional

from iam_generator.analyzer import IAMPermissionAnalyzer
from iam_generator.role_generator import IAMRoleGenerator
from iam_generator.parser import AWSCLIParser


class IAMGeneratorService:
    """Service class that encapsulates the core IAM generation logic."""
    
    def __init__(self):
        """Initialize the service with core components."""
        self.analyzer = IAMPermissionAnalyzer()
        self.role_generator = IAMRoleGenerator()
        self.parser = AWSCLIParser()
    
    def analyze_command(self, command: str, debug: bool = False) -> Dict[str, Any]:
        """
        Analyze a single AWS CLI command and return required permissions.
        
        Args:
            command: The AWS CLI command to analyze
            debug: Whether to include debug information
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Use the analyzer's analyze_command method directly
            result = self.analyzer.analyze_command(command)
            
            return {
                'service': result['service'],
                'action': result['action'],
                'original_command': command,
                'required_permissions': result['required_permissions'],
                'policy_document': result['policy_document'],
                'resource_arns': result.get('resource_arns', []),
                'warnings': result.get('warnings', [])
            }
        except Exception as e:
            if debug:
                raise
            return {
                'service': 'unknown',
                'action': 'unknown',
                'original_command': command,
                'required_permissions': [],
                'policy_document': {},
                'resource_arns': [],
                'warnings': [str(e)]
            }
    
    def generate_role(self, 
                     command: str, 
                     role_name: str, 
                     trust_policy: Optional[str] = None,
                     output_format: str = "json",
                     account_id: Optional[str] = None,
                     description: Optional[str] = None,
                     debug: bool = False) -> Dict[str, Any]:
        """
        Generate an IAM role configuration for the given command.
        
        Args:
            command: The AWS CLI command to analyze
            role_name: Name for the IAM role
            trust_policy: Trust policy type or custom policy
            output_format: Output format (json, terraform, cloudformation)
            account_id: AWS account ID for ARN generation
            description: Role description
            debug: Whether to include debug information
            
        Returns:
            Dictionary containing role configuration
        """
        try:
            # First analyze the command
            analysis = self.analyze_command(command, debug)
            
            # Generate role configuration using the role generator's expected interface
            result = self.role_generator.generate_role(
                analysis_result=analysis,
                role_name=role_name,
                trust_policy_type=trust_policy or "default",
                output_format=output_format,
                description=description,
                account_id=account_id
            )
            
            # Extract the result for the requested format
            if output_format == "terraform":
                return {
                    'role_name': role_name,
                    'trust_policy': result['json']['trust_policy'],
                    'permissions_policy': result['json']['permissions_policy'],
                    'terraform_config': result['terraform']
                }
            elif output_format == "cloudformation":
                return {
                    'role_name': role_name,
                    'trust_policy': result['json']['trust_policy'],
                    'permissions_policy': result['json']['permissions_policy'],
                    'cloudformation_config': json.dumps(result['cloudformation'], indent=2)
                }
            elif output_format == "aws_cli":
                return {
                    'role_name': role_name,
                    'trust_policy': result['json']['trust_policy'],
                    'permissions_policy': result['json']['permissions_policy'],
                    'aws_cli_commands': result['aws_cli']
                }
            else:
                # Default JSON format
                return result['json']
        except Exception as e:
            if debug:
                raise
            return {
                'role_name': role_name,
                'trust_policy': {},
                'permissions_policy': {},
                'error': str(e)
            }
    
    def batch_analyze(self, commands: List[str], debug: bool = False) -> Dict[str, Any]:
        """
        Analyze multiple commands and return combined results.
        
        Args:
            commands: List of AWS CLI commands to analyze
            debug: Whether to include debug information
            
        Returns:
            Dictionary containing batch analysis results
        """
        results = []
        all_permissions = []
        
        for command in commands:
            result = self.analyze_command(command, debug)
            results.append(result)
            all_permissions.extend(result['required_permissions'])
        
        # Use the analyzer's analyze_commands method for better integration
        analysis_result = self.analyzer.analyze_commands(commands)
        
        # Generate summary
        summary = self._generate_batch_summary(results)
        
        return {
            'results': results,
            'summary': summary,
            'combined_policy': analysis_result.policy_document
        }
    
    def get_supported_services(self) -> List[str]:
        """
        Get list of supported AWS services.
        
        Returns:
            List of supported service names
        """
        return self.analyzer.permissions_db.get_supported_services()
    
    def _extract_resource_arns(self, permissions: List[Dict[str, Any]]) -> List[str]:
        """Extract unique resource ARNs from permissions."""
        arns = set()
        for perm in permissions:
            if 'resource' in perm and perm['resource'] != '*':
                arns.add(perm['resource'])
        return list(arns)
    
    def _generate_batch_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for batch analysis."""
        services = set()
        actions = set()
        total_permissions = 0
        
        for result in results:
            services.add(result['service'])
            actions.add(f"{result['service']}:{result['action']}")
            total_permissions += len(result['required_permissions'])
        
        return {
            'total_commands': len(results),
            'unique_services': len(services),
            'unique_actions': len(actions),
            'total_permissions': total_permissions,
            'services_used': list(services)
        }
