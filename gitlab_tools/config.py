"""
Configuration Centralisée Simple

Configuration basique pour les extracteurs GitLab locaux.
Simple, efficace, sans sur-ingénierie.

Author: DevSecOps Team
Date: 2025-08-12
"""

from pathlib import Path
from typing import Dict, Any

# Configuration GitLab API
DEFAULT_GITLAB_TIMEOUT = 30
DEFAULT_PER_PAGE = 100
MAX_RETRIES = 3

# Configuration Batch Processing
DEFAULT_BATCH_SIZE = 10  # Optimal pour GitLab API
MIN_BATCH_SIZE = 5
MAX_BATCH_SIZE = 20

# Configuration Cache
DEFAULT_CACHE_DAYS = 7  # Parfait pour extractions hebdomadaires
DEFAULT_CACHE_DIR = Path.home() / ".gitlab_cache"

# Configuration Extraction
DEFAULT_MAX_COMMITS = 1000
DEFAULT_MAX_PIPELINES = 500

# Types de fichiers pour analyse
FILE_TYPES = {
    'code': {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.swift'},
    'config': {'.yml', '.yaml', '.json', '.xml', '.toml', '.ini', '.conf', '.cfg', '.env'},
    'docs': {'.md', '.rst', '.txt', '.doc', '.docx', '.pdf', '.adoc'},
    'tests': {'test_', '_test', '.test.', 'spec_', '_spec', '.spec.'}
}

# Seuils pour analyse des commits
CHANGE_MAGNITUDE_THRESHOLDS = {
    'Small': 50,
    'Medium': 200, 
    'Large': 500
}

def get_default_config() -> Dict[str, Any]:
    """Retourne la configuration par défaut."""
    return {
        'gitlab': {
            'timeout': DEFAULT_GITLAB_TIMEOUT,
            'per_page': DEFAULT_PER_PAGE,
            'max_retries': MAX_RETRIES
        },
        'batch': {
            'size': DEFAULT_BATCH_SIZE,
            'min_size': MIN_BATCH_SIZE,
            'max_size': MAX_BATCH_SIZE
        },
        'cache': {
            'days': DEFAULT_CACHE_DAYS,
            'dir': DEFAULT_CACHE_DIR
        },
        'extraction': {
            'max_commits': DEFAULT_MAX_COMMITS,
            'max_pipelines': DEFAULT_MAX_PIPELINES
        },
        'analysis': {
            'file_types': FILE_TYPES,
            'change_thresholds': CHANGE_MAGNITUDE_THRESHOLDS
        }
    }

def validate_batch_size(batch_size: int) -> int:
    """Valide et ajuste la taille des batches."""
    if batch_size < MIN_BATCH_SIZE:
        return MIN_BATCH_SIZE
    elif batch_size > MAX_BATCH_SIZE:
        return MAX_BATCH_SIZE
    return batch_size

def validate_cache_days(days: int) -> int:
    """Valide les jours de cache."""
    return max(1, min(days, 30))  # Entre 1 et 30 jours
