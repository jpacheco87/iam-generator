"""
Tests for the IAM role generator module.
"""

import pytest
import json
from unittest.mock import MagicMock
from iam_generator.role_generator import IAMRoleGenerator
from iam_generator.analyzer import IAMPermissionAnalyzer


class TestIAMRoleGenerator:
    """Test suite for IAMRoleGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.role_generator = IAMRoleGenerator()
        self.analyzer = IAMPermissionAnalyzer()
    
    @pytest.fixture
    def sample_analysis_result(self):
        """Sample analysis result for testing."""
        return {
            "service": "s3",
            "action": "ls",
            "original_command": "aws s3 ls s3://my-bucket",
            "required_permissions": [
                {
                    "action": "s3:ListBucket",
                    "resource": "arn:aws:s3:::my-bucket",
                    "condition": None
                }
            ],
            "policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:ListBucket"],
                        "Resource": ["arn:aws:s3:::my-bucket"]
                    }
                ]
            }
        }
    
    def test_generate_basic_role(self, sample_analysis_result):
        """Test generation of basic IAM role."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="TestRole"
        )
        
        assert "json" in result
        assert "terraform" in result
        assert "cloudformation" in result
        assert "aws_cli" in result
        
        # Check JSON structure
        json_config = result["json"]
        assert "role_name" in json_config
        assert "trust_policy" in json_config
        assert "permissions_policy" in json_config
        assert json_config["role_name"] == "TestRole"
    
    def test_generate_role_with_ec2_trust_policy(self, sample_analysis_result):
        """Test generation of role with EC2 trust policy."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="EC2Role",
            trust_policy_type="ec2"
        )
        
        trust_policy = result["json"]["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["Service"] == "ec2.amazonaws.com"
        assert statement["Action"] == "sts:AssumeRole"
    
    def test_generate_role_with_lambda_trust_policy(self, sample_analysis_result):
        """Test generation of role with Lambda trust policy."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="LambdaRole",
            trust_policy_type="lambda"
        )
        
        trust_policy = result["json"]["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["Service"] == "lambda.amazonaws.com"
    
    def test_generate_role_with_ecs_trust_policy(self, sample_analysis_result):
        """Test generation of role with ECS trust policy."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="ECSRole",
            trust_policy_type="ecs"
        )
        
        trust_policy = result["json"]["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["Service"] == "ecs-tasks.amazonaws.com"
    
    def test_generate_role_with_cross_account_trust_policy(self, sample_analysis_result):
        """Test generation of role with cross-account trust policy."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="CrossAccountRole",
            trust_policy_type="cross-account",
            cross_account_id="123456789012"
        )
        
        trust_policy = result["json"]["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["AWS"] == "arn:aws:iam::123456789012:root"
    
    def test_cross_account_without_account_id_raises_error(self, sample_analysis_result):
        """Test that cross-account trust policy without account ID raises error."""
        with pytest.raises(ValueError, match="Cross-account ID is required"):
            self.role_generator.generate_role(
                analysis_result=sample_analysis_result,
                role_name="CrossAccountRole",
                trust_policy_type="cross-account"
            )
    
    def test_terraform_output_format(self, sample_analysis_result):
        """Test Terraform output format."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="TerraformRole"
        )
        
        terraform_config = result["terraform"]
        assert "resource \"aws_iam_role\" \"terraformrole\"" in terraform_config
        assert "resource \"aws_iam_policy\" \"terraformrole_policy\"" in terraform_config
        assert "resource \"aws_iam_role_policy_attachment\"" in terraform_config
    
    def test_cloudformation_output_format(self, sample_analysis_result):
        """Test CloudFormation output format."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="CloudFormationRole"
        )
        
        cf_config = result["cloudformation"]
        assert "Resources" in cf_config
        assert "CloudFormationRoleRole" in cf_config["Resources"]
        assert "CloudFormationRolePolicy" in cf_config["Resources"]
    
    def test_aws_cli_output_format(self, sample_analysis_result):
        """Test AWS CLI output format."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="CLIRole"
        )
        
        cli_config = result["aws_cli"]
        cli_content = "\n".join(cli_config) if isinstance(cli_config, list) else cli_config
        assert "aws iam create-role" in cli_content
        assert "aws iam create-policy" in cli_content
        assert "aws iam attach-role-policy" in cli_content
    
    def test_complex_permissions_policy(self):
        """Test generation with complex permissions policy."""
        complex_analysis = {
            "service": "s3",
            "action": "sync",
            "original_command": "aws s3 sync s3://source s3://dest",
            "required_permissions": [
                {"action": "s3:ListBucket", "resource": "arn:aws:s3:::source"},
                {"action": "s3:ListBucket", "resource": "arn:aws:s3:::dest"},
                {"action": "s3:GetObject", "resource": "arn:aws:s3:::source/*"},
                {"action": "s3:PutObject", "resource": "arn:aws:s3:::dest/*"},
                {"action": "s3:DeleteObject", "resource": "arn:aws:s3:::dest/*"}
            ],
            "policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:ListBucket",
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:DeleteObject"
                        ],
                        "Resource": [
                            "arn:aws:s3:::source",
                            "arn:aws:s3:::dest",
                            "arn:aws:s3:::source/*",
                            "arn:aws:s3:::dest/*"
                        ]
                    }
                ]
            }
        }
        
        result = self.role_generator.generate_role(
            analysis_result=complex_analysis,
            role_name="ComplexRole"
        )
        
        permissions_policy = result["json"]["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        
        assert len(statement["Action"]) >= 4
        assert len(statement["Resource"]) >= 4
        assert "s3:ListBucket" in statement["Action"]
        assert "s3:GetObject" in statement["Action"]
        assert "s3:PutObject" in statement["Action"]
        assert "s3:DeleteObject" in statement["Action"]
    
    def test_role_with_conditions(self):
        """Test generation of role with conditional permissions."""
        analysis_with_conditions = {
            "service": "s3",
            "action": "ls",
            "original_command": "aws s3 ls s3://bucket",
            "required_permissions": [
                {
                    "action": "s3:ListBucket",
                    "resource": "arn:aws:s3:::bucket",
                    "condition": {
                        "StringEquals": {
                            "s3:prefix": "allowed-path/*"
                        }
                    }
                }
            ],
            "policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:ListBucket"],
                        "Resource": ["arn:aws:s3:::bucket"],
                        "Condition": {
                            "StringEquals": {
                                "s3:prefix": "allowed-path/*"
                            }
                        }
                    }
                ]
            }
        }
        
        result = self.role_generator.generate_role(
            analysis_result=analysis_with_conditions,
            role_name="ConditionalRole"
        )
        
        permissions_policy = result["json"]["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        
        assert "Condition" in statement
        assert "StringEquals" in statement["Condition"]
    
    def test_invalid_trust_policy_type(self, sample_analysis_result):
        """Test handling of invalid trust policy type."""
        with pytest.raises(ValueError, match="Unsupported trust policy type"):
            self.role_generator.generate_role(
                analysis_result=sample_analysis_result,
                role_name="InvalidRole",
                trust_policy_type="invalid"
            )
    
    def test_role_name_sanitization(self, sample_analysis_result):
        """Test that role names are properly sanitized."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="Test-Role_With.Special@Characters"
        )
        
        # Check that Terraform uses sanitized name (no special characters)
        terraform_config = result["terraform"]
        assert "test_role_with_special_characters" in terraform_config.lower()
    
    def test_description_generation(self, sample_analysis_result):
        """Test that role descriptions are properly generated."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="DescribedRole",
            description="Custom description"
        )
        
        terraform_config = result["terraform"]
        assert "Custom description" in terraform_config
        
        cf_config = result["cloudformation"]
        # Check if custom description is in role properties
        role_resource = None
        for resource in cf_config["Resources"].values():
            if resource["Type"] == "AWS::IAM::Role":
                role_resource = resource
                break
        assert role_resource is not None
        assert role_resource["Properties"]["Description"] == "Custom description"
    
    def test_default_description_generation(self, sample_analysis_result):
        """Test that default descriptions are generated when not provided."""
        result = self.role_generator.generate_role(
            analysis_result=sample_analysis_result,
            role_name="DefaultDescRole"
        )
        
        terraform_config = result["terraform"]
        assert "aws s3 ls s3://my-bucket" in terraform_config
    
    def test_multiple_services_role_generation(self):
        """Test generation of role for commands using multiple services."""
        multi_service_analysis = {
            "service": "multiple",
            "action": "multiple",
            "original_command": "aws s3 ls && aws ec2 describe-instances",
            "required_permissions": [
                {"action": "s3:ListBucket", "resource": "arn:aws:s3:::bucket"},
                {"action": "ec2:DescribeInstances", "resource": "*"}
            ],
            "policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": ["s3:ListBucket", "ec2:DescribeInstances"],
                        "Resource": ["arn:aws:s3:::bucket", "*"]
                    }
                ]
            }
        }
        
        result = self.role_generator.generate_role(
            analysis_result=multi_service_analysis,
            role_name="MultiServiceRole"
        )
        
        permissions_policy = result["json"]["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        
        assert "s3:ListBucket" in statement["Action"]
        assert "ec2:DescribeInstances" in statement["Action"]
    
    def test_integration_with_analyzer(self):
        """Test integration between analyzer and role generator."""
        command = "aws s3 ls s3://test-bucket"
        
        # Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        # Generate role
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="IntegrationTestRole"
        )
        
        assert "json" in role_result
        assert "terraform" in role_result
        assert "cloudformation" in role_result
        assert "aws_cli" in role_result
        
        # Verify the policy includes the required permissions
        permissions_policy = role_result["json"]["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        assert "s3:ListBucket" in statement["Action"]
