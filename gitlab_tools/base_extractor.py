"""
Interface BaseExtractor Simple

Classe de base commune pour tous les extracteurs GitLab.
Simple, pratique, sans sur-ingénierie.

Author: DevSecOps Team
Date: 2025-08-12
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import pandas as pd
import gitlab

from .config import get_default_config, validate_batch_size, validate_cache_days
from .exceptions import GitLabExtractionError, handle_gitlab_api_error
from .utils.batch_processor import GitLabBatchProcessor
from .utils.cache_manager import CacheManager


class BaseExtractor(ABC):
    """
    Classe de base pour tous les extracteurs GitLab.
    
    Fournit les fonctionnalités communes:
    - Configuration standardisée
    - Gestion des erreurs
    - Cache et batch processing
    - Logging unifié
    - Métriques basiques
    """
    
    def __init__(
        self, 
        gitlab_client: gitlab.Gitlab, 
        batch_size: int = 10,
        enable_cache: bool = True,
        cache_days: int = 7
    ):
        """
        Initialise l'extracteur avec configuration commune.
        
        Args:
            gitlab_client: Client GitLab API
            batch_size: Taille des batches (optimal: 10)
            enable_cache: Active le cache (recommandé)
            cache_days: Durée de cache en jours (optimal: 7)
        """
        self.gitlab = gitlab_client
        self.config = get_default_config()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration batch processing
        self.batch_size = validate_batch_size(batch_size)
        self.batch_processor = GitLabBatchProcessor(self.batch_size)
        
        # Configuration cache
        self.enable_cache = enable_cache
        self.cache_days = validate_cache_days(cache_days)
        if enable_cache:
            self.cache_manager = CacheManager(max_age_days=self.cache_days)
            self.logger.info(f"Cache activé: {self.cache_days} jours")
        else:
            self.cache_manager = None
            
        # Statistiques d'extraction
        self._stats = {
            'start_time': None,
            'end_time': None,
            'total_projects': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'cached_results': 0,
            'fresh_extractions': 0
        }
        
        self.logger.info(f"Extracteur initialisé: batch_size={self.batch_size}, cache={enable_cache}")
    
    @abstractmethod
    def extract(self, **kwargs) -> pd.DataFrame:
        """
        Méthode principale d'extraction (à implémenter par chaque extracteur).
        
        Args:
            **kwargs: Arguments spécifiques à chaque type d'extracteur
            
        Returns:
            DataFrame avec les données extraites
        """
        pass
    
    def _start_extraction(self):
        """Démarre le suivi des statistiques d'extraction."""
        self._stats['start_time'] = datetime.now()
        self._stats['successful_extractions'] = 0
        self._stats['failed_extractions'] = 0
        self._stats['cached_results'] = 0
        self._stats['fresh_extractions'] = 0
        
    def _end_extraction(self):
        """Finalise le suivi des statistiques d'extraction."""
        self._stats['end_time'] = datetime.now()
        
    def _record_success(self, from_cache: bool = False):
        """Enregistre une extraction réussie."""
        self._stats['successful_extractions'] += 1
        if from_cache:
            self._stats['cached_results'] += 1
        else:
            self._stats['fresh_extractions'] += 1
            
    def _record_failure(self):
        """Enregistre un échec d'extraction."""
        self._stats['failed_extractions'] += 1
        
    def get_extraction_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'extraction.
        
        Returns:
            Dictionnaire avec les métriques
        """
        stats = self._stats.copy()
        
        if stats['start_time'] and stats['end_time']:
            duration = stats['end_time'] - stats['start_time']
            stats['duration_seconds'] = duration.total_seconds()
            
            if stats['successful_extractions'] > 0:
                stats['avg_time_per_project'] = stats['duration_seconds'] / stats['successful_extractions']
                stats['cache_hit_rate'] = stats['cached_results'] / stats['successful_extractions']
        
        return stats
        
    def _get_accessible_projects(self, project_ids: Optional[List[int]] = None) -> List[Any]:
        """Récupère la liste des projets accessibles."""
        try:
            if project_ids:
                projects = []
                for project_id in project_ids:
                    try:
                        project = self.gitlab.projects.get(project_id, lazy=False)
                        projects.append(project)
                    except Exception as e:
                        error = handle_gitlab_api_error(e)
                        self.logger.warning(f"Projet {project_id} non accessible: {error}")
                return projects
            else:
                return self.gitlab.projects.list(
                    owned=True, 
                    membership=True, 
                    per_page=self.config['gitlab']['per_page']
                )
        except Exception as e:
            raise handle_gitlab_api_error(e) from e
    
    def _create_empty_dataframe(self) -> pd.DataFrame:
        """Crée un DataFrame vide avec les colonnes de base."""
        return pd.DataFrame({
            'project_id': [],
            'project_name': [],
            'extracted_at': []
        })
        
    def print_stats(self):
        """Affiche les statistiques d'extraction de manière lisible."""
        stats = self.get_extraction_stats()
        
        print(f"\n📊 Statistiques {self.__class__.__name__}")
        print("=" * 50)
        print(f"🎯 Projets traités: {stats['successful_extractions']}/{stats['total_projects']}")
        
        if stats['failed_extractions'] > 0:
            print(f"❌ Échecs: {stats['failed_extractions']}")
            
        if 'duration_seconds' in stats:
            print(f"⏱️ Durée: {stats['duration_seconds']:.1f}s")
            
        if 'avg_time_per_project' in stats:
            print(f"⚡ Moyenne: {stats['avg_time_per_project']:.2f}s/projet")
            
        if 'cache_hit_rate' in stats:
            cache_rate = stats['cache_hit_rate'] * 100
            print(f"💾 Cache hit rate: {cache_rate:.1f}%")
            print(f"🗄️ Résultats cachés: {stats['cached_results']}")
            print(f"🆕 Extractions fraîches: {stats['fresh_extractions']}")
            
    def cleanup_cache(self):
        """Nettoie le cache expiré."""
        if self.cache_manager:
            stats = self.cache_manager.cache.cleanup_expired_cache()
            self.logger.info(f"Nettoyage cache: {stats}")
            return stats
        return None
