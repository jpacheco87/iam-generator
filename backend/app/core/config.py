"""
Core configuration and settings for the IAM Generator API.
"""

import sys
from pathlib import Path
from typing import List

# Add the iam_generator package to the path  
PROJECT_ROOT = Path(__file__).parent.parent.parent
BACKEND_PATH = PROJECT_ROOT
sys.path.append(str(BACKEND_PATH))

# API Configuration
API_TITLE = "AWS IAM Generator API"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
AWS IAM Generator API - Analyze AWS CLI commands and generate precise IAM permissions.

This API provides endpoints for:
- Analyzing individual AWS CLI commands
- Batch analysis of multiple commands
- Generating IAM roles and policies
- Resource-specific permission analysis
- Least privilege policy generation
"""

# CORS Configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:80",  # Docker container communication
    "http://localhost:80",  # Docker host access
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",  # Vite dev server alternate
]

# Application Settings
DEBUG = False
LOG_LEVEL = "info"

# Default AWS Configuration
DEFAULT_ACCOUNT_ID = "123456789012"
DEFAULT_REGION = "us-east-1"
