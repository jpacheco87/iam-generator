#!/usr/bin/env python3
"""
Test the updated role generator UI functionality.
This test verifies that all formats are generated in one API call.
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_all_formats_endpoint():
    """Test the new all-formats endpoint."""
    print("Testing All-Formats Role Generation...")
    
    payload = {
        "command": "s3 get-object --bucket my-bucket --key my-file",
        "role_name": "test-ui-all-formats",
        "trust_policy": "lambda",
        "description": "Test role for UI all formats functionality"
    }
    
    response = requests.post(f"{BASE_URL}/generate-role-all-formats", json=payload)
    
    if response.status_code != 200:
        print(f"❌ All-formats endpoint failed: {response.text}")
        return False
    
    result = response.json()
    
    # Verify all required fields are present
    required_fields = ['role_name', 'trust_policy', 'permissions_policy']
    for field in required_fields:
        if field not in result:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Verify all format-specific fields are populated
    format_fields = {
        'terraform_config': 'Terraform configuration',
        'cloudformation_config': 'CloudFormation template',
        'aws_cli_commands': 'AWS CLI commands'
    }
    
    for field, description in format_fields.items():
        if field not in result or result[field] is None:
            print(f"❌ Missing {description}: {field}")
            return False
        
        if field == 'aws_cli_commands':
            if not isinstance(result[field], list) or len(result[field]) == 0:
                print(f"❌ {description} should be a non-empty list")
                return False
        else:
            if not isinstance(result[field], str) or len(result[field]) == 0:
                print(f"❌ {description} should be a non-empty string")
                return False
    
    # Verify content quality
    terraform_config = result['terraform_config']
    if 'resource "aws_iam_role"' not in terraform_config:
        print("❌ Terraform config missing IAM role resource")
        return False
    
    cloudformation_config = json.loads(result['cloudformation_config'])
    if 'AWSTemplateFormatVersion' not in cloudformation_config:
        print("❌ CloudFormation config missing template version")
        return False
    
    aws_cli_commands = result['aws_cli_commands']
    command_text = ' '.join(aws_cli_commands)
    if 'aws iam create-role' not in command_text:
        print("❌ AWS CLI commands missing role creation")
        return False
    
    print("✅ All-formats endpoint working correctly")
    print(f"   - Role name: {result['role_name']}")
    print(f"   - Trust policy: Lambda service")
    print(f"   - Terraform config: {len(terraform_config)} characters")
    print(f"   - CloudFormation config: {len(result['cloudformation_config'])} characters")
    print(f"   - AWS CLI commands: {len(aws_cli_commands)} commands")
    
    return True

def test_different_services():
    """Test the endpoint with different AWS services."""
    print("\nTesting different AWS services...")
    
    test_cases = [
        {
            "command": "dynamodb create-table --table-name MyTable",
            "service": "DynamoDB",
            "trust_policy": "ec2"
        },
        {
            "command": "lambda invoke --function-name my-function",
            "service": "Lambda",
            "trust_policy": "ecs"
        },
        {
            "command": "ec2 describe-instances",
            "service": "EC2",
            "trust_policy": "lambda"
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"  Testing {test_case['service']}...")
        
        payload = {
            "command": test_case["command"],
            "role_name": f"test-{test_case['service'].lower()}-{i}",
            "trust_policy": test_case["trust_policy"]
        }
        
        response = requests.post(f"{BASE_URL}/generate-role-all-formats", json=payload)
        
        if response.status_code != 200:
            print(f"❌ {test_case['service']} test failed: {response.text}")
            return False
        
        result = response.json()
        
        # Verify all formats are present
        if not all(key in result and result[key] for key in ['terraform_config', 'cloudformation_config', 'aws_cli_commands']):
            print(f"❌ {test_case['service']} missing some format outputs")
            return False
        
        print(f"✅ {test_case['service']} test passed")
    
    return True

def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\nTesting error handling...")
    
    # Test missing required fields
    invalid_requests = [
        {"role_name": "test"},  # Missing command
        {"command": "s3 list-buckets"},  # Missing role_name
        {"command": "", "role_name": "test"},  # Empty command
        {"command": "invalid-service invalid-action", "role_name": "test"}  # Invalid command
    ]
    
    for i, invalid_request in enumerate(invalid_requests):
        response = requests.post(f"{BASE_URL}/generate-role-all-formats", json=invalid_request)
        
        if response.status_code == 200:
            print(f"❌ Error test {i+1} should have failed but didn't")
            return False
    
    print("✅ Error handling working correctly")
    return True

def main():
    """Run all tests for the updated role generator."""
    print("🚀 Testing Updated Role Generator UI")
    print("=" * 60)
    
    try:
        # Test the main functionality
        if not test_all_formats_endpoint():
            sys.exit(1)
        
        # Test with different services
        if not test_different_services():
            sys.exit(1)
        
        # Test error handling
        if not test_error_handling():
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("✅ All-formats endpoint working correctly")
        print("✅ Multiple AWS services supported")
        print("✅ Error handling working properly")
        print("✅ All output formats generated simultaneously")
        print("\nThe UI update has been successfully implemented!")
        print("Users can now generate all formats without selecting an output format!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
