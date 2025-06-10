#!/usr/bin/env python3
"""
Database Updater

This script uses the documentation scraper to discover new AWS services and commands,
then systematically updates the permissions database with high-confidence mappings.
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from iam_generator.doc_scraper import AWSCLIDocumentationScraper
from iam_generator.permissions_db import IAMPermissionsDatabase, CommandPermissions, IAMPermission

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseUpdate:
    """Represents a potential database update."""
    service: str
    command: str
    permissions: List[str]
    confidence: str
    existing: bool = False

class DatabaseUpdater:
    """Updates the permissions database using scraper discoveries."""
    
    def __init__(self):
        self.scraper = AWSCLIDocumentationScraper()
        self.db = IAMPermissionsDatabase()
        self.updates: List[DatabaseUpdate] = []
        
    def get_current_services(self) -> Set[str]:
        """Get list of services currently in the manual database."""
        return set(self.db._permissions_map.keys())
    
    def discover_new_services(self) -> List[str]:
        """Discover services not yet in the manual database."""
        current_services = self.get_current_services()
        all_services = self.scraper.discover_services()
        
        new_services = [s for s in all_services if s not in current_services]
        logger.info(f"Found {len(new_services)} new services not in database")
        
        return new_services
    
    def analyze_service_commands(self, service: str, max_commands: int = 10) -> List[DatabaseUpdate]:
        """Analyze commands for a service and generate database updates."""
        updates = []
        
        logger.info(f"Analyzing service: {service}")
        commands = self.scraper.discover_commands(service)
        
        # Focus on high-confidence commands first
        high_confidence_commands = [c for c in commands if c.confidence == 'high'][:max_commands]
        
        for cmd_info in high_confidence_commands:
            try:
                # Use scraper to get permissions for this command
                permissions = self.scraper.map_command_to_permissions(service, cmd_info.command)
                
                if permissions:
                    update = DatabaseUpdate(
                        service=service,
                        command=cmd_info.command,
                        permissions=permissions,
                        confidence=cmd_info.confidence,
                        existing=self._command_exists(service, cmd_info.command)
                    )
                    updates.append(update)
                    logger.info(f"  ✅ {service} {cmd_info.command}: {permissions}")
                else:
                    logger.warning(f"  ❌ {service} {cmd_info.command}: No permissions found")
                    
            except Exception as e:
                logger.error(f"  ❌ {service} {cmd_info.command}: {e}")
        
        return updates
    
    def _command_exists(self, service: str, command: str) -> bool:
        """Check if a command already exists in the database."""
        return (service in self.db._permissions_map and 
                command in self.db._permissions_map[service])
    
    def generate_database_entries(self, updates: List[DatabaseUpdate]) -> Dict[str, Dict]:
        """Generate database entries from updates."""
        entries = {}
        
        for update in updates:
            if update.service not in entries:
                entries[update.service] = {}
            
            # Convert permissions to IAMPermission objects
            iam_permissions = []
            for perm in update.permissions:
                iam_permissions.append(IAMPermission(action=perm, resource="*"))
            
            # Create CommandPermissions entry
            entries[update.service][update.command] = {
                "service": update.service,
                "action": update.command,
                "permissions": [{"action": p, "resource": "*"} for p in update.permissions],
                "description": f"Auto-generated from documentation scraper ({update.confidence} confidence)",
                "resource_patterns": ["*"]
            }
        
        return entries
    
    def save_updates_to_file(self, updates: List[DatabaseUpdate], filename: str):
        """Save updates to a JSON file for review."""
        entries = self.generate_database_entries(updates)
        
        with open(filename, 'w') as f:
            json.dump(entries, f, indent=2)
        
        logger.info(f"Saved {len(updates)} updates to {filename}")
    
    def update_high_priority_services(self) -> List[DatabaseUpdate]:
        """Update database with high-priority services that are commonly used."""
        
        # Priority services that are commonly used but not in our manual database
        priority_services = [
            "bedrock", "bedrock-runtime", "textract", "rekognition", "comprehend",
            "polly", "transcribe", "translate", "personalize", "forecast",
            "lex", "connect", "workspaces", "workdocs", "workmail",
            "memorydb", "neptune", "documentdb", "timestream-query", "timestream-write",
            "amplify", "appsync", "pinpoint", "mobile", "device-farm"
        ]
        
        all_updates = []
        
        for service in priority_services:
            try:
                updates = self.analyze_service_commands(service, max_commands=5)
                all_updates.extend(updates)
            except Exception as e:
                logger.error(f"Failed to analyze {service}: {e}")
        
        return all_updates
    
    def generate_summary_report(self, updates: List[DatabaseUpdate]) -> str:
        """Generate a summary report of potential updates."""
        
        new_services = set()
        new_commands = 0
        existing_updates = 0
        
        by_service = {}
        
        for update in updates:
            if update.service not in by_service:
                by_service[update.service] = []
                new_services.add(update.service)
            
            by_service[update.service].append(update)
            
            if update.existing:
                existing_updates += 1
            else:
                new_commands += 1
        
        report = []
        report.append("🔍 DATABASE UPDATE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"📊 Summary:")
        report.append(f"  • New services discovered: {len(new_services)}")
        report.append(f"  • New commands to add: {new_commands}")
        report.append(f"  • Existing commands with updates: {existing_updates}")
        report.append(f"  • Total updates: {len(updates)}")
        report.append("")
        
        report.append("📋 By Service:")
        for service, service_updates in by_service.items():
            report.append(f"  🔧 {service}:")
            for update in service_updates:
                status = "🆕" if not update.existing else "🔄"
                confidence = {"high": "🟢", "medium": "🟡", "low": "🟠"}.get(update.confidence, "⚪")
                report.append(f"    {status} {confidence} {update.command}: {', '.join(update.permissions)}")
        
        return "\n".join(report)

def main():
    """Main function to run database updates."""
    updater = DatabaseUpdater()
    
    print("🚀 Starting database update process...")
    print(f"📊 Current database has {len(updater.get_current_services())} services")
    
    # Discover new services
    new_services = updater.discover_new_services()
    print(f"🔍 Found {len(new_services)} new services: {', '.join(new_services[:10])}{'...' if len(new_services) > 10 else ''}")
    
    # Update high-priority services
    print("\n🎯 Analyzing high-priority services...")
    updates = updater.update_high_priority_services()
    
    # Generate and save report
    report = updater.generate_summary_report(updates)
    print(f"\n{report}")
    
    # Save updates to files
    if updates:
        updater.save_updates_to_file(updates, "database_updates.json")
        
        # Also save just the new services for easier integration
        new_service_updates = [u for u in updates if not u.existing]
        if new_service_updates:
            updater.save_updates_to_file(new_service_updates, "new_services_only.json")
            print(f"💾 Saved {len(new_service_updates)} new service updates to new_services_only.json")
    
    print("\n✅ Database update analysis complete!")
    print("\n📝 Next steps:")
    print("  1. Review database_updates.json")
    print("  2. Test selected services manually")
    print("  3. Integrate approved updates into permissions_db.py")

if __name__ == "__main__":
    main()
