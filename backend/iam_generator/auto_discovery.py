"""
Auto-Discovery Cache System

This module implements an automatic discovery and caching system that extends
the IAM permissions database with dynamically discovered AWS services and commands.
"""

import json
import logging
from typing import Dict, List, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import time

from .permissions_db import IAMPermission, CommandPermissions, IAMPermissionsDatabase
from .doc_scraper import AWSCLIDocumentationScraper

logger = logging.getLogger(__name__)

@dataclass
class CachedPermission:
    """Cached permission entry with metadata."""
    service: str
    command: str
    permissions: List[Dict]  # Serializable IAMPermission data
    confidence: str
    description: str
    resource_patterns: List[str]
    discovered_at: str  # ISO timestamp
    last_accessed: str  # ISO timestamp
    access_count: int = 0

class AutoDiscoveryCache:
    """Persistent cache for auto-discovered permissions."""
    
    def __init__(self, cache_file: str = "auto_discovery_cache.json"):
        """Initialize the auto-discovery cache."""
        self.cache_file = Path(cache_file)
        self.cache: Dict[str, CachedPermission] = {}
        self.cache_lock = threading.Lock()
        self._load_cache()
        
    def _load_cache(self):
        """Load cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    
                # Convert to CachedPermission objects
                for key, item in data.items():
                    self.cache[key] = CachedPermission(**item)
                    
                logger.info(f"Loaded {len(self.cache)} cached permissions from {self.cache_file}")
            else:
                logger.info("No existing cache file found, starting with empty cache")
                
        except Exception as e:
            logger.warning(f"Failed to load cache from {self.cache_file}: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with self.cache_lock:
                # Convert to serializable format
                data = {}
                for key, cached_perm in self.cache.items():
                    data[key] = asdict(cached_perm)
                
                # Atomic write
                temp_file = self.cache_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                temp_file.replace(self.cache_file)
                logger.debug(f"Saved {len(self.cache)} cached permissions to {self.cache_file}")
                
        except Exception as e:
            logger.error(f"Failed to save cache to {self.cache_file}: {e}")
    
    def get_cache_key(self, service: str, command: str) -> str:
        """Generate cache key for service and command."""
        return f"{service}:{command}"
    
    def get_cached_permissions(self, service: str, command: str) -> Optional[CommandPermissions]:
        """Get cached permissions for a service command."""
        cache_key = self.get_cache_key(service, command)
        
        with self.cache_lock:
            if cache_key in self.cache:
                cached = self.cache[cache_key]
                
                # Update access statistics
                cached.last_accessed = datetime.now().isoformat()
                cached.access_count += 1
                
                # Convert back to CommandPermissions
                permissions = []
                for perm_data in cached.permissions:
                    permissions.append(IAMPermission(
                        action=perm_data['action'],
                        resource=perm_data['resource'],
                        condition=perm_data.get('condition'),
                        effect=perm_data.get('effect', 'Allow')
                    ))
                
                return CommandPermissions(
                    service=cached.service,
                    action=cached.command,
                    permissions=permissions,
                    description=cached.description,
                    resource_patterns=cached.resource_patterns
                )
        
        return None
    
    def cache_permissions(self, service: str, command: str, 
                         permissions: CommandPermissions, confidence: str):
        """Cache discovered permissions."""
        cache_key = self.get_cache_key(service, command)
        
        # Convert permissions to serializable format
        perm_data = []
        for perm in permissions.permissions:
            perm_data.append({
                'action': perm.action,
                'resource': perm.resource,
                'condition': perm.condition,
                'effect': perm.effect
            })
        
        cached_perm = CachedPermission(
            service=service,
            command=command,
            permissions=perm_data,
            confidence=confidence,
            description=permissions.description,
            resource_patterns=permissions.resource_patterns,
            discovered_at=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            access_count=1
        )
        
        with self.cache_lock:
            self.cache[cache_key] = cached_perm
            
        # Save to disk asynchronously
        threading.Thread(target=self._save_cache, daemon=True).start()
        
        logger.info(f"Cached permissions for {service} {command} (confidence: {confidence})")
    
    def is_cached(self, service: str, command: str) -> bool:
        """Check if service command is cached."""
        cache_key = self.get_cache_key(service, command)
        return cache_key in self.cache
    
    def get_cached_services(self) -> Set[str]:
        """Get set of all cached services."""
        return {cached.service for cached in self.cache.values()}
    
    def get_cached_commands(self, service: str) -> List[str]:
        """Get list of cached commands for a service."""
        return [cached.command for cached in self.cache.values() 
                if cached.service == service]
    
    def cleanup_old_entries(self, max_age_days: int = 30):
        """Remove old unused cache entries."""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        cutoff_str = cutoff.isoformat()
        
        with self.cache_lock:
            old_keys = []
            for key, cached in self.cache.items():
                if (cached.access_count <= 1 and 
                    cached.last_accessed < cutoff_str):
                    old_keys.append(key)
            
            for key in old_keys:
                del self.cache[key]
        
        if old_keys:
            logger.info(f"Cleaned up {len(old_keys)} old cache entries")
            self._save_cache()
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        with self.cache_lock:
            services = set()
            total_commands = len(self.cache)
            high_confidence = 0
            
            for cached in self.cache.values():
                services.add(cached.service)
                if cached.confidence == 'high':
                    high_confidence += 1
            
            return {
                'total_cached_services': len(services),
                'total_cached_commands': total_commands,
                'high_confidence_commands': high_confidence,
                'cache_file_size': self.cache_file.stat().st_size if self.cache_file.exists() else 0
            }

class EnhancedPermissionsDatabase(IAMPermissionsDatabase):
    """Enhanced permissions database with auto-discovery capabilities."""
    
    def __init__(self, enable_auto_discovery: bool = True, 
                 cache_file: str = "auto_discovery_cache.json"):
        """Initialize enhanced database with auto-discovery."""
        super().__init__()
        
        self.enable_auto_discovery = enable_auto_discovery
        
        if enable_auto_discovery:
            self.auto_cache = AutoDiscoveryCache(cache_file)
            self.scraper = AWSCLIDocumentationScraper()
            logger.info("Auto-discovery enabled")
        else:
            self.auto_cache = None
            self.scraper = None
            logger.info("Auto-discovery disabled")
    
    def get_permissions_object(self, service: str, action: str) -> Optional[CommandPermissions]:
        """Get permissions with auto-discovery fallback."""
        # First, check manual database
        manual_perms = super().get_permissions_object(service, action)
        if manual_perms:
            return manual_perms
        
        # If auto-discovery is disabled, return None
        if not self.enable_auto_discovery or not self.auto_cache:
            return None
        
        # Check auto-discovery cache
        cached_perms = self.auto_cache.get_cached_permissions(service, action)
        if cached_perms:
            logger.debug(f"Using cached permissions for {service} {action}")
            return cached_perms
        
        # Try to discover using scraper
        discovered_perms = self._discover_permissions(service, action)
        if discovered_perms:
            # Cache the discovery for future use
            confidence = self.scraper._determine_confidence(service, action)
            
            # Only cache high and medium confidence discoveries
            if confidence in ['high', 'medium']:
                self.auto_cache.cache_permissions(service, action, discovered_perms, confidence)
                logger.info(f"Auto-discovered and cached {service} {action} (confidence: {confidence})")
            else:
                logger.debug(f"Discovered {service} {action} but not caching (low confidence)")
            
            return discovered_perms
        
        return None
    
    def _discover_permissions(self, service: str, action: str) -> Optional[CommandPermissions]:
        """Discover permissions using scraper."""
        if not self.scraper:
            return None
        
        try:
            # Check if service exists
            known_services = self.scraper.discover_services()
            if service not in known_services:
                logger.debug(f"Service {service} not found by scraper")
                return None
            
            # Check if command exists for this service
            commands = self.scraper.discover_commands(service)
            command_names = [cmd.command for cmd in commands]
            
            if action not in command_names:
                logger.debug(f"Command {action} not found in service {service}")
                return None
            
            # Map command to permissions
            permissions = self.scraper.map_command_to_permissions(service, action)
            logger.debug(f"Discovered permissions for {service} {action}: {[p.action for p in permissions.permissions]}")
            
            return permissions
            
        except Exception as e:
            logger.warning(f"Failed to discover permissions for {service} {action}: {e}")
            return None
    
    def get_supported_services(self) -> List[str]:
        """Get list of supported services including auto-discovered ones."""
        manual_services = super().get_supported_services()
        
        if self.enable_auto_discovery and self.auto_cache:
            cached_services = self.auto_cache.get_cached_services()
            all_services = set(manual_services) | cached_services
            return sorted(list(all_services))
        
        return manual_services
    
    def preload_high_priority_services(self, services: List[str], max_commands_per_service: int = 5):
        """Preload high-priority services into the cache."""
        if not self.enable_auto_discovery:
            logger.warning("Auto-discovery disabled, cannot preload services")
            return
        
        logger.info(f"Preloading {len(services)} high-priority services...")
        
        for service in services:
            try:
                commands = self.scraper.discover_commands(service)
                
                # Focus on high-confidence commands
                high_conf_commands = [c for c in commands if c.confidence == 'high'][:max_commands_per_service]
                
                for cmd in high_conf_commands:
                    if not self.auto_cache.is_cached(service, cmd.command):
                        self._discover_permissions(service, cmd.command)
                        
                logger.info(f"Preloaded {len(high_conf_commands)} commands for {service}")
                        
            except Exception as e:
                logger.warning(f"Failed to preload service {service}: {e}")
    
    def get_auto_discovery_stats(self) -> Dict:
        """Get auto-discovery statistics."""
        if not self.enable_auto_discovery or not self.auto_cache:
            return {'auto_discovery_enabled': False}
        
        stats = self.auto_cache.get_stats()
        stats['auto_discovery_enabled'] = True
        stats['manual_services'] = len(super().get_supported_services())
        
        return stats

def background_preloader(database: EnhancedPermissionsDatabase, 
                        high_priority_services: List[str]):
    """Background thread function to preload high-priority services."""
    logger.info("Starting background preloader for high-priority services")
    
    try:
        database.preload_high_priority_services(high_priority_services)
        logger.info("Background preloader completed successfully")
    except Exception as e:
        logger.error(f"Background preloader failed: {e}")

# High-priority services that are commonly requested
HIGH_PRIORITY_SERVICES = [
    "bedrock-runtime", "bedrock", "textract", "rekognition", "comprehend",
    "polly", "transcribe", "translate", "personalize", "forecast",
    "lex", "connect", "workspaces", "workdocs", "workmail",
    "memorydb", "neptune", "documentdb", "timestream-query", "timestream-write",
    "amplify", "pinpoint", "mobile", "device-farm", "cost-optimization-hub",
    "application-cost-profiler", "ce", "cur", "pricing"
]

def create_enhanced_database(enable_auto_discovery: bool = True,
                           enable_background_preload: bool = True,
                           cache_file: str = "auto_discovery_cache.json") -> EnhancedPermissionsDatabase:
    """Create an enhanced permissions database with optional background preloading."""
    
    database = EnhancedPermissionsDatabase(
        enable_auto_discovery=enable_auto_discovery,
        cache_file=cache_file
    )
    
    if enable_auto_discovery and enable_background_preload:
        # Start background preloader
        preloader_thread = threading.Thread(
            target=background_preloader,
            args=(database, HIGH_PRIORITY_SERVICES),
            daemon=True
        )
        preloader_thread.start()
        logger.info("Started background preloader thread")
    
    return database
