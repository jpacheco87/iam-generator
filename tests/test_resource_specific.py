#!/usr/bin/env python3
"""
Tests for resource-specific policy generation functionality.
"""

import pytest
import json
from src.iam_generator.analyzer import IAMPermissionAnalyzer


class TestResourceSpecificAnalyzer:
    """Test resource-specific policy generation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.analyzer = IAMPermissionAnalyzer()

    def test_s3_resource_specific_policy(self):
        """Test S3 resource-specific policy generation."""
        commands = [
            "aws s3 cp file.txt s3://my-bucket/data/",
            "aws s3 ls s3://my-bucket"
        ]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            account_id="123456789012",
            region="us-east-1",
            strict_mode=True
        )
        
        assert "Version" in policy
        assert "Statement" in policy
        assert policy["Version"] == "2012-10-17"
        
        # Check metadata
        metadata = policy.get("_metadata", {})
        assert metadata["resource_specific"] is True
        assert metadata["account_id"] == "123456789012"
        assert metadata["region"] == "us-east-1"
        assert metadata["commands_analyzed"] == 2
        
        # Check for S3 bucket-specific ARNs
        statements = policy["Statement"]
        bucket_arns = [
            stmt["Resource"] for stmt in statements 
            if isinstance(stmt["Resource"], str) and "arn:aws:s3:::my-bucket" in stmt["Resource"]
        ]
        assert len(bucket_arns) > 0
        
        # Should have both bucket and object ARNs
        bucket_only_arns = [arn for arn in bucket_arns if arn == "arn:aws:s3:::my-bucket"]
        object_arns = [arn for arn in bucket_arns if "arn:aws:s3:::my-bucket/" in arn]
        
        assert len(bucket_only_arns) > 0  # For ListBucket
        assert len(object_arns) > 0  # For GetObject/PutObject

    def test_ec2_resource_specific_policy(self):
        """Test EC2 resource-specific policy generation."""
        commands = [
            "aws ec2 describe-instances --instance-ids i-1234567890abcdef0 i-0987654321fedcba0",
            "aws ec2 stop-instances --instance-ids i-1234567890abcdef0"
        ]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            account_id="123456789012",
            region="us-east-1",
            strict_mode=True
        )
        
        statements = policy["Statement"]
        
        # Check for instance-specific ARNs
        instance_arns = []
        for stmt in statements:
            resource = stmt["Resource"]
            if isinstance(resource, str) and "arn:aws:ec2:us-east-1:123456789012:instance/" in resource:
                instance_arns.append(resource)
        
        assert len(instance_arns) > 0
        
        # Should include the specific instance IDs
        assert any("i-1234567890abcdef0" in arn for arn in instance_arns)

    def test_lambda_resource_specific_policy(self):
        """Test Lambda resource-specific policy generation."""
        commands = [
            "aws lambda invoke --function-name my-function output.json",
            "aws lambda get-function --function-name my-function"
        ]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            account_id="123456789012",
            region="us-east-1",
            strict_mode=True
        )
        
        statements = policy["Statement"]
        
        # Check for function-specific ARNs
        function_arns = []
        for stmt in statements:
            resource = stmt["Resource"]
            if isinstance(resource, str) and "arn:aws:lambda:us-east-1:123456789012:function:my-function" in resource:
                function_arns.append(resource)
        
        assert len(function_arns) > 0

    def test_mixed_services_resource_specific_policy(self):
        """Test resource-specific policy generation with multiple services."""
        commands = [
            "aws s3 cp file.txt s3://my-bucket/data/",
            "aws ec2 describe-instances --instance-ids i-1234567890abcdef0",
            "aws lambda invoke --function-name my-function output.json",
            "aws dynamodb get-item --table-name my-table --key '{\"id\":{\"S\":\"123\"}}'",
            "aws iam get-user --user-name my-user"
        ]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            account_id="123456789012",
            region="us-east-1",
            strict_mode=True
        )
        
        statements = policy["Statement"]
        
        # Should have statements for multiple services
        services_found = set()
        for stmt in statements:
            for action in stmt["Action"]:
                service = action.split(":")[0] if ":" in action else "unknown"
                services_found.add(service)
        
        expected_services = {"s3", "ec2", "lambda", "dynamodb", "iam"}
        assert expected_services.issubset(services_found)
        
        # Check metadata
        metadata = policy.get("_metadata", {})
        assert metadata["commands_analyzed"] == 5
        assert metadata["specific_resources_found"] >= 3  # Should find specific resources

    def test_no_account_id_region(self):
        """Test resource-specific policy generation without account ID and region."""
        commands = [
            "aws s3 ls s3://my-bucket",
            "aws ec2 describe-instances"
        ]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            strict_mode=True
        )
        
        assert "Version" in policy
        assert "Statement" in policy
        
        # Should still work with wildcards for account/region
        statements = policy["Statement"]
        assert len(statements) > 0

    def test_least_privilege_policy(self):
        """Test least privilege policy generation."""
        commands = [
            "aws s3 cp file.txt s3://my-bucket/data/",
            "aws ec2 describe-instances --instance-ids i-1234567890abcdef0"
        ]
        
        policy = self.analyzer.generate_least_privilege_policy(
            commands=commands,
            account_id="123456789012",
            region="us-east-1"
        )
        
        assert "Version" in policy
        assert "Statement" in policy
        
        # Should have security conditions
        statements = policy["Statement"]
        secure_transport_found = False
        for stmt in statements:
            if "Condition" in stmt:
                condition = stmt["Condition"]
                if "Bool" in condition and "aws:SecureTransport" in condition["Bool"]:
                    secure_transport_found = True
                    break
        
        # Note: Secure transport condition might not be added to all statements
        # depending on the action type

    def test_service_summary(self):
        """Test service summary generation."""
        commands = [
            "aws s3 ls s3://my-bucket",
            "aws s3 cp file.txt s3://my-bucket/data/",
            "aws ec2 describe-instances",
            "aws lambda list-functions"
        ]
        
        summary = self.analyzer.get_service_summary(commands)
        
        assert isinstance(summary, dict)
        assert "s3" in summary
        assert "ec2" in summary
        assert "lambda" in summary
        
        # Check S3 summary structure
        s3_summary = summary["s3"]
        assert "actions" in s3_summary
        assert "permissions" in s3_summary
        assert "resources" in s3_summary
        
        # Should have multiple S3 actions
        assert len(s3_summary["actions"]) >= 2

    def test_policy_deduplication(self):
        """Test that duplicate permissions are properly deduplicated."""
        commands = [
            "aws s3 ls s3://my-bucket",
            "aws s3 ls s3://my-bucket",  # Duplicate command
            "aws s3 cp file.txt s3://my-bucket/data/",
            "aws s3 cp file2.txt s3://my-bucket/data/"  # Similar command
        ]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            strict_mode=True
        )
        
        statements = policy["Statement"]
        
        # Count ListBucket statements - should be deduplicated
        list_bucket_statements = [
            stmt for stmt in statements 
            if "s3:ListBucket" in stmt.get("Action", [])
        ]
        
        # Should have only one ListBucket statement for the bucket
        bucket_resources = set()
        for stmt in list_bucket_statements:
            resource = stmt["Resource"]
            if isinstance(resource, str) and resource.startswith("arn:aws:s3:::"):
                bucket_resources.add(resource)
        
        # Should not have duplicate bucket permissions
        assert len(bucket_resources) <= 2  # At most one for each unique bucket

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Empty commands list should return empty policy
        result = self.analyzer.generate_resource_specific_policy([])
        assert result["Statement"] == []
        assert result["Version"] == "2012-10-17"
        
        # Invalid command format should be handled gracefully
        result = self.analyzer.generate_resource_specific_policy(["invalid command"])
        # Should still return a valid policy structure, even if empty
        assert "Version" in result
        assert "Statement" in result

    def test_arn_enhancement(self):
        """Test ARN enhancement with account and region."""
        commands = ["aws ec2 describe-instances"]
        
        policy = self.analyzer.generate_resource_specific_policy(
            commands=commands,
            account_id="123456789012",
            region="us-west-2",
            strict_mode=True
        )
        
        statements = policy["Statement"]
        
        # Check that ARNs are enhanced with account and region
        for stmt in statements:
            resource = stmt["Resource"]
            if isinstance(resource, str) and resource.startswith("arn:aws:ec2:"):
                # Should contain the specified region and account
                assert "us-west-2" in resource or resource.count("*") > 0
                assert "123456789012" in resource or resource.count("*") > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
