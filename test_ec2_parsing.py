#!/usr/bin/env python3

import subprocess
import re

def test_ec2_parsing():
    print("Testing EC2 command parsing...")
    
    try:
        # Get AWS CLI help for EC2
        result = subprocess.run(['aws', 'ec2', 'help'], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"AWS CLI failed: {result.stderr}")
            return
            
        print(f"Got {len(result.stdout)} characters of output")
        
        # Clean up formatting
        cleaned = re.sub(r'.\x08', '', result.stdout)
        lines = cleaned.split('\n')
        
        print(f"Split into {len(lines)} lines")
        
        # Find commands section
        commands = []
        in_commands_section = False
        
        for i, line in enumerate(lines):
            if "AVAILABLE COMMANDS" in line:
                in_commands_section = True
                print(f"Found commands section at line {i}")
                continue
                
            if in_commands_section:
                if line.strip() == "":
                    continue
                if line.startswith("SEE ALSO") or line.startswith("EXAMPLES"):
                    print(f"End of commands section at line {i}")
                    break
                    
                match = re.match(r'\s+o\s+([a-z0-9-]+)(?:\s+(.+))?', line)
                if match:
                    command_name = match.group(1)
                    if command_name not in ['help', 'wait']:
                        commands.append(command_name)
                        
                        # Show first few and look for copy-image
                        if len(commands) <= 10 or command_name == 'copy-image':
                            print(f"  Found: {command_name}")
                            
        print(f"\nTotal commands found: {len(commands)}")
        
        # Look for copy-image
        if 'copy-image' in commands:
            print("✓ copy-image found!")
        else:
            print("✗ copy-image not found")
            # Show some commands around where it might be
            print("Sample commands found:")
            for cmd in commands[50:70]:  # Show middle section
                print(f"  {cmd}")
                
    except subprocess.TimeoutExpired:
        print("AWS CLI command timed out")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ec2_parsing()
