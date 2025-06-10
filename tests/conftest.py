"""
Test configuration and fixtures for IAM Generator tests.
"""

import sys
from pathlib import Path
import pytest
from typing import Dict, Any

# Add backend directory to Python path for testing
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def sample_s3_command() -> str:
    """Sample S3 command for testing."""
    return "aws s3 ls s3://my-test-bucket/folder/"


@pytest.fixture
def sample_ec2_command() -> str:
    """Sample EC2 command for testing."""
    return "aws ec2 describe-instances --region us-west-2 --instance-ids i-1234567890abcdef0"


@pytest.fixture
def sample_lambda_command() -> str:
    """Sample Lambda command for testing."""
    return "aws lambda invoke --function-name my-function output.json"


@pytest.fixture
def sample_iam_command() -> str:
    """Sample IAM command for testing."""
    return "aws iam list-users --path-prefix /division_abc/"


@pytest.fixture
def expected_s3_permissions() -> Dict[str, Any]:
    """Expected permissions for S3 list command."""
    return {
        "service": "s3",
        "action": "ls",
        "required_permissions": [
            {
                "action": "s3:ListBucket",
                "resource": "arn:aws:s3:::my-test-bucket",
                "condition": None
            }
        ]
    }


@pytest.fixture
def expected_ec2_permissions() -> Dict[str, Any]:
    """Expected permissions for EC2 describe command."""
    return {
        "service": "ec2",
        "action": "describe-instances",
        "required_permissions": [
            {
                "action": "ec2:DescribeInstances",
                "resource": "*",
                "condition": None
            }
        ]
    }


@pytest.fixture
def sample_policy_document() -> Dict[str, Any]:
    """Sample IAM policy document."""
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::my-test-bucket"
                ]
            }
        ]
    }
