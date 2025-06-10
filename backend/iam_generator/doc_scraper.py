"""
AWS CLI Documentation Scraper

This module automatically discovers AWS CLI commands and maps them to IAM permissions
by scraping AWS CLI help documentation and applying intelligent mapping rules.
"""

import subprocess
import re
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

try:
    from .permissions_db import IAMPermission, CommandPermissions
except ImportError:
    # Handle relative import issues
    import sys
    sys.path.append(str(Path(__file__).parent))
    from permissions_db import IAMPermission, CommandPermissions

logger = logging.getLogger(__name__)

@dataclass
class CommandInfo:
    """Information about an AWS CLI command."""
    service: str
    command: str
    description: str
    confidence: str  # 'high', 'medium', 'low'

@dataclass
class ServiceInfo:
    """Information about an AWS service."""
    name: str
    description: str
    commands: List[CommandInfo]

class AWSCLIDocumentationScraper:
    """Scrapes AWS CLI documentation to build comprehensive permissions database."""
    
    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.permission_mapping_rules = self._load_mapping_rules()
        self.special_cases = self._load_special_cases()
        
    def _load_mapping_rules(self) -> Dict[str, Dict]:
        """Load rules for mapping CLI commands to IAM permissions."""
        return {
            # Common patterns for command to permission mapping
            "patterns": {
                "describe-*": "{service}:Describe*",
                "list-*": "{service}:List*", 
                "get-*": "{service}:Get*",
                "create-*": "{service}:Create*",
                "delete-*": "{service}:Delete*",
                "put-*": "{service}:Put*",
                "update-*": "{service}:Update*",
                "modify-*": "{service}:Modify*",
                "attach-*": "{service}:Attach*",
                "detach-*": "{service}:Detach*",
                "enable-*": "{service}:Enable*",
                "disable-*": "{service}:Disable*",
                "start-*": "{service}:Start*",
                "stop-*": "{service}:Stop*",
                "restart-*": "{service}:Restart*",
                "terminate-*": "{service}:Terminate*",
                "reboot-*": "{service}:Reboot*",
                "authorize-*": "{service}:Authorize*",
                "revoke-*": "{service}:Revoke*",
                "copy-*": "{service}:Copy*",
                "sync": "s3:ListBucket,s3:GetObject,s3:PutObject,s3:DeleteObject",
                "cp": "s3:GetObject,s3:PutObject",
                "mv": "s3:GetObject,s3:PutObject,s3:DeleteObject",
                "rm": "s3:DeleteObject",
                "ls": "s3:ListBucket"
            },
            
            # Service-specific patterns
            "service_patterns": {
                "s3": {
                    "ls": ["s3:ListBucket"],
                    "cp": ["s3:GetObject", "s3:PutObject"],
                    "mv": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    "rm": ["s3:DeleteObject"],
                    "sync": ["s3:ListBucket", "s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                    "mb": ["s3:CreateBucket"],
                    "rb": ["s3:DeleteBucket"]
                },
                "ec2": {
                    "run-instances": ["ec2:RunInstances", "ec2:DescribeImages", "ec2:DescribeKeyPairs", "ec2:DescribeSecurityGroups", "ec2:DescribeSubnets"],
                    "copy-image": ["ec2:CopyImage", "ec2:DescribeImages"],
                    "import-image": ["ec2:ImportImage", "ec2:DescribeImportImageTasks"],
                    "create-image": ["ec2:CreateImage", "ec2:DescribeInstances"],
                    "register-image": ["ec2:RegisterImage"]
                },
                "lambda": {
                    "create-function": ["lambda:CreateFunction", "iam:PassRole"],
                    "update-function-code": ["lambda:UpdateFunctionCode"],
                    "update-function-configuration": ["lambda:UpdateFunctionConfiguration"],
                    "invoke": ["lambda:InvokeFunction"]
                },
                "rds": {
                    "create-db-instance": ["rds:CreateDBInstance", "rds:DescribeDBSubnetGroups", "rds:DescribeDBParameterGroups"],
                    "describe-db-engine-versions": ["rds:DescribeDBEngineVersions"],
                    "create-custom-db-engine-version": ["rds:CreateCustomDBEngineVersion"],
                    "describe-custom-db-engine-versions": ["rds:DescribeCustomDBEngineVersions"],
                    "modify-db-instance": ["rds:ModifyDBInstance"]
                }
            }
        }
    
    def _load_special_cases(self) -> Dict[str, Dict]:
        """Load special cases that require manual handling."""
        return {
            # Commands that need additional permissions beyond the basic mapping
            "additional_permissions": {
                "lambda:CreateFunction": ["iam:PassRole"],
                "lambda:UpdateFunctionConfiguration": ["iam:PassRole"],
                "ec2:RunInstances": ["ec2:DescribeImages", "ec2:DescribeKeyPairs", "ec2:DescribeSecurityGroups", "ec2:DescribeSubnets"],
                "ec2:CreateSecurityGroup": ["ec2:DescribeVpcs"],
                "iam:AttachUserPolicy": ["iam:GetPolicy"],
                "iam:AttachRolePolicy": ["iam:GetPolicy"],
                "iam:AttachGroupPolicy": ["iam:GetPolicy"]
            },
            
            # Resource ARN patterns by service
            "resource_patterns": {
                "s3": ["arn:aws:s3:::*", "arn:aws:s3:::*/*"],
                "ec2": ["arn:aws:ec2:*:*:instance/*", "arn:aws:ec2:*:*:volume/*", "arn:aws:ec2:*:*:security-group/*"],
                "lambda": ["arn:aws:lambda:*:*:function:*"],
                "iam": ["arn:aws:iam::*:user/*", "arn:aws:iam::*:role/*", "arn:aws:iam::*:policy/*"],
                "rds": ["arn:aws:rds:*:*:db:*", "arn:aws:rds:*:*:cluster:*"],
                "dynamodb": ["arn:aws:dynamodb:*:*:table/*"]
            }
        }
    
    def discover_services(self) -> List[str]:
        """Discover all available AWS services from CLI help."""
        try:
            logger.info("Discovering AWS services...")
            result = subprocess.run(
                ["aws", "help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to get AWS help: {result.stderr}")
                return []
            
            # Parse the help output to extract service names
            # Clean up terminal formatting escape sequences
            cleaned_output = re.sub(r'.\x08', '', result.stdout)  # Remove backspace formatting
            lines = cleaned_output.split('\n')
            services = []
            in_services_section = False
            
            for line in lines:
                # Handle terminal formatting in section headers
                if "Available Services:" in line or "AVAILABLE SERVICES" in line:
                    in_services_section = True
                    continue
                
                if in_services_section:
                    if line.strip() == "":
                        continue  # Skip empty lines, don't break
                    if line.startswith("SEE ALSO") or line.startswith("EXAMPLES"):
                        break
                    
                    # Extract service names (AWS CLI uses format: "       o service-name")
                    match = re.match(r'\s+o\s+([a-z0-9-]+)', line)
                    if match:
                        service_name = match.group(1)
                        if service_name not in ['help', 'configure']:  # Skip utility commands
                            services.append(service_name)
            
            logger.info(f"Discovered {len(services)} AWS services")
            return services
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout while discovering AWS services")
            return []
        except Exception as e:
            logger.error(f"Error discovering AWS services: {e}")
            return []
    
    def discover_commands(self, service: str) -> List[CommandInfo]:
        """Discover all commands for a specific AWS service."""
        try:
            logger.info(f"Discovering commands for service: {service}")
            result = subprocess.run(
                ["aws", service, "help"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"Failed to get help for service {service}: {result.stderr}")
                return []
            
            # Parse the help output to extract command names
            # Clean up terminal formatting escape sequences
            cleaned_output = re.sub(r'.\x08', '', result.stdout)  # Remove backspace formatting
            lines = cleaned_output.split('\n')
            commands = []
            in_commands_section = False
            
            for line in lines:
                if "Available Commands:" in line or "AVAILABLE COMMANDS" in line:
                    in_commands_section = True
                    continue
                
                if in_commands_section:
                    # Don't break on empty lines, just continue
                    if line.strip() == "":
                        continue
                    if line.startswith("SEE ALSO") or line.startswith("EXAMPLES"):
                        break
                    
                    # Extract command names and descriptions
                    # AWS CLI uses format: "       o command-name"
                    match = re.match(r'\s+o\s+([a-z0-9-]+)(?:\s+(.+))?', line)
                    if match:
                        command_name = match.group(1)
                        description = match.group(2) or ""
                        
                        # Skip utility commands
                        if command_name not in ['help', 'wait']:
                            commands.append(CommandInfo(
                                service=service,
                                command=command_name,
                                description=description.strip(),
                                confidence='medium'  # Default confidence
                            ))
            
            logger.info(f"Discovered {len(commands)} commands for {service}")
            return commands
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout while discovering commands for {service}")
            return []
        except Exception as e:
            logger.warning(f"Error discovering commands for {service}: {e}")
            return []
    
    def _convert_command_to_action(self, command: str) -> str:
        """Convert a CLI command name to IAM action format."""
        # Split on hyphens and convert to PascalCase
        parts = command.split('-')
        return ''.join(word.capitalize() for word in parts)
    
    def _get_base_permissions(self, service: str, command: str) -> List[str]:
        """Get base IAM permissions for a command using mapping rules."""
        # Check service-specific patterns first
        service_patterns = self.permission_mapping_rules.get("service_patterns", {}).get(service, {})
        if command in service_patterns:
            return service_patterns[command]
        
        # Apply general patterns
        action = self._convert_command_to_action(command)
        base_permission = f"{service}:{action}"
        
        # Handle special command patterns
        patterns = self.permission_mapping_rules.get("patterns", {})
        for pattern, permission_template in patterns.items():
            if pattern.endswith('*'):
                prefix = pattern[:-1]
                if command.startswith(prefix):
                    if '{service}' in permission_template:
                        permission = permission_template.format(service=service)
                        if ',' in permission:
                            return permission.split(',')
                        return [permission]
            elif pattern == command:
                if '{service}' in permission_template:
                    permission = permission_template.format(service=service)
                    if ',' in permission:
                        return permission.split(',')
                    return [permission]
        
        return [base_permission]
    
    def _get_additional_permissions(self, service: str, command: str, base_permissions: List[str]) -> List[str]:
        """Get additional permissions that might be required."""
        additional = []
        
        # Check for additional permissions based on the base permissions
        additional_rules = self.special_cases.get("additional_permissions", {})
        for base_perm in base_permissions:
            if base_perm in additional_rules:
                additional.extend(additional_rules[base_perm])
        
        # Add describe permissions for create/modify operations
        if any(keyword in command for keyword in ['create', 'modify', 'update', 'attach']):
            describe_perm = f"{service}:Describe*"
            if describe_perm not in base_permissions and describe_perm not in additional:
                additional.append(describe_perm)
        
        return additional
    
    def _get_resource_patterns(self, service: str, command: str) -> List[str]:
        """Get resource ARN patterns for a service."""
        service_patterns = self.special_cases.get("resource_patterns", {})
        return service_patterns.get(service, ["*"])
    
    def map_command_to_permissions(self, service: str, command: str) -> CommandPermissions:
        """Map a CLI command to IAM permissions."""
        # Get base permissions
        base_permissions = self._get_base_permissions(service, command)
        
        # Get additional permissions
        additional_permissions = self._get_additional_permissions(service, command, base_permissions)
        
        # Combine all permissions
        all_permissions = base_permissions + additional_permissions
        
        # Remove duplicates while preserving order
        seen = set()
        unique_permissions = []
        for perm in all_permissions:
            if perm not in seen:
                seen.add(perm)
                unique_permissions.append(perm)
        
        # Convert to IAMPermission objects
        iam_permissions = []
        for perm in unique_permissions:
            iam_permissions.append(IAMPermission(action=perm, resource="*"))
        
        # Get resource patterns
        resource_patterns = self._get_resource_patterns(service, command)
        
        # Determine confidence level
        confidence = self._determine_confidence(service, command)
        
        return CommandPermissions(
            service=service,
            action=command,
            permissions=iam_permissions,
            description=f"Auto-generated permissions for {service} {command}",
            resource_patterns=resource_patterns
        )
    
    def _determine_confidence(self, service: str, command: str) -> str:
        """Determine confidence level for the permission mapping."""
        # High confidence for well-known patterns
        if service in self.permission_mapping_rules.get("service_patterns", {}):
            if command in self.permission_mapping_rules["service_patterns"][service]:
                return "high"
        
        # Medium confidence for standard patterns
        patterns = self.permission_mapping_rules.get("patterns", {})
        for pattern in patterns.keys():
            if pattern.endswith('*'):
                prefix = pattern[:-1]
                if command.startswith(prefix):
                    return "medium"
            elif pattern == command:
                return "medium"
        
        # Low confidence for unknown patterns
        return "low"
    
    def scrape_all_services(self, services: Optional[List[str]] = None) -> Dict[str, ServiceInfo]:
        """Scrape all AWS services and their commands."""
        if services is None:
            services = self.discover_services()
        
        logger.info(f"Scraping {len(services)} AWS services...")
        
        for service in services:
            commands = self.discover_commands(service)
            if commands:
                self.services[service] = ServiceInfo(
                    name=service,
                    description=f"AWS {service.upper()} service",
                    commands=commands
                )
        
        logger.info(f"Successfully scraped {len(self.services)} services")
        return self.services
    
    def generate_permissions_database(self, services: Optional[List[str]] = None) -> Dict[str, Dict[str, CommandPermissions]]:
        """Generate a comprehensive permissions database."""
        if not self.services:
            self.scrape_all_services(services)
        
        logger.info("Generating permissions database...")
        
        database = {}
        
        for service_name, service_info in self.services.items():
            database[service_name] = {}
            
            for command_info in service_info.commands:
                command_permissions = self.map_command_to_permissions(
                    command_info.service,
                    command_info.command
                )
                database[service_name][command_info.command] = command_permissions
        
        logger.info(f"Generated database with {len(database)} services")
        return database
    
    def save_database_to_file(self, database: Dict, output_file: str):
        """Save the generated database to a Python file."""
        logger.info(f"Saving database to {output_file}")
        
        # Generate Python code for the database
        content = '''"""
Auto-generated AWS CLI permissions database.
Generated by doc_scraper.py
"""

from .permissions_db import IAMPermission, CommandPermissions

# Auto-generated permissions database
GENERATED_PERMISSIONS_DB = {
'''
        
        for service_name, commands in database.items():
            content += f'    "{service_name}": {{\n'
            
            for command_name, command_perms in commands.items():
                content += f'        "{command_name}": CommandPermissions(\n'
                content += f'            service="{command_perms.service}",\n'
                content += f'            action="{command_perms.action}",\n'
                content += f'            permissions=[\n'
                
                for perm in command_perms.permissions:
                    content += f'                IAMPermission(action="{perm.action}", resource="{perm.resource}"),\n'
                
                content += f'            ],\n'
                content += f'            description="{command_perms.description}",\n'
                content += f'            resource_patterns={command_perms.resource_patterns}\n'
                content += f'        ),\n'
            
            content += f'    }},\n'
        
        content += '}\n'
        
        with open(output_file, 'w') as f:
            f.write(content)
        
        logger.info(f"Database saved to {output_file}")
    
    def compare_with_existing(self, existing_db: Dict, services: Optional[List[str]] = None) -> Dict[str, List[str]]:
        """Compare generated database with existing database."""
        comparison = {
            "missing_services": [],
            "missing_commands": [],
            "new_services": [],
            "new_commands": []
        }
        
        generated_db = self.generate_permissions_database(services)
        
        # Find missing services in existing DB
        for service in generated_db.keys():
            if service not in existing_db:
                comparison["missing_services"].append(service)
        
        # Find new services in generated DB
        for service in existing_db.keys():
            if service not in generated_db:
                comparison["new_services"].append(service)
        
        # Find missing commands
        for service, commands in generated_db.items():
            if service in existing_db:
                for command in commands.keys():
                    if command not in existing_db[service]:
                        comparison["missing_commands"].append(f"{service}:{command}")
        
        # Find new commands in existing DB
        for service, commands in existing_db.items():
            if service in generated_db:
                for command in commands.keys():
                    if command not in generated_db[service]:
                        comparison["new_commands"].append(f"{service}:{command}")
        
        return comparison


def main():
    """Main function for testing the scraper."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AWS CLI Documentation Scraper")
    parser.add_argument("--services", nargs="+", help="Specific services to scrape")
    parser.add_argument("--output", default="generated_permissions_db.py", help="Output file")
    parser.add_argument("--compare", action="store_true", help="Compare with existing database")
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    
    scraper = AWSCLIDocumentationScraper()
    
    if args.compare:
        # Import existing database for comparison
        try:
            try:
                from .permissions_db import IAMPermissionsDatabase
            except ImportError:
                from permissions_db import IAMPermissionsDatabase
            
            # Create instance and get the internal database
            existing_db_instance = IAMPermissionsDatabase()
            existing_db = existing_db_instance._permissions_map
            
            comparison = scraper.compare_with_existing(existing_db)
            print("Database Comparison Results:")
            print(f"Missing services: {comparison['missing_services']}")
            print(f"Missing commands: {comparison['missing_commands']}")
            print(f"New services: {comparison['new_services']}")
            print(f"New commands: {comparison['new_commands']}")
        except ImportError:
            print("Could not import existing database for comparison")
    else:
        # Generate new database
        database = scraper.generate_permissions_database(args.services)
        scraper.save_database_to_file(database, args.output)
        print(f"Generated database saved to {args.output}")


if __name__ == "__main__":
    main()
