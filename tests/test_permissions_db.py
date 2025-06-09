"""
Tests for the IAM permissions database module.
"""

import pytest
from iam_generator.permissions_db import IAMPermissionsDatabase


class TestIAMPermissionsDatabase:
    """Test suite for IAMPermissionsDatabase class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.permissions_db = IAMPermissionsDatabase()
    
    def test_get_s3_permissions(self):
        """Test getting S3 permissions for ls action."""
        permissions = self.permissions_db.get_permissions("s3", "ls")
        
        assert len(permissions) > 0
        assert any(perm["action"] == "s3:ListBucket" for perm in permissions)
    
    def test_get_ec2_permissions(self):
        """Test getting EC2 permissions for describe-instances action."""
        permissions = self.permissions_db.get_permissions("ec2", "describe-instances")
        
        assert len(permissions) > 0
        assert any(perm["action"] == "ec2:DescribeInstances" for perm in permissions)
    
    def test_get_lambda_permissions(self):
        """Test getting Lambda permissions for invoke action."""
        permissions = self.permissions_db.get_permissions("lambda", "invoke")
        
        assert len(permissions) > 0
        assert any(perm["action"] == "lambda:InvokeFunction" for perm in permissions)
    
    def test_get_iam_permissions(self):
        """Test getting IAM permissions for list-users action."""
        permissions = self.permissions_db.get_permissions("iam", "list-users")
        
        assert len(permissions) > 0
        assert any(perm["action"] == "iam:ListUsers" for perm in permissions)
    
    def test_get_permissions_for_unsupported_service(self):
        """Test getting permissions for unsupported service."""
        permissions = self.permissions_db.get_permissions("unsupported", "action")
        
        # Should return empty list for unsupported service
        assert permissions == []
    
    def test_get_permissions_for_unsupported_action(self):
        """Test getting permissions for unsupported action in supported service."""
        permissions = self.permissions_db.get_permissions("s3", "unsupported-action")
        
        # Should return empty list for unsupported action
        assert permissions == []
    
    def test_get_supported_services(self):
        """Test getting list of supported services."""
        services = self.permissions_db.get_supported_services()
        
        assert "s3" in services
        assert "ec2" in services
        assert "lambda" in services
        assert "iam" in services
        assert "logs" in services
        assert "sts" in services
    
    def test_get_service_actions(self):
        """Test getting actions for a specific service."""
        s3_actions = self.permissions_db.get_service_actions("s3")
        
        assert "ls" in s3_actions
        assert "cp" in s3_actions
        assert "sync" in s3_actions
        assert "rm" in s3_actions
        assert "mb" in s3_actions
        assert "rb" in s3_actions
    
    def test_s3_cp_permissions(self):
        """Test S3 cp command permissions."""
        permissions = self.permissions_db.get_permissions("s3", "cp")
        
        # Should include both read and write permissions
        actions = [perm["action"] for perm in permissions]
        assert "s3:GetObject" in actions
        assert "s3:PutObject" in actions
        assert "s3:ListBucket" in actions
    
    def test_s3_sync_permissions(self):
        """Test S3 sync command permissions."""
        permissions = self.permissions_db.get_permissions("s3", "sync")
        
        # Should include comprehensive permissions for sync
        actions = [perm["action"] for perm in permissions]
        assert "s3:GetObject" in actions
        assert "s3:PutObject" in actions
        assert "s3:DeleteObject" in actions
        assert "s3:ListBucket" in actions
    
    def test_ec2_run_instances_permissions(self):
        """Test EC2 run-instances command permissions."""
        permissions = self.permissions_db.get_permissions("ec2", "run-instances")
        
        actions = [perm["action"] for perm in permissions]
        assert "ec2:RunInstances" in actions
        assert "ec2:DescribeImages" in actions
        assert "ec2:DescribeInstanceTypes" in actions
    
    def test_lambda_create_function_permissions(self):
        """Test Lambda create-function command permissions."""
        permissions = self.permissions_db.get_permissions("lambda", "create-function")
        
        actions = [perm["action"] for perm in permissions]
        assert "lambda:CreateFunction" in actions
        assert "iam:PassRole" in actions
    
    def test_iam_create_role_permissions(self):
        """Test IAM create-role command permissions."""
        permissions = self.permissions_db.get_permissions("iam", "create-role")
        
        actions = [perm["action"] for perm in permissions]
        assert "iam:CreateRole" in actions
    
    def test_logs_permissions(self):
        """Test CloudWatch Logs permissions."""
        permissions = self.permissions_db.get_permissions("logs", "describe-log-groups")
        
        actions = [perm["action"] for perm in permissions]
        assert "logs:DescribeLogGroups" in actions
    
    def test_sts_permissions(self):
        """Test STS permissions."""
        permissions = self.permissions_db.get_permissions("sts", "get-caller-identity")
        
        actions = [perm["action"] for perm in permissions]
        assert "sts:GetCallerIdentity" in actions
    
    def test_permission_structure(self):
        """Test that permissions have the correct structure."""
        permissions = self.permissions_db.get_permissions("s3", "ls")
        
        for perm in permissions:
            assert "action" in perm
            assert "resource" in perm
            # Optional fields
            if "condition" in perm and perm["condition"] is not None:
                assert isinstance(perm["condition"], dict)
            if "description" in perm:
                assert isinstance(perm["description"], str)
    
    def test_resource_patterns(self):
        """Test that resource patterns are correctly defined."""
        permissions = self.permissions_db.get_permissions("s3", "ls")
        
        # Should have different resource patterns for different actions
        resources = [perm["resource"] for perm in permissions]
        assert len(resources) > 0
        
        # S3 ListBucket should have bucket ARN pattern
        list_bucket_perms = [perm for perm in permissions if perm["action"] == "s3:ListBucket"]
        if list_bucket_perms:
            assert "arn:aws:s3:::" in list_bucket_perms[0]["resource"]
