"""
Utilitaires de validation pour GitLab Client
Sépare la logique de validation pour réduire la complexité cognitive
"""
import os
from typing import Optional
from urllib.parse import urlparse


class GitLabValidator:
    """Validateur pour les paramètres GitLab"""
    
    @staticmethod
    def determine_url(config: Optional[dict], url: Optional[str]) -> str:
        """
        Détermine l'URL GitLab à utiliser
        
        Args:
            config: Configuration chargée
            url: URL fournie explicitement
            
        Returns:
            URL GitLab valide
            
        Raises:
            ValueError: Si aucune URL n'est trouvée
        """
        gitlab_url = url or (config.get('gitlab', {}).get('url') if config else None)
        if not gitlab_url:
            raise ValueError("URL GitLab manquante dans la configuration")
        return gitlab_url

    @staticmethod
    def determine_token(config: Optional[dict], token: Optional[str]) -> str:
        """
        Détermine le token GitLab à utiliser
        
        Args:
            config: Configuration chargée
            token: Token fourni explicitement
            
        Returns:
            Token GitLab valide
            
        Raises:
            ValueError: Si aucun token valide n'est trouvé
        """
        gitlab_token = (token or
                      os.getenv('GITLAB_TOKEN') or
                      (config.get('gitlab', {}).get('token') if config else None))

        if not gitlab_token or gitlab_token.startswith('${'):
            raise ValueError(
                "Token GitLab manquant. Vérifiez votre fichier .env ou la configuration"
            )
        return gitlab_token

    @staticmethod
    def is_internal_domain(gitlab_url: str) -> bool:
        """
        Vérifie si l'URL correspond à un domaine interne
        
        Args:
            gitlab_url: URL à vérifier
            
        Returns:
            True si le domaine est interne
        """
        try:
            parsed_url = urlparse(gitlab_url)
            hostname = parsed_url.hostname
            
            # Liste blanche des domaines autorisés pour SSL désactivé
            internal_domains = [
                "oncf.net",
                "localhost"
            ]
            
            return any(hostname and hostname.endswith(domain) 
                      for domain in internal_domains)
        except Exception:
            return False

    @staticmethod
    def validate_url_format(gitlab_url: str) -> bool:
        """
        Valide le format de l'URL GitLab
        
        Args:
            gitlab_url: URL à valider
            
        Returns:
            True si l'URL est valide
        """
        try:
            parsed = urlparse(gitlab_url)
            return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
        except Exception:
            return False
