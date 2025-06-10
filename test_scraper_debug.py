#!/usr/bin/env python3

import subprocess
import re

# Test AWS CLI output parsing
print("Testing AWS CLI help parsing...")

result = subprocess.run(['aws', 'ec2', 'help'], capture_output=True, text=True, timeout=30)
print(f"Return code: {result.returncode}")
print(f"Output length: {len(result.stdout)}")

# Show raw sample
print("\nRaw output sample:")
print(repr(result.stdout[300:500]))

# Test cleaning
cleaned = re.sub(r'.\x08', '', result.stdout)
print(f"\nCleaned output length: {len(cleaned)}")
print("Cleaned sample:")
print(repr(cleaned[300:500]))

# Check for section header
print("\nLooking for AVAILABLE COMMANDS in cleaned output:")
if 'AVAILABLE COMMANDS' in cleaned:
    print("✓ Found 'AVAILABLE COMMANDS'")
    idx = cleaned.index('AVAILABLE COMMANDS')
    print(f"Found at position: {idx}")
    
    # Show context around it
    context_start = max(0, idx - 50)
    context_end = min(len(cleaned), idx + 200)
    print("Context:")
    print(repr(cleaned[context_start:context_end]))
    
    # Look for commands after this point
    lines_after_header = cleaned[idx:].split('\n')
    print(f"\nLines after header ({len(lines_after_header)}):")
    for i, line in enumerate(lines_after_header[:20]):
        print(f"  {i}: {repr(line)}")
        
        # Test regex match
        match = re.match(r'\s+o\s+([a-z0-9-]+)(?:\s+(.+))?', line)
        if match:
            print(f"    -> COMMAND FOUND: {match.group(1)}")
            
else:
    print("✗ 'AVAILABLE COMMANDS' not found")
    
    # Try variations
    variations = ['available commands', 'Available Commands', 'COMMANDS']
    for var in variations:
        if var in cleaned:
            print(f"✓ Found variation: '{var}'")
        else:
            print(f"✗ Not found: '{var}'")
