"""
Tests for the CLI interface module.
"""

import pytest
import json
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from iam_generator.cli import cli


class TestCLI:
    """Test suite for CLI interface."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_help(self):
        """Test CLI help output."""
        result = self.runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "AWS CLI IAM Permissions Analyzer" in result.output
    
    def test_analyze_command_help(self):
        """Test analyze command help."""
        result = self.runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze an AWS CLI command" in result.output
    
    def test_generate_role_command_help(self):
        """Test generate-role command help."""
        result = self.runner.invoke(cli, ["generate-role", "--help"])
        assert result.exit_code == 0
        assert "Generate an IAM role" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_analyze_s3_command(self, mock_analyzer):
        """Test analyzing S3 command via CLI."""
        # Mock analyzer response
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "original_command": "aws s3 ls s3://bucket",
            "required_permissions": [
                {"action": "s3:ListBucket", "resource": "arn:aws:s3:::bucket"}
            ],
            "policy_document": {
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Action": ["s3:ListBucket"], "Resource": ["arn:aws:s3:::bucket"]}]
            }
        }
        
        result = self.runner.invoke(cli, ["analyze", "s3", "ls", "s3://bucket"])
        
        assert result.exit_code == 0
        mock_instance.analyze_command.assert_called_once_with("aws s3 ls s3://bucket")
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_analyze_with_json_output(self, mock_analyzer):
        """Test analyzing command with JSON output."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "original_command": "aws s3 ls s3://bucket",
            "required_permissions": [
                {"action": "s3:ListBucket", "resource": "arn:aws:s3:::bucket"}
            ]
        }
        
        result = self.runner.invoke(cli, ["analyze", "--output", "json", "s3", "ls", "s3://bucket"])
        
        assert result.exit_code == 0
        # Should contain JSON output
        assert "{" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_analyze_with_save_option(self, mock_analyzer):
        """Test analyzing command with save option."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "original_command": "aws s3 ls s3://bucket",
            "required_permissions": []
        }
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                "analyze", "--save", "output.json", "--output", "json",
                "s3", "ls", "s3://bucket"
            ])
            
            assert result.exit_code == 0
            assert "Output saved to: output.json" in result.output
            
            # Check file was created
            with open("output.json", "r") as f:
                data = json.load(f)
                assert "service" in data
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    @patch('iam_generator.cli.IAMRoleGenerator')
    def test_generate_role_command(self, mock_role_gen, mock_analyzer):
        """Test generating IAM role via CLI."""
        # Mock analyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "required_permissions": [{"action": "s3:ListBucket", "resource": "*"}]
        }
        
        # Mock role generator
        mock_role_instance = MagicMock()
        mock_role_gen.return_value = mock_role_instance
        mock_role_instance.generate_role.return_value = {
            "json": {"role_name": "TestRole"},
            "terraform": "terraform config",
            "cloudformation": "cf config",
            "aws_cli": "cli commands"
        }
        
        result = self.runner.invoke(cli, [
            "generate-role", "--role-name", "TestRole", "s3", "ls", "s3://bucket"
        ])
        
        assert result.exit_code == 0
        mock_role_instance.generate_role.assert_called_once()
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    @patch('iam_generator.cli.IAMRoleGenerator')
    def test_generate_role_with_terraform_output(self, mock_role_gen, mock_analyzer):
        """Test generating role with Terraform output format."""
        # Mock analyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "required_permissions": []
        }
        
        # Mock role generator
        mock_role_instance = MagicMock()
        mock_role_gen.return_value = mock_role_instance
        mock_role_instance.generate_role.return_value = {
            "terraform": "resource \"aws_iam_role\" \"test\" {}",
            "json": {},
            "cloudformation": "",
            "aws_cli": ""
        }
        
        result = self.runner.invoke(cli, [
            "generate-role", "--output-format", "terraform",
            "s3", "ls", "s3://bucket"
        ])
        
        assert result.exit_code == 0
        assert "resource" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    @patch('iam_generator.cli.IAMRoleGenerator')
    def test_generate_role_cross_account_without_account_id(self, mock_role_gen, mock_analyzer):
        """Test generating cross-account role without account ID."""
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        
        result = self.runner.invoke(cli, [
            "generate-role", "--trust-policy", "cross-account",
            "s3", "ls", "s3://bucket"
        ])
        
        assert result.exit_code == 1
        assert "account-id is required" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    @patch('iam_generator.cli.IAMRoleGenerator')
    def test_generate_role_with_save(self, mock_role_gen, mock_analyzer):
        """Test generating role with save option."""
        # Mock analyzer
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance
        mock_analyzer_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "required_permissions": []
        }
        
        # Mock role generator
        mock_role_instance = MagicMock()
        mock_role_gen.return_value = mock_role_instance
        mock_role_instance.generate_role.return_value = {
            "json": {"role_name": "SavedRole"},
            "terraform": "terraform config",
            "cloudformation": "cf config",
            "aws_cli": "cli commands"
        }
        
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, [
                "generate-role", "--save", "role.json",
                "s3", "ls", "s3://bucket"
            ])
            
            assert result.exit_code == 0
            assert "Role configuration saved to: role.json" in result.output
    
    def test_batch_analyze_command_help(self):
        """Test batch-analyze command help."""
        result = self.runner.invoke(cli, ["batch-analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze multiple AWS CLI commands" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_batch_analyze(self, mock_analyzer):
        """Test batch analysis of commands."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "required_permissions": []
        }
        
        with self.runner.isolated_filesystem():
            # Create commands file
            with open("commands.txt", "w") as f:
                f.write("s3 ls s3://bucket1\n")
                f.write("s3 ls s3://bucket2\n")
                f.write("# This is a comment\n")
                f.write("ec2 describe-instances\n")
            
            result = self.runner.invoke(cli, [
                "batch-analyze", "commands.txt"
            ])
            
            assert result.exit_code == 0
            assert "Analyzing 3 commands" in result.output
            assert "Batch analysis complete" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_list_services_command(self, mock_analyzer):
        """Test list-services command."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.permissions_db.get_supported_services.return_value = ["s3", "ec2", "lambda"]
        mock_instance.permissions_db.get_service_actions.return_value = ["ls", "cp", "sync"]
        
        result = self.runner.invoke(cli, ["list-services"])
        
        assert result.exit_code == 0
        assert "Supported AWS Services" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_analyze_with_verbose_flag(self, mock_analyzer):
        """Test analyze command with verbose flag."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "original_command": "aws s3 ls s3://bucket",
            "required_permissions": []
        }
        
        result = self.runner.invoke(cli, [
            "--verbose", "analyze", "s3", "ls", "s3://bucket"
        ])
        
        assert result.exit_code == 0
        assert "Analyzing command:" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_analyze_error_handling(self, mock_analyzer):
        """Test error handling in analyze command."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.side_effect = Exception("Analysis failed")
        
        result = self.runner.invoke(cli, ["analyze", "s3", "ls", "s3://bucket"])
        
        assert result.exit_code == 1
        assert "Error analyzing command" in result.output
    
    @patch('iam_generator.cli.IAMPermissionAnalyzer')
    def test_analyze_with_yaml_output(self, mock_analyzer):
        """Test analyze command with YAML output."""
        mock_instance = MagicMock()
        mock_analyzer.return_value = mock_instance
        mock_instance.analyze_command.return_value = {
            "service": "s3",
            "action": "ls",
            "required_permissions": []
        }
        
        result = self.runner.invoke(cli, [
            "analyze", "--output", "yaml", "s3", "ls", "s3://bucket"
        ])
        
        assert result.exit_code == 0
        # YAML output should contain service field
        assert "service:" in result.output
    
    def test_cli_version(self):
        """Test CLI version option."""
        result = self.runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output
    
    def test_analyze_no_arguments(self):
        """Test analyze command without arguments."""
        result = self.runner.invoke(cli, ["analyze"])
        assert result.exit_code == 2  # Click error for missing arguments
    
    def test_generate_role_no_arguments(self):
        """Test generate-role command without arguments."""
        result = self.runner.invoke(cli, ["generate-role"])
        assert result.exit_code == 2  # Click error for missing arguments
