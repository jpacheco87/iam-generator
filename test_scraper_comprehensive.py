#!/usr/bin/env python3

import sys
import os

# Add the src directory to the path
sys.path.insert(0, '/Users/jpacheco/Developer/iam_generator/src')

from iam_generator.doc_scraper import AWSCLIDocumentationScraper
import logging

logging.basicConfig(level=logging.INFO)

def test_basic_functionality():
    """Test basic scraper functionality."""
    print("=" * 60)
    print("TESTING: Basic Doc Scraper Functionality")
    print("=" * 60)
    
    try:
        print("✓ Creating scraper...")
        scraper = AWSCLIDocumentationScraper()
        
        print("✓ Testing help command output...")
        # Test if we can get help output
        help_output = scraper.get_help_output('s3')
        if help_output and 'AVAILABLE COMMANDS' in help_output:
            print("✓ Successfully retrieved AWS CLI help output")
        else:
            print("✗ Failed to get valid help output")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error in basic functionality: {e}")
        return False

def test_service_discovery():
    """Test service discovery functionality."""
    print("\n" + "=" * 60)
    print("TESTING: Service Discovery")
    print("=" * 60)
    
    try:
        scraper = AWSCLIDocumentationScraper()
        
        print("Discovering AWS services...")
        services = scraper.discover_services()
        
        print(f"✓ Found {len(services)} total AWS services")
        
        # Show some examples
        common_services = ['s3', 'ec2', 'lambda', 'iam', 'rds', 'dynamodb']
        found_common = [svc for svc in common_services if svc in services]
        
        print(f"✓ Found {len(found_common)}/{len(common_services)} common services:")
        for svc in found_common:
            print(f"  • {svc}")
            
        # Show first 20 services
        print(f"\nFirst 20 discovered services:")
        for i, service in enumerate(sorted(services)[:20]):
            print(f"  {i+1:2d}. {service}")
            
        return len(services) > 100  # Should find many services
        
    except Exception as e:
        print(f"✗ Error in service discovery: {e}")
        return False

def test_command_discovery():
    """Test command discovery for specific services."""
    print("\n" + "=" * 60)
    print("TESTING: Command Discovery")
    print("=" * 60)
    
    try:
        scraper = AWSCLIDocumentationScraper()
        
        # Test with a few key services
        test_services = ['s3', 'ec2', 'lambda']
        
        for service in test_services:
            print(f"\nDiscovering commands for {service}...")
            commands = scraper.discover_commands(service)
            
            print(f"✓ Found {len(commands)} commands for {service}")
            
            # Show first few commands
            if commands:
                print(f"  First 5 commands:")
                for i, cmd in enumerate(commands[:5]):
                    print(f"    {i+1}. {cmd.command} - {cmd.description[:50]}...")
            
        return True
        
    except Exception as e:
        print(f"✗ Error in command discovery: {e}")
        return False

def test_permission_mapping():
    """Test permission mapping functionality."""
    print("\n" + "=" * 60)
    print("TESTING: Permission Mapping")
    print("=" * 60)
    
    try:
        scraper = AWSCLIDocumentationScraper()
        
        # Test some common command mappings
        test_cases = [
            ('s3', 'cp'),
            ('ec2', 'describe-instances'),
            ('lambda', 'invoke'),
            ('iam', 'list-users'),
            ('dynamodb', 'put-item')
        ]
        
        for service, command in test_cases:
            print(f"\nMapping {service} {command}...")
            permissions = scraper.map_command_to_permissions(service, command)
            
            print(f"  ✓ Service: {permissions.service}")
            print(f"  ✓ Action: {permissions.action}")
            print(f"  ✓ Permissions:")
            for perm in permissions.permissions:
                print(f"    • {perm.action}")
            print(f"  ✓ Confidence: {scraper._determine_confidence(service, command)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Error in permission mapping: {e}")
        return False

def test_database_generation():
    """Test full database generation."""
    print("\n" + "=" * 60)
    print("TESTING: Database Generation")
    print("=" * 60)
    
    try:
        scraper = AWSCLIDocumentationScraper()
        
        # Test with a small subset to avoid long execution time
        test_services = ['s3', 'ec2', 'lambda']
        
        print(f"Generating database for {test_services}...")
        database = scraper.generate_permissions_database(test_services)
        
        total_commands = sum(len(commands) for commands in database.values())
        print(f"✓ Generated database with {len(database)} services and {total_commands} commands")
        
        # Show summary
        for service, commands in database.items():
            print(f"  • {service}: {len(commands)} commands")
            
        return len(database) == len(test_services) and total_commands > 50
        
    except Exception as e:
        print(f"✗ Error in database generation: {e}")
        return False

def test_integration_points():
    """Test how the scraper integrates with the main application."""
    print("\n" + "=" * 60)
    print("TESTING: Integration Points")
    print("=" * 60)
    
    try:
        # Test if we can import the existing permissions database
        from iam_generator.permissions_db import IAMPermissionsDatabase
        existing_db = IAMPermissionsDatabase()
        
        print(f"✓ Existing database has {len(existing_db._permissions_map)} services")
        
        # Test comparison functionality
        scraper = AWSCLIDocumentationScraper()
        
        # Get a small sample to compare
        existing_services = list(existing_db._permissions_map.keys())[:5]
        print(f"Testing comparison with existing services: {existing_services}")
        
        comparison = scraper.compare_with_existing(existing_db._permissions_map, existing_services)
        
        print(f"✓ Comparison results:")
        print(f"  • Missing services: {len(comparison.get('missing_services', []))}")
        print(f"  • Missing commands: {len(comparison.get('missing_commands', []))}")
        print(f"  • New services: {len(comparison.get('new_services', []))}")
        print(f"  • New commands: {len(comparison.get('new_commands', []))}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing integration: {e}")
        return False

def main():
    """Run comprehensive tests."""
    print("AWS CLI Documentation Scraper - Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Service Discovery", test_service_discovery),
        ("Command Discovery", test_command_discovery),
        ("Permission Mapping", test_permission_mapping),
        ("Database Generation", test_database_generation),
        ("Integration Points", test_integration_points),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The doc_scraper is working correctly.")
    elif passed > len(tests) // 2:
        print("⚠️  Most tests passed. The doc_scraper is largely functional.")
    else:
        print("❌ Many tests failed. The doc_scraper may have issues.")

if __name__ == "__main__":
    main()
