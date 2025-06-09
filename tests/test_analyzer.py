"""
Tests for the IAM permission analyzer module.
"""

import pytest
from unittest.mock import patch, MagicMock
from iam_generator.analyzer import IAMPermissionAnalyzer


class TestIAMPermissionAnalyzer:
    """Test suite for IAMPermissionAnalyzer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = IAMPermissionAnalyzer()
    
    def test_analyze_s3_ls_command(self, sample_s3_command, expected_s3_permissions):
        """Test analysis of S3 ls command."""
        result = self.analyzer.analyze_command(sample_s3_command)
        
        assert result["service"] == "s3"
        assert result["action"] == "ls"
        assert result["original_command"] == sample_s3_command
        assert "required_permissions" in result
        assert len(result["required_permissions"]) > 0
        
        # Check for S3 ListBucket permission
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "s3:ListBucket" in actions
    
    def test_analyze_ec2_describe_command(self, sample_ec2_command, expected_ec2_permissions):
        """Test analysis of EC2 describe-instances command."""
        result = self.analyzer.analyze_command(sample_ec2_command)
        
        assert result["service"] == "ec2"
        assert result["action"] == "describe-instances"
        assert "required_permissions" in result
        
        # Check for EC2 DescribeInstances permission
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "ec2:DescribeInstances" in actions
    
    def test_analyze_lambda_invoke_command(self, sample_lambda_command):
        """Test analysis of Lambda invoke command."""
        result = self.analyzer.analyze_command(sample_lambda_command)
        
        assert result["service"] == "lambda"
        assert result["action"] == "invoke"
        assert "required_permissions" in result
        
        # Check for Lambda InvokeFunction permission
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "lambda:InvokeFunction" in actions
    
    def test_analyze_iam_command(self, sample_iam_command):
        """Test analysis of IAM list-users command."""
        result = self.analyzer.analyze_command(sample_iam_command)
        
        assert result["service"] == "iam"
        assert result["action"] == "list-users"
        assert "required_permissions" in result
        
        # Check for IAM ListUsers permission
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "iam:ListUsers" in actions
    
    def test_result_structure(self, sample_s3_command):
        """Test that analysis result has the correct structure."""
        result = self.analyzer.analyze_command(sample_s3_command)
        
        # Required fields
        assert "service" in result
        assert "action" in result
        assert "original_command" in result
        assert "required_permissions" in result
        assert "policy_document" in result
        
        # Optional fields
        if "additional_permissions" in result:
            assert isinstance(result["additional_permissions"], list)
        if "resource_arns" in result:
            assert isinstance(result["resource_arns"], list)
    
    def test_policy_document_generation(self, sample_s3_command):
        """Test that a valid IAM policy document is generated."""
        result = self.analyzer.analyze_command(sample_s3_command)
        
        policy = result["policy_document"]
        assert "Version" in policy
        assert "Statement" in policy
        assert policy["Version"] == "2012-10-17"
        assert isinstance(policy["Statement"], list)
        assert len(policy["Statement"]) > 0
        
        # Check statement structure
        statement = policy["Statement"][0]
        assert "Effect" in statement
        assert "Action" in statement
        assert "Resource" in statement
        assert statement["Effect"] == "Allow"
    
    def test_resource_arn_extraction(self, sample_s3_command):
        """Test that resource ARNs are correctly extracted."""
        result = self.analyzer.analyze_command(sample_s3_command)
        
        if "resource_arns" in result:
            arns = result["resource_arns"]
            assert len(arns) > 0
            # S3 bucket ARN should be present
            assert any("arn:aws:s3:::my-test-bucket" in arn for arn in arns)
    
    def test_s3_cp_command_analysis(self):
        """Test analysis of S3 cp command with source and destination."""
        command = "aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/"
        result = self.analyzer.analyze_command(command)
        
        assert result["service"] == "s3"
        assert result["action"] == "cp"
        
        # Should have both read and write permissions
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "s3:GetObject" in actions
        assert "s3:PutObject" in actions
        assert "s3:ListBucket" in actions
    
    def test_ec2_with_filters_analysis(self):
        """Test analysis of EC2 command with filters."""
        command = "aws ec2 describe-instances --filters Name=instance-state-name,Values=running"
        result = self.analyzer.analyze_command(command)
        
        assert result["service"] == "ec2"
        assert result["action"] == "describe-instances"
        
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "ec2:DescribeInstances" in actions
    
    def test_lambda_with_qualifier_analysis(self):
        """Test analysis of Lambda command with function qualifier."""
        command = "aws lambda invoke --function-name my-function:PROD output.json"
        result = self.analyzer.analyze_command(command)
        
        assert result["service"] == "lambda"
        assert result["action"] == "invoke"
        
        # Check that function ARN is correctly identified
        if "resource_arns" in result:
            arns = result["resource_arns"]
            assert any("my-function" in arn for arn in arns)
    
    def test_iam_with_arn_analysis(self):
        """Test analysis of IAM command with ARN parameter."""
        command = "aws iam attach-role-policy --role-name MyRole --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess"
        result = self.analyzer.analyze_command(command)
        
        assert result["service"] == "iam"
        assert result["action"] == "attach-role-policy"
        
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "iam:AttachRolePolicy" in actions
    
    def test_unsupported_service_analysis(self):
        """Test analysis of unsupported service command."""
        command = "aws unsupported-service some-action"
        result = self.analyzer.analyze_command(command)
        
        assert result["service"] == "unsupported-service"
        assert result["action"] == "some-action"
        # Should return empty permissions for unsupported service
        assert result["required_permissions"] == []
    
    def test_invalid_command_analysis(self):
        """Test analysis of invalid command format."""
        with pytest.raises(ValueError):
            self.analyzer.analyze_command("invalid command format")
    
    def test_complex_s3_sync_analysis(self):
        """Test analysis of complex S3 sync command."""
        command = "aws s3 sync s3://source-bucket/ s3://dest-bucket/ --delete --exclude '*.log'"
        result = self.analyzer.analyze_command(command)
        
        assert result["service"] == "s3"
        assert result["action"] == "sync"
        
        # Should include comprehensive permissions for sync
        actions = [perm["action"] for perm in result["required_permissions"]]
        assert "s3:GetObject" in actions
        assert "s3:PutObject" in actions
        assert "s3:DeleteObject" in actions
        assert "s3:ListBucket" in actions
    
    def test_policy_optimization(self, sample_s3_command):
        """Test that generated policies are optimized (no duplicate actions)."""
        result = self.analyzer.analyze_command(sample_s3_command)
        
        policy = result["policy_document"]
        statement = policy["Statement"][0]
        actions = statement["Action"]
        
        # Check for no duplicate actions
        if isinstance(actions, list):
            assert len(actions) == len(set(actions))
    
    def test_resource_specific_permissions(self):
        """Test that resource-specific permissions are correctly applied."""
        command = "aws s3 ls s3://specific-bucket/path/"
        result = self.analyzer.analyze_command(command)
        
        # Check that bucket-specific resources are used
        for perm in result["required_permissions"]:
            if perm["action"] == "s3:ListBucket":
                assert "specific-bucket" in perm["resource"]
    
    @patch('iam_generator.analyzer.IAMPermissionAnalyzer._enhance_with_additional_permissions')
    def test_additional_permissions_enhancement(self, mock_enhance):
        """Test that additional permissions enhancement is called."""
        mock_enhance.return_value = []
        
        result = self.analyzer.analyze_command("aws s3 ls s3://bucket")
        
        mock_enhance.assert_called_once()
    
    def test_multiple_resource_handling(self):
        """Test handling of commands with multiple resources."""
        command = "aws s3 cp s3://bucket1/file s3://bucket2/ --recursive"
        result = self.analyzer.analyze_command(command)
        
        # Should handle multiple buckets
        if "resource_arns" in result:
            arns = result["resource_arns"]
            assert any("bucket1" in arn for arn in arns)
            assert any("bucket2" in arn for arn in arns)
