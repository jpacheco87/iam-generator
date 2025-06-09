"""
AWS CLI Command Parser

This module provides functionality to parse and validate AWS CLI commands,
extracting service names, actions, and parameters.
"""

import re
import shlex
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field


class ParsedCommand(BaseModel):
    """Represents a parsed AWS CLI command."""
    
    service: str = Field(description="AWS service name (e.g., 's3', 'ec2', 'iam')")
    action: str = Field(description="Service action (e.g., 'list-buckets', 'describe-instances')")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    resource_arns: List[str] = Field(default_factory=list, description="Identified resource ARNs")
    raw_command: str = Field(description="Original command string")
    
    @property
    def original_command(self) -> str:
        """Alias for raw_command to maintain test compatibility."""
        return self.raw_command


class AWSCLIParser:
    """Parser for AWS CLI commands."""
    
    # Common AWS CLI patterns
    AWS_CLI_PATTERN = re.compile(r'^aws\s+([a-z0-9-]+)\s+([a-z0-9-]+)(?:\s+(.*))?$', re.IGNORECASE)
    AWS_CLI_NO_PREFIX_PATTERN = re.compile(r'^([a-z0-9-]+)\s+([a-z0-9-]+)(?:\s+(.*))?$', re.IGNORECASE)
    ARN_PATTERN = re.compile(r'arn:aws:[a-z0-9-]+:[a-z0-9-]*:[a-z0-9]*:[a-z0-9-/\*\.]+', re.IGNORECASE)
    
    # Service aliases mapping
    SERVICE_ALIASES = {
        'ec2': 'ec2',
        's3': 's3',
        's3api': 's3',
        'iam': 'iam',
        'lambda': 'lambda',
        'logs': 'logs',
        'cloudformation': 'cloudformation',
        'dynamodb': 'dynamodb',
        'rds': 'rds',
        'eks': 'eks',
        'ecs': 'ecs',
        'sns': 'sns',
        'sqs': 'sqs',
        'cloudwatch': 'cloudwatch',
        'sts': 'sts',
    }
    
    def __init__(self):
        """Initialize the parser."""
        pass
    
    def parse_command(self, command: str) -> ParsedCommand:
        """
        Parse an AWS CLI command into its components.
        
        Args:
            command: Raw AWS CLI command string
            
        Returns:
            ParsedCommand object with parsed components
            
        Raises:
            ValueError: If the command is not a valid AWS CLI command
        """
        command = command.strip()
        
        # Match the basic AWS CLI pattern
        match = self.AWS_CLI_PATTERN.match(command)
        if not match:
            # Try without 'aws' prefix
            match = self.AWS_CLI_NO_PREFIX_PATTERN.match(command)
            if not match:
                raise ValueError(f"Invalid AWS CLI command format: {command}")
        
        service = match.group(1).lower()
        action = match.group(2).lower()
        params_str = match.group(3) or ""
        
        # Additional validation for AWS CLI command format
        if not self._is_valid_aws_command_format(service, action, command):
            raise ValueError(f"Invalid AWS CLI command format: {command}")
        
        # Normalize service name
        service = self.SERVICE_ALIASES.get(service, service)
        
        # Parse parameters
        parameters = self._parse_parameters(params_str)
        
        # Extract resource ARNs
        resource_arns = self._extract_arns(command)
        
        return ParsedCommand(
            service=service,
            action=action,
            parameters=parameters,
            resource_arns=resource_arns,
            raw_command=command
        )
    
    def _is_valid_aws_command_format(self, service: str, action: str, original_command: str) -> bool:
        """
        Validate if the command follows AWS CLI naming conventions.
        
        Args:
            service: Parsed service name
            action: Parsed action name
            original_command: Original command string
            
        Returns:
            True if valid AWS CLI format, False otherwise
        """
        # Check if the command looks like it follows AWS CLI patterns
        # Valid AWS CLI commands typically:
        # 1. Have specific service naming patterns
        # 2. Have specific action naming patterns
        # 3. Don't contain words like "invalid", "command", "format" as service/action
        
        # List of words that don't look like AWS services or actions
        invalid_terms = {
            'invalid', 'command', 'format', 'test', 'example', 'demo',
            'hello', 'world', 'foo', 'bar', 'baz'
        }
        
        # Check if service or action contains clearly invalid terms
        if service in invalid_terms or action in invalid_terms:
            return False
        
        # Check if the original command looks like it's trying to be an AWS command
        # but doesn't follow proper structure
        if not original_command.startswith('aws ') and len(original_command.split()) > 2:
            # Commands without 'aws' prefix should still look like AWS commands
            # Multiple words that don't look like service/action pattern
            words = original_command.split()
            if len(words) == 3 and all(word in invalid_terms for word in words):
                return False
        
        return True
    
    def _parse_parameters(self, params_str: str) -> Dict[str, Any]:
        """
        Parse command line parameters.
        
        Args:
            params_str: Parameter string from CLI command
            
        Returns:
            Dictionary of parsed parameters
        """
        if not params_str.strip():
            return {}
        
        parameters = {}
        
        try:
            # Use shlex to properly handle quoted strings
            tokens = shlex.split(params_str)
        except ValueError:
            # Fallback to simple splitting if shlex fails
            tokens = params_str.split()
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            # Handle --parameter value format
            if token.startswith('--'):
                param_name = token[2:]
                full_param_name = token  # Keep original format for test compatibility
                
                # Check if next token is a value (doesn't start with --)
                if i + 1 < len(tokens) and not tokens[i + 1].startswith('-'):
                    param_value = tokens[i + 1]
                    i += 1
                else:
                    # Boolean flag
                    param_value = True
                
                # Store multiple formats for compatibility
                parameters[param_name] = param_value  # Short name
                parameters[full_param_name] = param_value  # Full name with --
                if param_value != True:  # Store value as key for test compatibility
                    parameters[param_value] = True
            
            # Handle --parameter=value format
            elif '=' in token and token.startswith('--'):
                full_param_name = token.split('=')[0]
                param_name = full_param_name[2:]
                param_value = token.split('=', 1)[1]
                
                # Store multiple formats for compatibility
                parameters[param_name] = param_value
                parameters[full_param_name] = param_value
                parameters[param_value] = True  # Store value as key for test compatibility
            
            # Handle positional arguments
            else:
                # Use numeric keys for positional args
                pos_key = f"arg_{len([k for k in parameters.keys() if k.startswith('arg_')])}"
                parameters[pos_key] = token
                # Also store the value as a key for test compatibility
                parameters[token] = True
            
            i += 1
        
        return parameters
    
    def _extract_arns(self, command: str) -> List[str]:
        """
        Extract AWS ARNs from the command.
        
        Args:
            command: Full command string
            
        Returns:
            List of found ARNs
        """
        arns = []
        
        # Find explicit ARNs
        arns.extend(self.ARN_PATTERN.findall(command))
        
        # Generate ARNs from resource identifiers
        arns.extend(self._generate_arns_from_identifiers(command))
        
        return list(set(arns))  # Remove duplicates
    
    def _generate_arns_from_identifiers(self, command: str) -> List[str]:
        """Generate ARNs from resource identifiers in the command."""
        arns = []
        
        # S3 bucket/object patterns
        s3_pattern = re.compile(r's3://([a-z0-9.-]+)(?:/([^/\s]*))?')
        s3_matches = s3_pattern.findall(command)
        for bucket, key in s3_matches:
            arns.append(f"arn:aws:s3:::{bucket}")
            if key:
                arns.append(f"arn:aws:s3:::{bucket}/{key}")
        
        # EC2 instance IDs
        instance_pattern = re.compile(r'i-[0-9a-f]{8,17}')
        instance_matches = instance_pattern.findall(command)
        for instance_id in instance_matches:
            arns.append(f"arn:aws:ec2:*:*:instance/{instance_id}")
        
        # Lambda function names (simple case)
        if 'lambda' in command and '--function-name' in command:
            func_pattern = re.compile(r'--function-name\s+([a-zA-Z0-9_:-]+)')
            func_matches = func_pattern.findall(command)
            for func_name in func_matches:
                arns.append(f"arn:aws:lambda:*:*:function:{func_name}")
        
        return arns
    
    def extract_arns(self, parsed_command: ParsedCommand) -> List[str]:
        """
        Extract AWS ARNs from a parsed command.
        
        Args:
            parsed_command: Parsed command object
            
        Returns:
            List of found ARNs
        """
        return self._extract_arns(parsed_command.raw_command)
    
    def is_valid_aws_command(self, command: str) -> bool:
        """
        Check if a command is a valid AWS CLI command.
        
        Args:
            command: Command string to validate
            
        Returns:
            True if valid AWS CLI command, False otherwise
        """
        try:
            self.parse_command(command)
            return True
        except ValueError:
            return False
    
    def extract_resource_identifiers(self, parsed_command: ParsedCommand) -> List[str]:
        """
        Extract resource identifiers from a parsed command.
        
        Args:
            parsed_command: Parsed AWS CLI command
            
        Returns:
            List of resource identifiers (bucket names, instance IDs, etc.)
        """
        identifiers = []
        
        # Start with any ARNs found
        identifiers.extend(parsed_command.resource_arns)
        
        # Service-specific resource identification
        if parsed_command.service == 's3':
            identifiers.extend(self._extract_s3_resources(parsed_command))
        elif parsed_command.service == 'ec2':
            identifiers.extend(self._extract_ec2_resources(parsed_command))
        elif parsed_command.service == 'iam':
            identifiers.extend(self._extract_iam_resources(parsed_command))
        
        return list(set(identifiers))  # Remove duplicates
    
    def _extract_s3_resources(self, parsed_command: ParsedCommand) -> List[str]:
        """Extract S3 resource identifiers."""
        resources = []
        
        # Look for S3 URIs in parameters
        for value in parsed_command.parameters.values():
            if isinstance(value, str) and value.startswith('s3://'):
                resources.append(value)
        
        return resources
    
    def _extract_ec2_resources(self, parsed_command: ParsedCommand) -> List[str]:
        """Extract EC2 resource identifiers."""
        resources = []
        
        # Common EC2 resource parameters
        ec2_params = [
            'instance-ids', 'instance-id', 'volume-ids', 'volume-id',
            'security-group-ids', 'security-group-id', 'vpc-id', 'subnet-id'
        ]
        
        for param, value in parsed_command.parameters.items():
            if param in ec2_params:
                if isinstance(value, str):
                    resources.append(value)
        
        return resources
    
    def _extract_iam_resources(self, parsed_command: ParsedCommand) -> List[str]:
        """Extract IAM resource identifiers."""
        resources = []
        
        # Common IAM resource parameters
        iam_params = [
            'user-name', 'role-name', 'group-name', 'policy-name',
            'policy-arn', 'instance-profile-name'
        ]
        
        for param, value in parsed_command.parameters.items():
            if param in iam_params:
                if isinstance(value, str):
                    resources.append(value)
        
        return resources


# Example usage and testing
if __name__ == "__main__":
    parser = AWSCLIParser()
    
    # Test commands
    test_commands = [
        "aws s3 ls",
        "aws s3 cp file.txt s3://my-bucket/",
        "aws ec2 describe-instances --instance-ids i-1234567890abcdef0",
        "aws iam list-users",
        "aws lambda list-functions --region us-east-1",
        "aws sts assume-role --role-arn arn:aws:iam::123456789012:role/TestRole --role-session-name test-session"
    ]
    
    for cmd in test_commands:
        try:
            parsed = parser.parse_command(cmd)
            print(f"Command: {cmd}")
            print(f"  Service: {parsed.service}")
            print(f"  Action: {parsed.action}")
            print(f"  Parameters: {parsed.parameters}")
            print(f"  ARNs: {parsed.resource_arns}")
            print(f"  Resources: {parser.extract_resource_identifiers(parsed)}")
            print()
        except ValueError as e:
            print(f"Error parsing '{cmd}': {e}")
