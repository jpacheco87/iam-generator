#!/usr/bin/env python3

import sys
import os

# Add the src directory to the path
sys.path.insert(0, '/Users/jpacheco/Developer/iam_generator/src')

from iam_generator.doc_scraper import AWSCLIDocumentationScraper
import logging

logging.basicConfig(level=logging.INFO)

try:
    print("Creating scraper...")
    scraper = AWSCLIDocumentationScraper()
    
    print("Testing discovery of EC2 commands...")
    commands = scraper.discover_commands('ec2')
    
    print(f"Found {len(commands)} EC2 commands:")
    for i, cmd in enumerate(commands[:15]):  # Show first 15
        print(f"  {i+1}. {cmd.command}")
        
    # Look for copy-image specifically
    copy_image_found = any(cmd.command == 'copy-image' for cmd in commands)
    print(f"\ncopy-image found: {copy_image_found}")
    
    if copy_image_found:
        for cmd in commands:
            if cmd.command == 'copy-image':
                print(f"copy-image details: {cmd}")
                break
                
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
