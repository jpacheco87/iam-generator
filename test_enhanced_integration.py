#!/usr/bin/env python3
"""
Integration test for enhanced IAM features.
Tests all the new enhanced endpoints to ensure they work correctly.
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_policy_validation():
    """Test policy validation endpoint."""
    print("Testing Policy Validation...")
    
    payload = {
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "*",
                    "Resource": "*"
                }
            ]
        },
        "policy_type": "managed"
    }
    
    response = requests.post(f"{BASE_URL}/enhanced/validate-policy", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert result['is_valid'] == False
    assert result['score'] < 100
    assert len(result['issues']) > 0
    print("✅ Policy validation working correctly")

def test_cross_service_dependencies():
    """Test cross-service dependency analysis."""
    print("Testing Cross-Service Dependencies...")
    
    payload = {
        "commands": ["lambda invoke --function-name test-function"],
        "include_implicit": True
    }
    
    response = requests.post(f"{BASE_URL}/enhanced/cross-service-dependencies", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert 'dependencies' in result
    assert 'additional_permissions' in result
    assert 'enhanced_policy' in result
    print("✅ Cross-service dependencies working correctly")

def test_conditional_policy():
    """Test conditional policy generation."""
    print("Testing Conditional Policy Generation...")
    
    payload = {
        "commands": ["s3 list-buckets"],
        "conditions": {
            "require_mfa": True,
            "ip_restrictions": ["203.0.113.0/24"],
            "time_restrictions": {
                "start_time": "09:00",
                "end_time": "17:00",
                "timezone": "UTC"
            }
        }
    }
    
    response = requests.post(f"{BASE_URL}/enhanced/conditional-policy", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert 'policy_document' in result
    assert 'conditions_applied' in result
    assert len(result['conditions_applied']) > 0
    print("✅ Conditional policy generation working correctly")

def test_compliance_check():
    """Test compliance checking."""
    print("Testing Compliance Check...")
    
    payload = {
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject"],
                    "Resource": "arn:aws:s3:::my-bucket/*",
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "true"
                        },
                        "Bool": {
                            "aws:MultiFactorAuthPresent": "true"
                        }
                    }
                }
            ]
        }
    }
    
    response = requests.post(f"{BASE_URL}/enhanced/compliance-check/soc2", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert 'framework' in result
    assert 'score' in result
    assert 'passed_checks' in result
    assert 'failed_checks' in result
    print("✅ Compliance check working correctly")

def test_security_recommendations():
    """Test security recommendations."""
    print("Testing Security Recommendations...")
    
    response = requests.get(f"{BASE_URL}/enhanced/security-recommendations/s3")
    assert response.status_code == 200
    
    result = response.json()
    assert 'service' in result
    assert 'best_practices' in result
    assert 'conditions' in result
    print("✅ Security recommendations working correctly")

def test_policy_templates():
    """Test policy templates."""
    print("Testing Policy Templates...")
    
    response = requests.get(f"{BASE_URL}/enhanced/policy-templates/lambda-basic")
    assert response.status_code == 200
    
    result = response.json()
    assert 'use_case' in result
    assert 'template' in result
    assert 'description' in result
    print("✅ Policy templates working correctly")

def test_policy_optimization():
    """Test policy optimization."""
    print("Testing Policy Optimization...")
    
    payload = {
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:GetObjectVersion"],
                    "Resource": "arn:aws:s3:::my-bucket/*"
                },
                {
                    "Effect": "Allow",
                    "Action": ["s3:ListBucket"],
                    "Resource": "arn:aws:s3:::my-bucket"
                }
            ]
        },
        "optimization_level": "standard"
    }
    
    response = requests.post(f"{BASE_URL}/enhanced/optimize-policy", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    assert 'original_policy' in result
    assert 'optimized_policy' in result
    assert 'validation_result' in result
    print("✅ Policy optimization working correctly")

def main():
    """Run all integration tests."""
    print("🚀 Starting Enhanced Features Integration Tests")
    print("=" * 60)
    
    try:
        test_policy_validation()
        test_cross_service_dependencies()
        test_conditional_policy()
        test_compliance_check()
        test_security_recommendations()
        test_policy_templates()
        test_policy_optimization()
        
        print("=" * 60)
        print("🎉 All enhanced features tests passed!")
        print("The enhanced IAM features are working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
