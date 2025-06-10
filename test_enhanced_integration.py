#!/usr/bin/env python3
"""
Test the enhanced scraper integration in the analyzer.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, '/Users/jpacheco/Developer/iam_generator/src')

from iam_generator.analyzer import IAMPermissionAnalyzer
import json

def test_enhanced_integration():
    """Test the enhanced analyzer with scraper integration."""
    print("=" * 80)
    print("TESTING: Enhanced Analyzer with Scraper Integration")
    print("=" * 80)
    
    analyzer = IAMPermissionAnalyzer()
    
    print("\n1. Testing known command in existing database:")
    try:
        result = analyzer.analyze_commands(["aws s3 ls s3://my-bucket"])
        print(f"✓ S3 command analysis: {len(result.required_permissions)} permissions")
        print(f"  Services: {result.services_used}")
        print(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")
    except Exception as e:
        print(f"✗ Error with known command: {e}")
    
    print("\n2. Testing unknown command in known service:")
    try:
        result = analyzer.analyze_commands(["aws s3 unknown-command"])
        print(f"✓ Unknown S3 command analysis: {len(result.required_permissions)} permissions")
        print(f"  Services: {result.services_used}")
        print(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")
    except Exception as e:
        print(f"✗ Error with unknown command in known service: {e}")
    
    print("\n3. Testing unknown service (bedrock-runtime):")
    try:
        result = analyzer.analyze_commands(["aws bedrock-runtime invoke-model"])
        print(f"✓ Bedrock command analysis: {len(result.required_permissions)} permissions")
        print(f"  Services: {result.services_used}")
        print(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")
        if result.required_permissions:
            print(f"  Permissions found:")
            for perm in result.required_permissions:
                print(f"    - {perm.action}")
    except Exception as e:
        print(f"✗ Error with unknown service: {e}")
    
    print("\n4. Testing completely unknown service:")
    try:
        result = analyzer.analyze_commands(["aws fake-service fake-command"])
        print(f"✓ Fake service analysis: {len(result.required_permissions)} permissions")
        print(f"  Services: {result.services_used}")
        print(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")
    except Exception as e:
        print(f"✗ Error with fake service: {e}")
    
    print("\n5. Testing mixed commands:")
    try:
        result = analyzer.analyze_commands([
            "aws s3 ls s3://bucket",  # Known
            "aws bedrock-runtime invoke-model",  # Unknown service  
            "aws ec2 describe-instances"  # Known
        ])
        print(f"✓ Mixed commands analysis: {len(result.required_permissions)} permissions")
        print(f"  Services: {result.services_used}")
        print(f"  Missing commands: {result.missing_commands}")
        print(f"  Warnings: {len(result.warnings)}")
        if result.warnings:
            for warning in result.warnings:
                print(f"    - {warning}")
        
        # Show policy
        print(f"\n  Generated policy:")
        print(json.dumps(result.policy_document, indent=2))
        
    except Exception as e:
        print(f"✗ Error with mixed commands: {e}")

if __name__ == "__main__":
    test_enhanced_integration()
