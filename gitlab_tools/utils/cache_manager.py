"""
Project Cache System for GitLab Extractors

Optimized caching for weekly extractions with automatic expiration.
Stores project metadata and extraction results to avoid redundant API calls.
"""

import json
import pickle
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

# Cache configuration constants
CACHE_FILE_PATTERN = "*.pkl"
DEFAULT_MAX_AGE_DAYS = 7


class ProjectCache:
    """
    File-based cache system for GitLab projects and extraction results.
    
    Stores commits, pipelines, and project metadata with automatic expiration.
    Optimized for weekly extractions on large GitLab instances.
    """

    def __init__(self, cache_dir: Optional[Path] = None, max_age_days: int = 7):
        """
        Initialize project cache system.
        
        Args:
            cache_dir: Directory for cache files (default: cache/)
            max_age_days: Cache expiration in days (default: 7 for weekly)
        """
        self.cache_dir = cache_dir or Path("cache")
        self.max_age_days = max_age_days
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory structure
        self.cache_dir.mkdir(exist_ok=True)
        (self.cache_dir / "projects").mkdir(exist_ok=True)
        (self.cache_dir / "commits").mkdir(exist_ok=True)
        (self.cache_dir / "pipelines").mkdir(exist_ok=True)
        (self.cache_dir / "metadata").mkdir(exist_ok=True)
    
    def is_cache_valid(self, cache_key: str, cache_type: str = "projects") -> bool:
        """
        Check if cache entry is still valid (not expired).
        
        Args:
            cache_key: Unique identifier for cached item
            cache_type: Type of cache (projects, commits, pipelines)
            
        Returns:
            True if cache is valid and not expired
        """
        cache_file = self.cache_dir / cache_type / f"{cache_key}.pkl"
        
        if not cache_file.exists():
            return False
        
        # Check file age
        file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        is_valid = file_age < timedelta(days=self.max_age_days)
        
        if not is_valid:
            self.logger.info(f"Cache expired for {cache_key} (age: {file_age.days} days)")
        
        return is_valid
    
    def get_cached_data(self, cache_key: str, cache_type: str = "projects") -> Optional[Any]:
        """
        Retrieve cached data if valid.
        
        Args:
            cache_key: Unique identifier for cached item
            cache_type: Type of cache
            
        Returns:
            Cached data or None if not found/expired
        """
        if not self.is_cache_valid(cache_key, cache_type):
            return None
        
        cache_file = self.cache_dir / cache_type / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            self.logger.info(f"Cache hit: {cache_key}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error reading cache for {cache_key}: {e}")
            return None
    
    def save_to_cache(self, cache_key: str, data: Any, cache_type: str = "projects") -> bool:
        """
        Save data to cache with timestamp.
        
        Args:
            cache_key: Unique identifier for cached item
            data: Data to cache
            cache_type: Type of cache
            
        Returns:
            True if successfully cached
        """
        cache_file = self.cache_dir / cache_type / f"{cache_key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            self.logger.info(f"Cached data: {cache_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving cache for {cache_key}: {e}")
            return False
    
    def get_cached_project_list(self) -> Optional[List[Dict[str, Any]]]:
        """Get cached list of all projects."""
        return self.get_cached_data("project_list", "metadata")
    
    def cache_project_list(self, projects: List[Dict[str, Any]]) -> bool:
        """Cache list of all projects for future use."""
        return self.save_to_cache("project_list", projects, "metadata")
    
    def get_cached_commits(self, project_id: int) -> Optional[pd.DataFrame]:
        """Get cached commits for a specific project."""
        data = self.get_cached_data(f"project_{project_id}", "commits")
        if data is not None and isinstance(data, dict) and 'dataframe' in data:
            return pd.DataFrame(data['dataframe'])
        return None
    
    def cache_commits(self, project_id: int, commits_df: pd.DataFrame) -> bool:
        """Cache commits DataFrame for a specific project."""
        # Store as dict to preserve DataFrame structure
        cache_data = {
            'dataframe': commits_df.to_dict(),
            'rows': len(commits_df),
            'cached_at': datetime.now().isoformat()
        }
        return self.save_to_cache(f"project_{project_id}", cache_data, "commits")
    
    def get_cached_pipelines(self, project_id: int) -> Optional[pd.DataFrame]:
        """Get cached pipelines for a specific project."""
        data = self.get_cached_data(f"project_{project_id}", "pipelines")
        if data is not None and isinstance(data, dict) and 'dataframe' in data:
            return pd.DataFrame(data['dataframe'])
        return None
    
    def cache_pipelines(self, project_id: int, pipelines_df: pd.DataFrame) -> bool:
        """Cache pipelines DataFrame for a specific project."""
        cache_data = {
            'dataframe': pipelines_df.to_dict(),
            'rows': len(pipelines_df),
            'cached_at': datetime.now().isoformat()
        }
        return self.save_to_cache(f"project_{project_id}", cache_data, "pipelines")
    
    def cleanup_expired_cache(self) -> Dict[str, int]:
        """
        Remove expired cache files.
        
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {"removed": 0, "kept": 0, "errors": 0}
        
        for cache_type in ["projects", "commits", "pipelines", "metadata"]:
            cache_type_dir = self.cache_dir / cache_type
            
            if not cache_type_dir.exists():
                continue
            
            for cache_file in cache_type_dir.glob(CACHE_FILE_PATTERN):
                try:
                    file_age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
                    
                    if file_age > timedelta(days=self.max_age_days):
                        cache_file.unlink()
                        stats["removed"] += 1
                        self.logger.info(f"Removed expired cache: {cache_file.name}")
                    else:
                        stats["kept"] += 1
                        
                except Exception as e:
                    stats["errors"] += 1
                    self.logger.error(f"Error cleaning cache file {cache_file}: {e}")
        
        self.logger.info(f"Cache cleanup: {stats}")
        return stats
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get detailed cache statistics.
        
        Returns:
            Dictionary with cache statistics and health info
        """
        stats = {
            "total_files": 0,
            "total_size_mb": 0,
            "by_type": {},
            "oldest_file": None,
            "newest_file": None
        }
        
        oldest_time = datetime.now()
        newest_time = datetime.min
        
        for cache_type in ["projects", "commits", "pipelines", "metadata"]:
            type_stats = self._get_cache_type_stats(cache_type)
            oldest_time, newest_time = self._update_time_stats(
                cache_type, oldest_time, newest_time, stats
            )
            
            stats["by_type"][cache_type] = type_stats
            stats["total_files"] += type_stats["files"]
            stats["total_size_mb"] += type_stats["size_mb"]
        
        # Round for readability
        stats["total_size_mb"] = round(stats["total_size_mb"], 2)
        for cache_type in stats["by_type"]:
            stats["by_type"][cache_type]["size_mb"] = round(stats["by_type"][cache_type]["size_mb"], 2)
        
        return stats

    def _get_cache_type_stats(self, cache_type: str) -> Dict[str, int]:
        """Get statistics for specific cache type."""
        cache_type_dir = self.cache_dir / cache_type
        type_stats = {"files": 0, "size_mb": 0}
        
        if cache_type_dir.exists():
            for cache_file in cache_type_dir.glob(CACHE_FILE_PATTERN):
                try:
                    file_stat = cache_file.stat()
                    type_stats["files"] += 1
                    type_stats["size_mb"] += int(file_stat.st_size / (1024 * 1024))
                except Exception as e:
                    self.logger.error(f"Error reading cache file stats {cache_file}: {e}")
        
        return type_stats

    def _update_time_stats(self, cache_type: str, 
                          oldest_time: datetime, newest_time: datetime, 
                          stats: Dict[str, Any]) -> tuple[datetime, datetime]:
        """Update oldest/newest file timestamps."""
        cache_type_dir = self.cache_dir / cache_type
        
        if cache_type_dir.exists():
            for cache_file in cache_type_dir.glob(CACHE_FILE_PATTERN):
                try:
                    file_stat = cache_file.stat()
                    file_time = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    if file_time < oldest_time:
                        oldest_time = file_time
                        stats["oldest_file"] = cache_file.name
                    
                    if file_time > newest_time:
                        newest_time = file_time
                        stats["newest_file"] = cache_file.name
                except Exception as e:
                    self.logger.error(f"Error reading cache file stats {cache_file}: {e}")
        
        return oldest_time, newest_time


class CacheManager:
    """
    High-level cache management for GitLab extractors.
    
    Provides simple interface for caching extraction results.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None, max_age_days: int = 7):
        """Initialize cache manager."""
        self.cache = ProjectCache(cache_dir, max_age_days)
        self.logger = logging.getLogger(__name__)
    
    def get_or_extract_commits(
        self, 
        project_id: int, 
        extractor_func, 
        force_refresh: bool = False
    ) -> Optional[pd.DataFrame]:
        """
        Get commits from cache or extract fresh data.
        
        Args:
            project_id: GitLab project ID
            extractor_func: Function to extract commits if not cached
            force_refresh: Skip cache and extract fresh data
            
        Returns:
            DataFrame with commits data
        """
        if not force_refresh:
            cached_commits = self.cache.get_cached_commits(project_id)
            if cached_commits is not None:
                self.logger.info(f"Using cached commits for project {project_id}")
                return cached_commits
        
        # Extract fresh data
        self.logger.info(f"Extracting fresh commits for project {project_id}")
        commits_df = extractor_func(project_id)
        
        if commits_df is not None and not commits_df.empty:
            self.cache.cache_commits(project_id, commits_df)
        
        return commits_df
    
    def get_cache_health_report(self) -> str:
        """
        Generate a human-readable cache health report.
        
        Returns:
            Formatted cache statistics report
        """
        stats = self.cache.get_cache_statistics()
        
        report = f"""
📊 CACHE HEALTH REPORT
{'=' * 50}
Total Files: {stats['total_files']:,}
Total Size: {stats['total_size_mb']:.2f} MB
Max Age: {self.cache.max_age_days} days

By Type:
├── Projects: {stats['by_type']['projects']['files']} files ({stats['by_type']['projects']['size_mb']:.2f} MB)
├── Commits: {stats['by_type']['commits']['files']} files ({stats['by_type']['commits']['size_mb']:.2f} MB)
├── Pipelines: {stats['by_type']['pipelines']['files']} files ({stats['by_type']['pipelines']['size_mb']:.2f} MB)
└── Metadata: {stats['by_type']['metadata']['files']} files ({stats['by_type']['metadata']['size_mb']:.2f} MB)

Oldest: {stats['oldest_file']}
Newest: {stats['newest_file']}
        """
        
        return report.strip()
