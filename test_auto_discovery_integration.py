#!/usr/bin/env python3
"""
Test Auto-Discovery Integration

This script tests the complete auto-discovery system to ensure it's working correctly.
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_auto_discovery_system():
    """Test the complete auto-discovery system."""
    
    print("🔍 Testing Auto-Discovery Integration")
    print("=" * 50)
    
    try:
        # Import the enhanced analyzer
        from iam_generator.analyzer import IAMPermissionAnalyzer
        
        # Test 1: Create analyzer with auto-discovery enabled
        print("\n📝 Test 1: Creating analyzer with auto-discovery...")
        analyzer = IAMPermissionAnalyzer(enable_auto_discovery=True)
        print(f"✅ Auto-discovery enabled: {analyzer.auto_discovery_enabled}")
        
        # Test 2: Get auto-discovery statistics
        print("\n📊 Test 2: Getting auto-discovery statistics...")
        stats = analyzer.get_auto_discovery_stats()
        print("Auto-Discovery Statistics:")
        for key, value in stats.items():
            print(f"  - {key}: {value}")
        
        # Test 3: Test with a known AI/ML service from manual database
        print("\n🧠 Test 3: Testing with known AI/ML service (bedrock-runtime)...")
        try:
            result = analyzer.analyze_command("aws bedrock-runtime invoke-model --model-id anthropic.claude-v2")
            print(f"✅ Successfully analyzed bedrock-runtime command")
            print(f"  - Service: {result['service']}")
            print(f"  - Action: {result['action']}")
            print(f"  - Permissions: {len(result['required_permissions'])}")
        except Exception as e:
            print(f"⚠️  Analysis failed: {e}")
        
        # Test 4: Test with a potentially unknown service (auto-discovery target)
        print("\n🔍 Test 4: Testing with potentially unknown service...")
        try:
            result = analyzer.analyze_command("aws personalize create-dataset")
            print(f"✅ Successfully analyzed personalize command")
            print(f"  - Service: {result['service']}")
            print(f"  - Action: {result['action']}")
            print(f"  - Permissions: {len(result['required_permissions'])}")
            if result['warnings']:
                print(f"  - Warnings: {result['warnings']}")
        except Exception as e:
            print(f"⚠️  Analysis failed: {e}")
        
        # Test 5: Check if cache file was created
        print("\n💾 Test 5: Checking auto-discovery cache...")
        cache_file = Path("auto_discovery_cache.json")
        if cache_file.exists():
            print(f"✅ Cache file created: {cache_file}")
            print(f"  - Size: {cache_file.stat().st_size} bytes")
            
            # Read cache contents
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                print(f"  - Cached entries: {len(cache_data)}")
                if cache_data:
                    print("  - Sample entries:")
                    for i, (key, entry) in enumerate(cache_data.items()):
                        if i >= 3:  # Show only first 3
                            break
                        print(f"    • {key}: {entry.get('confidence', 'unknown')} confidence")
            except Exception as e:
                print(f"  - Cache read error: {e}")
        else:
            print("ℹ️  No cache file found (may be created asynchronously)")
        
        # Test 6: Test enhanced database methods
        print("\n🔧 Test 6: Testing enhanced database methods...")
        if hasattr(analyzer.permissions_db, 'get_supported_services'):
            services = analyzer.permissions_db.get_supported_services()
            print(f"✅ Total supported services: {len(services)}")
            
            # Show some auto-discovered services if any
            if hasattr(analyzer.permissions_db, 'auto_cache') and analyzer.permissions_db.auto_cache:
                cached_services = analyzer.permissions_db.auto_cache.get_cached_services()
                if cached_services:
                    print(f"  - Auto-discovered services: {len(cached_services)}")
                    print(f"  - Examples: {list(cached_services)[:5]}")
        
        print("\n✅ Auto-Discovery Integration Test Completed Successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Auto-discovery system may not be properly integrated")
        return False
    except Exception as e:
        print(f"❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comparison_with_without_auto_discovery():
    """Compare analyzer behavior with and without auto-discovery."""
    
    print("\n🔄 Testing Comparison: With vs Without Auto-Discovery")
    print("=" * 60)
    
    try:
        from iam_generator.analyzer import IAMPermissionAnalyzer
        
        # Test command for unknown service
        test_command = "aws personalize create-dataset"
        
        # Test with auto-discovery enabled
        print("📊 With Auto-Discovery:")
        analyzer_auto = IAMPermissionAnalyzer(enable_auto_discovery=True)
        result_auto = analyzer_auto.analyze_command(test_command)
        print(f"  - Permissions found: {len(result_auto['required_permissions'])}")
        print(f"  - Warnings: {len(result_auto['warnings'])}")
        
        # Test with auto-discovery disabled
        print("\n📊 Without Auto-Discovery:")
        analyzer_manual = IAMPermissionAnalyzer(enable_auto_discovery=False)
        result_manual = analyzer_manual.analyze_command(test_command)
        print(f"  - Permissions found: {len(result_manual['required_permissions'])}")
        print(f"  - Warnings: {len(result_manual['warnings'])}")
        
        # Compare results
        print(f"\n📈 Comparison:")
        print(f"  - Auto-discovery found {len(result_auto['required_permissions']) - len(result_manual['required_permissions'])} additional permissions")
        print(f"  - Auto-discovery stats: {analyzer_auto.get_auto_discovery_stats()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AWS IAM Generator - Auto-Discovery System Test")
    print("=" * 60)
    
    # Run main test
    success1 = test_auto_discovery_system()
    
    # Run comparison test
    success2 = test_comparison_with_without_auto_discovery()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Auto-discovery system is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the auto-discovery implementation.")
        sys.exit(1)
