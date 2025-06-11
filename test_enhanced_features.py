#!/usr/bin/env python3
"""
Simple test script for the enhanced IAM features.
"""

import json
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

from iam_generator.policy_validator import IAMPolicyValidator, PolicyType
from iam_generator.enhanced_services import EnhancedIAMService


def test_policy_validation():
    """Test the policy validation functionality."""
    print("🧪 Testing Policy Validation...")
    
    # Sample policy with issues
    test_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "*",
                "Resource": "*"
            }
        ]
    }
    
    validator = IAMPolicyValidator()
    result = validator.validate_policy(test_policy, PolicyType.MANAGED)
    
    print(f"  ✓ Policy is valid: {result.is_valid}")
    print(f"  ✓ Security score: {result.score}/100")
    print(f"  ✓ Issues found: {len(result.issues)}")
    
    for issue in result.issues[:3]:  # Show first 3 issues
        print(f"    - {issue.severity.value.upper()}: {issue.message}")
    
    return result.score > 0


def test_cross_service_dependencies():
    """Test cross-service dependency analysis."""
    print("\n🔗 Testing Cross-Service Dependencies...")
    
    commands = [
        "lambda invoke --function-name my-function",
        "ecs run-task --cluster my-cluster --task-definition my-task",
        "s3 put-object --bucket my-bucket --key file.txt"
    ]
    
    service = EnhancedIAMService()
    result = service.analyze_cross_service_dependencies(commands, include_implicit=True)
    
    print(f"  ✓ Services found: {len(result['dependencies'])}")
    print(f"  ✓ Additional permissions: {len(result['additional_permissions'])}")
    
    for service_name, deps in result['dependencies'].items():
        print(f"    - {service_name}: {len(deps)} dependencies")
    
    return len(result['dependencies']) > 0


def test_conditional_policy():
    """Test conditional policy generation."""
    print("\n🔐 Testing Conditional Policy Generation...")
    
    commands = [
        "s3 put-object --bucket sensitive-bucket --key file.txt",
        "iam create-user --user-name new-user"
    ]
    
    conditions = {
        'mfa_required': True,
        'ip_restriction': ['203.0.113.0/24'],
        'secure_transport': True
    }
    
    service = EnhancedIAMService()
    result = service.generate_conditional_policy(commands, conditions)
    
    print(f"  ✓ Policy statements: {len(result['policy_document']['Statement'])}")
    print(f"  ✓ Conditions applied: {len(result['conditions_applied'])}")
    print(f"  ✓ Security enhancements: {len(result['security_enhancements'])}")
    
    for enhancement in result['security_enhancements']:
        print(f"    - {enhancement}")
    
    return len(result['conditions_applied']) > 0


def main():
    """Run all tests."""
    print("🚀 Enhanced IAM Features Test Suite")
    print("=" * 50)
    
    tests = [
        test_policy_validation,
        test_cross_service_dependencies,
        test_conditional_policy
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
                print("  ✅ PASSED")
            else:
                print("  ❌ FAILED")
        except Exception as e:
            print(f"  💥 ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
