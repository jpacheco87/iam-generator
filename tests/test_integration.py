"""
Integration tests for the complete IAM Generator workflow.
"""

import pytest
import json
from iam_generator.analyzer import IAMPermissionAnalyzer
from iam_generator.role_generator import IAMRoleGenerator


class TestIntegration:
    """Integration test suite for the complete workflow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = IAMPermissionAnalyzer()
        self.role_generator = IAMRoleGenerator()
    
    def test_s3_ls_complete_workflow(self):
        """Test complete workflow for S3 ls command."""
        command = "aws s3 ls s3://my-test-bucket"
        
        # Step 1: Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        assert analysis_result["service"] == "s3"
        assert analysis_result["action"] == "ls"
        assert len(analysis_result["required_permissions"]) > 0
        
        # Step 2: Generate role
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="S3ListRole"
        )
        
        assert "json" in role_result
        assert "terraform" in role_result
        assert "cloudformation" in role_result
        assert "aws_cli" in role_result
        
        # Step 3: Validate generated configurations
        json_config = role_result["json"]
        assert json_config["role_name"] == "S3ListRole"
        assert "trust_policy" in json_config
        assert "permissions_policy" in json_config
        
        # Validate trust policy
        trust_policy = json_config["trust_policy"]
        assert trust_policy["Version"] == "2012-10-17"
        assert len(trust_policy["Statement"]) > 0
        
        # Validate permissions policy
        permissions_policy = json_config["permissions_policy"]
        assert permissions_policy["Version"] == "2012-10-17"
        assert len(permissions_policy["Statement"]) > 0
        
        statement = permissions_policy["Statement"][0]
        assert "s3:ListBucket" in statement["Action"]
    
    def test_ec2_describe_complete_workflow(self):
        """Test complete workflow for EC2 describe-instances command."""
        command = "aws ec2 describe-instances --region us-west-2"
        
        # Step 1: Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        assert analysis_result["service"] == "ec2"
        assert analysis_result["action"] == "describe-instances"
        
        # Step 2: Generate role with Lambda trust policy
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="EC2DescribeRole",
            trust_policy_type="lambda"
        )
        
        # Step 3: Validate Lambda trust policy
        json_config = role_result["json"]
        trust_policy = json_config["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["Service"] == "lambda.amazonaws.com"
        
        # Validate EC2 permissions
        permissions_policy = json_config["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        assert "ec2:DescribeInstances" in statement["Action"]
    
    def test_lambda_invoke_complete_workflow(self):
        """Test complete workflow for Lambda invoke command."""
        command = "aws lambda invoke --function-name my-function output.json"
        
        # Step 1: Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        assert analysis_result["service"] == "lambda"
        assert analysis_result["action"] == "invoke"
        
        # Step 2: Generate role with ECS trust policy
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="LambdaInvokeRole",
            trust_policy_type="ecs"
        )
        
        # Step 3: Validate ECS trust policy
        json_config = role_result["json"]
        trust_policy = json_config["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["Service"] == "ecs-tasks.amazonaws.com"
        
        # Validate Lambda permissions
        permissions_policy = json_config["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        assert "lambda:InvokeFunction" in statement["Action"]
    
    def test_s3_cp_complex_workflow(self):
        """Test complete workflow for complex S3 cp command."""
        command = "aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/ --recursive"
        
        # Step 1: Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        assert analysis_result["service"] == "s3"
        assert analysis_result["action"] == "cp"
        
        # Should have multiple permissions for copy operation
        actions = [perm["action"] for perm in analysis_result["required_permissions"]]
        assert "s3:GetObject" in actions
        assert "s3:PutObject" in actions
        assert "s3:ListBucket" in actions
        
        # Step 2: Generate role
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="S3CopyRole"
        )
        
        # Step 3: Validate comprehensive permissions
        permissions_policy = role_result["json"]["permissions_policy"]
        
        # Collect all actions across all statements
        all_actions = []
        for statement in permissions_policy["Statement"]:
            all_actions.extend(statement["Action"])
        
        assert "s3:GetObject" in all_actions
        assert "s3:PutObject" in all_actions
        assert "s3:ListBucket" in all_actions
        
        # Should have resources for both source and destination buckets
        all_resources = []
        for statement in permissions_policy["Statement"]:
            if "Resource" in statement:
                if isinstance(statement["Resource"], list):
                    all_resources.extend(statement["Resource"])
                else:
                    all_resources.append(statement["Resource"])
        
        assert any("source-bucket" in resource for resource in all_resources)
        assert any("dest-bucket" in resource for resource in all_resources)
    
    def test_cross_account_role_workflow(self):
        """Test complete workflow for cross-account role."""
        command = "aws s3 ls s3://shared-bucket"
        
        # Step 1: Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        # Step 2: Generate cross-account role
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="CrossAccountS3Role",
            trust_policy_type="cross-account",
            cross_account_id="123456789012"
        )
        
        # Step 3: Validate cross-account trust policy
        json_config = role_result["json"]
        trust_policy = json_config["trust_policy"]
        statement = trust_policy["Statement"][0]
        assert statement["Principal"]["AWS"] == "arn:aws:iam::123456789012:root"
    
    def test_iam_command_workflow(self):
        """Test complete workflow for IAM command."""
        command = "aws iam list-users --path-prefix /division_abc/"
        
        # Step 1: Analyze command
        analysis_result = self.analyzer.analyze_command(command)
        
        assert analysis_result["service"] == "iam"
        assert analysis_result["action"] == "list-users"
        
        # Step 2: Generate role
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="IAMListUsersRole"
        )
        
        # Step 3: Validate IAM permissions
        permissions_policy = role_result["json"]["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        assert "iam:ListUsers" in statement["Action"]
    
    def test_terraform_output_validity(self):
        """Test that generated Terraform configuration is valid."""
        command = "aws s3 ls s3://bucket"
        
        analysis_result = self.analyzer.analyze_command(command)
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="TerraformTestRole"
        )
        
        terraform_config = role_result["terraform"]
        
        # Check for required Terraform blocks
        assert "resource \"aws_iam_role\"" in terraform_config
        assert "resource \"aws_iam_policy\"" in terraform_config
        assert "resource \"aws_iam_role_policy_attachment\"" in terraform_config
        
        # Check for proper HCL syntax elements
        assert "assume_role_policy" in terraform_config
        assert "policy =" in terraform_config
        assert "role       =" in terraform_config
        assert "policy_arn =" in terraform_config
    
    def test_cloudformation_output_validity(self):
        """Test that generated CloudFormation template is valid."""
        command = "aws s3 ls s3://bucket"
        
        analysis_result = self.analyzer.analyze_command(command)
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="CloudFormationTestRole"
        )
        
        cf_config = role_result["cloudformation"]
        
        # Check for required CloudFormation structure
        assert "AWSTemplateFormatVersion" in cf_config
        assert "Resources" in cf_config
        assert "Description" in cf_config
        assert "Outputs" in cf_config
        
        # Check resources
        resources = cf_config["Resources"]
        role_resources = [k for k, v in resources.items() if v["Type"] == "AWS::IAM::Role"]
        policy_resources = [k for k, v in resources.items() if v["Type"] == "AWS::IAM::Policy"]
        
        assert len(role_resources) > 0
        assert len(policy_resources) > 0
    
    def test_aws_cli_output_validity(self):
        """Test that generated AWS CLI commands are valid."""
        command = "aws s3 ls s3://bucket"
        
        analysis_result = self.analyzer.analyze_command(command)
        role_result = self.role_generator.generate_role(
            analysis_result=analysis_result,
            role_name="CLITestRole"
        )
        
        cli_config = role_result["aws_cli"]
        
        # Join all lines for string searching
        cli_content = "\n".join(cli_config) if isinstance(cli_config, list) else cli_config
        
        # Check for required AWS CLI commands
        assert "aws iam create-role" in cli_content
        assert "aws iam create-policy" in cli_content
        assert "aws iam attach-role-policy" in cli_content
        
        # Check for proper CLI options
        assert "--role-name" in cli_content
        assert "--assume-role-policy-document" in cli_content
        assert "--policy-name" in cli_content
        assert "--policy-document" in cli_content
    
    def test_policy_document_validity(self):
        """Test that generated policy documents are valid IAM policies."""
        command = "aws s3 cp s3://source s3://dest --recursive"
        
        analysis_result = self.analyzer.analyze_command(command)
        
        policy_doc = analysis_result["policy_document"]
        
        # Check policy structure
        assert policy_doc["Version"] == "2012-10-17"
        assert "Statement" in policy_doc
        assert isinstance(policy_doc["Statement"], list)
        assert len(policy_doc["Statement"]) > 0
        
        # Check statement structure
        statement = policy_doc["Statement"][0]
        assert statement["Effect"] == "Allow"
        assert "Action" in statement
        assert "Resource" in statement
        
        # Actions should be strings or list of strings
        actions = statement["Action"]
        if isinstance(actions, list):
            assert all(isinstance(action, str) for action in actions)
        else:
            assert isinstance(actions, str)
        
        # Resources should be strings or list of strings
        resources = statement["Resource"]
        if isinstance(resources, list):
            assert all(isinstance(resource, str) for resource in resources)
        else:
            assert isinstance(resources, str)
    
    def test_multiple_commands_workflow(self):
        """Test workflow with multiple related commands."""
        commands = [
            "aws s3 ls s3://bucket",
            "aws s3 cp file.txt s3://bucket/",
            "aws s3 rm s3://bucket/old-file.txt"
        ]
        
        all_permissions = set()
        all_resources = set()
        
        for command in commands:
            analysis_result = self.analyzer.analyze_command(command)
            
            # Collect all permissions and resources
            for perm in analysis_result["required_permissions"]:
                all_permissions.add(perm["action"])
                all_resources.add(perm["resource"])
        
        # Create a combined analysis result
        combined_analysis = {
            "service": "s3",
            "action": "multiple",
            "original_command": " && ".join(commands),
            "required_permissions": [
                {"action": action, "resource": "*"} for action in all_permissions
            ],
            "policy_document": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": list(all_permissions),
                        "Resource": list(all_resources)
                    }
                ]
            }
        }
        
        # Generate role for combined permissions
        role_result = self.role_generator.generate_role(
            analysis_result=combined_analysis,
            role_name="MultiCommandRole"
        )
        
        # Should include all required permissions
        permissions_policy = role_result["json"]["permissions_policy"]
        statement = permissions_policy["Statement"][0]
        
        assert "s3:ListBucket" in statement["Action"]
        assert "s3:PutObject" in statement["Action"]
        assert "s3:DeleteObject" in statement["Action"]
