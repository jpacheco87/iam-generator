#!/usr/bin/env python3
"""
Test role generation fix for all output formats.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_role_generation_format(output_format: str, trust_policy: str = "ec2"):
    """Test role generation for a specific output format."""
    print(f"Testing {output_format.upper()} format...")
    
    payload = {
        "command": "s3 list-buckets",
        "role_name": f"test-{output_format}-role",
        "trust_policy": trust_policy,
        "output_format": output_format,
        "description": f"Test role for {output_format} format"
    }
    
    response = requests.post(f"{BASE_URL}/generate-role", json=payload)
    
    if response.status_code != 200:
        print(f"❌ {output_format.upper()} format failed: {response.text}")
        return False
    
    result = response.json()
    
    # Check basic fields
    assert result['role_name'] == f"test-{output_format}-role"
    assert 'trust_policy' in result
    assert 'permissions_policy' in result
    
    # Check format-specific fields
    if output_format == "terraform":
        assert 'terraform_config' in result and result['terraform_config'] is not None
        assert 'resource "aws_iam_role"' in result['terraform_config']
        assert 'resource "aws_iam_policy"' in result['terraform_config']
        print(f"✅ {output_format.upper()} format working - Contains Terraform resources")
        
    elif output_format == "cloudformation":
        assert 'cloudformation_config' in result and result['cloudformation_config'] is not None
        cf_config = json.loads(result['cloudformation_config'])
        assert 'AWSTemplateFormatVersion' in cf_config
        assert 'Resources' in cf_config
        print(f"✅ {output_format.upper()} format working - Contains CloudFormation template")
        
    elif output_format == "aws_cli":
        assert 'aws_cli_commands' in result and result['aws_cli_commands'] is not None
        assert len(result['aws_cli_commands']) > 0
        commands_text = ' '.join(result['aws_cli_commands'])
        assert 'aws iam create-role' in commands_text
        assert 'aws iam create-policy' in commands_text
        print(f"✅ {output_format.upper()} format working - Contains AWS CLI commands")
        
    else:  # JSON format
        print(f"✅ {output_format.upper()} format working - Standard JSON response")
    
    return True

def test_different_trust_policies():
    """Test different trust policy types."""
    print("\nTesting different trust policy types...")
    
    trust_policies = ["ec2", "lambda", "ecs", "default"]
    
    for trust_policy in trust_policies:
        payload = {
            "command": "dynamodb list-tables",
            "role_name": f"test-{trust_policy}-trust",
            "trust_policy": trust_policy,
            "output_format": "json"
        }
        
        response = requests.post(f"{BASE_URL}/generate-role", json=payload)
        
        if response.status_code != 200:
            print(f"❌ Trust policy {trust_policy} failed: {response.text}")
            return False
        
        result = response.json()
        trust_doc = result['trust_policy']
        
        if trust_policy == "ec2":
            assert "ec2.amazonaws.com" in str(trust_doc)
        elif trust_policy == "lambda":
            assert "lambda.amazonaws.com" in str(trust_doc)
        elif trust_policy == "ecs":
            assert "ecs-tasks.amazonaws.com" in str(trust_doc)
        
        print(f"✅ Trust policy {trust_policy} working correctly")
    
    return True

def main():
    """Run all role generation tests."""
    print("🚀 Testing Role Generation Fix")
    print("=" * 50)
    
    try:
        # Test all output formats
        formats = ["json", "terraform", "cloudformation", "aws_cli"]
        
        for format_type in formats:
            if not test_role_generation_format(format_type):
                sys.exit(1)
        
        # Test different trust policies
        if not test_different_trust_policies():
            sys.exit(1)
        
        print("\n" + "=" * 50)
        print("🎉 All role generation tests passed!")
        print("✅ Terraform format working")
        print("✅ CloudFormation format working") 
        print("✅ AWS CLI format working")
        print("✅ JSON format working")
        print("✅ All trust policy types working")
        print("\nThe role generation issue has been successfully fixed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
