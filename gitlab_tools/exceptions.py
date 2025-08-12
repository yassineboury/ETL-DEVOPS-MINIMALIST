"""
Exceptions Simples pour Extracteurs GitLab

Gestion d'erreurs basique mais efficace, sans complexité inutile.

Author: DevSecOps Team
Date: 2025-08-12
"""

from typing import Optional, Any, Union
import gitlab


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


class ValidationError(GitLabExtractionError):
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


def handle_gitlab_api_error(error: Union[Exception, Any]) -> GitLabExtractionError:
    """
    Convertit les erreurs API GitLab en exceptions personnalisées.
    
    Args:
        error: Exception ou mock avec response_code et error_message
        
    Returns:
        Exception personnalisée appropriée
        
    Raises:
        GitLabExtractionError: Exception appropriée selon le code d'erreur
    """
    # Gestion des erreurs mockées dans les tests
    if hasattr(error, 'response_code') and hasattr(error, 'error_message'):
        exception = _handle_mock_error(error)
        raise exception from error
    
    # Gestion des erreurs réelles
    exception = _handle_real_error(error)
    raise exception from error


def _handle_mock_error(error: Any) -> GitLabExtractionError:
    """Gestion des erreurs mockées avec codes HTTP."""
    code = error.response_code
    message = error.error_message
    
    error_map = {
        401: f"Authentication failed: {message}",
        403: f"Access denied: {message}",
        404: f"Resource not found: {message}",
        500: f"Server error: {message}"
    }
    
    error_text = error_map.get(code, f"GitLab API error [{code}]: {message}")
    return GitLabExtractionError(error_text)


def _handle_real_error(error: Exception) -> GitLabExtractionError:
    """Gestion des erreurs réelles de l'API GitLab."""
    error_message = str(error)
    
    error_patterns = [
        (["404", "Not Found"], "Projet ou ressource introuvable"),
        (["403", "Forbidden"], "Accès interdit"),
        (["401", "Unauthorized"], "Non autorisé"),
        (["timeout"], "Timeout API")
    ]
    
    for patterns, prefix in error_patterns:
        if any(pattern in error_message for pattern in patterns):
            return GitLabAPIError(f"{prefix}: {error_message}")
    
    return GitLabAPIError(f"Erreur API GitLab: {error_message}")
