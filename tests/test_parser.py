"""
Tests for the AWS CLI command parser module.
"""

import pytest
from iam_generator.parser import AWSCLIParser, ParsedCommand


class TestAWSCLIParser:
    """Test suite for AWSCLIParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = AWSCLIParser()
    
    def test_parse_s3_ls_command(self, sample_s3_command):
        """Test parsing of S3 ls command."""
        result = self.parser.parse_command(sample_s3_command)
        
        assert isinstance(result, ParsedCommand)
        assert result.service == "s3"
        assert result.action == "ls"
        assert result.original_command == sample_s3_command
        assert "s3://my-test-bucket/folder/" in result.parameters
    
    def test_parse_ec2_describe_command(self, sample_ec2_command):
        """Test parsing of EC2 describe-instances command."""
        result = self.parser.parse_command(sample_ec2_command)
        
        assert result.service == "ec2"
        assert result.action == "describe-instances"
        assert "--region" in result.parameters
        assert "--instance-ids" in result.parameters
    
    def test_parse_lambda_invoke_command(self, sample_lambda_command):
        """Test parsing of Lambda invoke command."""
        result = self.parser.parse_command(sample_lambda_command)
        
        assert result.service == "lambda"
        assert result.action == "invoke"
        assert "--function-name" in result.parameters
        assert "my-function" in result.parameters
    
    def test_parse_iam_command(self, sample_iam_command):
        """Test parsing of IAM list-users command."""
        result = self.parser.parse_command(sample_iam_command)
        
        assert result.service == "iam"
        assert result.action == "list-users"
        assert "--path-prefix" in result.parameters
    
    def test_extract_s3_arns(self, sample_s3_command):
        """Test extraction of S3 ARNs from command."""
        result = self.parser.parse_command(sample_s3_command)
        arns = self.parser.extract_arns(result)
        
        assert len(arns) > 0
        assert any("arn:aws:s3:::my-test-bucket" in arn for arn in arns)
    
    def test_extract_ec2_arns(self, sample_ec2_command):
        """Test extraction of EC2 instance ARNs from command."""
        result = self.parser.parse_command(sample_ec2_command)
        arns = self.parser.extract_arns(result)
        
        assert len(arns) > 0
        assert any("i-1234567890abcdef0" in arn for arn in arns)
    
    def test_extract_lambda_arns(self, sample_lambda_command):
        """Test extraction of Lambda function ARNs from command."""
        result = self.parser.parse_command(sample_lambda_command)
        arns = self.parser.extract_arns(result)
        
        assert len(arns) > 0
        assert any("my-function" in arn for arn in arns)
    
    def test_invalid_command_format(self):
        """Test handling of invalid command format."""
        with pytest.raises(ValueError):
            self.parser.parse_command("invalid command format")
    
    def test_unsupported_service(self):
        """Test handling of unsupported AWS service."""
        # This should not raise an error, but return a basic parsed command
        result = self.parser.parse_command("aws unsupported-service some-action")
        assert result.service == "unsupported-service"
        assert result.action == "some-action"
    
    def test_command_without_aws_prefix(self):
        """Test parsing command without 'aws' prefix."""
        result = self.parser.parse_command("s3 ls s3://bucket")
        assert result.service == "s3"
        assert result.action == "ls"
    
    def test_complex_s3_command_with_options(self):
        """Test parsing complex S3 command with multiple options."""
        command = "aws s3 cp s3://source-bucket/file.txt s3://dest-bucket/ --recursive --exclude '*.log'"
        result = self.parser.parse_command(command)
        
        assert result.service == "s3"
        assert result.action == "cp"
        assert "--recursive" in result.parameters
        assert "--exclude" in result.parameters
        
        arns = self.parser.extract_arns(result)
        assert any("source-bucket" in arn for arn in arns)
        assert any("dest-bucket" in arn for arn in arns)
    
    def test_ec2_command_with_filters(self):
        """Test parsing EC2 command with filters."""
        command = "aws ec2 describe-instances --filters Name=instance-state-name,Values=running"
        result = self.parser.parse_command(command)
        
        assert result.service == "ec2"
        assert result.action == "describe-instances"
        assert "--filters" in result.parameters
    
    def test_iam_command_with_arn(self):
        """Test parsing IAM command with ARN parameter."""
        command = "aws iam attach-role-policy --role-name MyRole --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess"
        result = self.parser.parse_command(command)
        
        assert result.service == "iam"
        assert result.action == "attach-role-policy"
        
        arns = self.parser.extract_arns(result)
        assert any("arn:aws:iam::aws:policy/ReadOnlyAccess" in arn for arn in arns)
    
    def test_lambda_command_with_qualifier(self):
        """Test parsing Lambda command with version qualifier."""
        command = "aws lambda invoke --function-name my-function:PROD --payload '{\"key\":\"value\"}' output.json"
        result = self.parser.parse_command(command)
        
        assert result.service == "lambda"
        assert result.action == "invoke"
        assert "--function-name" in result.parameters
        assert "--payload" in result.parameters
        
        arns = self.parser.extract_arns(result)
        assert any("my-function" in arn for arn in arns)
