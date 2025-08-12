"""
Exceptions Simples pour Extracteurs GitLab

Gestion d'erreurs basique mais efficace, sans complexité inutile.

Author: DevSecOps Team
Date: 2025-08-12
"""

from typing import Optional, Any


class GitLabExtractionError(Exception):
    """Erreur générale lors de l'extraction depuis GitLab."""
    
    def __init__(self, message: str, project_id: Optional[int] = None, details: Optional[Any] = None):
        self.project_id = project_id
        self.details = details
        super().__init__(message)
    
    def __str__(self):
        base_msg = super().__str__()
        if self.project_id:
            base_msg += f" [Project: {self.project_id}]"
        return base_msg


class GitLabAPIError(GitLabExtractionError):
    """Erreur spécifique à l'API GitLab."""
    pass


class CacheError(Exception):
    """Erreur liée au système de cache."""
    pass


class ValidationError(Exception):
    """Erreur de validation des données."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        self.field = field
        self.value = value
        super().__init__(message)
    
    def __str__(self):
        base_msg = super().__str__()
        if self.field:
            base_msg += f" [Field: {self.field}]"
        if self.value is not None:
            base_msg += f" [Value: {self.value}]"
        return base_msg


class BatchProcessingError(GitLabExtractionError):
    """Erreur lors du traitement par batches."""
    
    def __init__(self, message: str, batch_index: Optional[int] = None, failed_projects: Optional[list] = None):
        self.batch_index = batch_index
        self.failed_projects = failed_projects or []
        super().__init__(message)


def handle_gitlab_api_error(error: Exception, project_id: Optional[int] = None) -> GitLabExtractionError:
    """
    Convertit les erreurs API GitLab en exceptions personnalisées.
    
    Args:
        error: Exception originale
        project_id: ID du projet concerné
        
    Returns:
        Exception personnalisée appropriée
    """
    error_message = str(error)
    
    if "404" in error_message or "Not Found" in error_message:
        return GitLabAPIError(f"Projet ou ressource introuvable: {error_message}", project_id)
    elif "403" in error_message or "Forbidden" in error_message:
        return GitLabAPIError(f"Accès interdit: {error_message}", project_id)
    elif "401" in error_message or "Unauthorized" in error_message:
        return GitLabAPIError(f"Non autorisé: {error_message}", project_id)
    elif "timeout" in error_message.lower():
        return GitLabAPIError(f"Timeout API: {error_message}", project_id)
    else:
        return GitLabAPIError(f"Erreur API GitLab: {error_message}", project_id, error)
