"""
AWS IAM Generator - A tool to analyze AWS CLI commands and generate IAM permissions
"""

from .parser import AWSCLIParser
from .permissions_db import IAMPermissionsDatabase
from .analyzer import IAMPermissionAnalyzer
from .role_generator import IAMRoleGenerator
from .cli import cli

__version__ = "1.0.0"
__author__ = "IAM Generator Team"
__email__ = "team@iamgenerator.dev"

__all__ = [
    "AWSCLIParser",
    "IAMPermissionsDatabase", 
    "IAMPermissionAnalyzer",
    "IAMRoleGenerator",
    "cli"
]
